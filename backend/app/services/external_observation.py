"""ExternalObservationService — C6.3 controlled external observation pipeline.

Fetch -> Artifact -> extract candidate facts -> LearningLoopService.
External content NEVER becomes fact directly; it only creates Candidate Changes.
"""
import hashlib, json, re, uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import os as _os, yaml

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import ObservationSource, ObservationRun, ObservationArtifact
from app.services.observation_network import validate_url, validate_host_ip, validate_redirect_url, resolve_all_and_validate
from urllib.parse import urlparse

print("Phase C6.3: ExternalObservationService loaded")

MAX_REDIRECTS = 3
BACKOFF_BASE_SECONDS = 60
MAX_RETRIES = 3
PAUSE_AFTER_FAILURES = 5


def _load_source_config() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'universe', 'observation_sources.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


class ExternalObservationService:
    def __init__(self, fetch_fn=None, skip_network_validation: bool = False):
        self.config = _load_source_config()
        self.defaults = self.config.get("defaults", {})
        self._fetch = fetch_fn  # injectable for tests
        self.skip_network_validation = skip_network_validation  # tests only

    # ────────────────────── Run a source ──────────────────────

    async def run_source(self, db: AsyncSession, source: ObservationSource,
                         manual: bool = False, actor_id: str = None) -> ObservationRun:
        run = ObservationRun(source_id=source.source_id, node_id=source.node_id, status="running",
                             started_at=datetime.now(timezone.utc))
        db.add(run)
        await db.commit()
        await db.refresh(run)

        try:
            url = validate_url(source.base_url or f"https://{source.domain}")
            if not self.skip_network_validation:
                # C6.4 Gate 0: validate ALL resolved addresses before connecting.
                resolve_all_and_validate(urlparse(url).hostname)

            status, headers, body = await self._fetch_page(source, url)
            if status in (429,):
                retry_after = int(headers.get("retry-after", "60") or 60) if headers else 60
                raise _HttpError(429, f"rate limited retry-after={retry_after}")
            if status >= 500:
                raise _HttpError(status, f"server error {status}")
            if status in (403, 404):
                raise _HttpError(status, f"http {status}")
            if status == 304:
                return await self._finish(db, run, "completed", http_status=304, error_code=None,
                                          source=source, change_created=False)

            content_type = (headers.get("content-type") or "").split(";")[0].strip().lower()
            allowed = source.allowed_content_types or self.defaults.get("allowed_content_types", ["text/html"])
            if content_type and not any(content_type in a for a in allowed):
                return await self._fail(db, run, "bad_content_type", source, f"content-type {content_type} rejected")

            content_hash = hashlib.sha256(body).hexdigest()
            prev_artifact = (await db.execute(
                select(ObservationArtifact).where(
                    ObservationArtifact.source_id == source.source_id,
                    ObservationArtifact.content_hash != content_hash,
                ).order_by(ObservationArtifact.captured_at.desc()).limit(1)
            )).scalars().first()
            prev_hash = prev_artifact.content_hash if prev_artifact else None
            same_hash = (await db.execute(
                select(ObservationArtifact).where(
                    ObservationArtifact.content_hash == content_hash,
                    ObservationArtifact.source_id == source.source_id,
                ).limit(1)
            )).scalars().first()
            if same_hash:
                # NO_CHANGE: identical content, do not create duplicate candidates.
                return await self._finish(db, run, "completed", http_status=status,
                                          content_hash=content_hash, previous_content_hash=prev_hash,
                                          source=source, change_created=False, candidates_found=0)

            artifact = await self._save_artifact(db, run, source, url, status, headers, body, content_hash)
            facts = self._extract_facts(artifact)
            created = 0
            for fact in facts[:5]:
                try:
                    from app.services.learning_loop import LearningLoopService
                    lls = LearningLoopService()
                    await lls.create_observation(db, {
                        "node_id": source.node_id or fact.get("node_id", ""),
                        "change_type": "user_evidence",
                        "source_type": "external",
                        "source_id": f"{source.source_id}-{artifact.content_hash[:8]}",
                        "source_evidence_ids": [str(artifact.id)],
                        "evidence_summary": fact.get("excerpt", "")[:300],
                        "evidence_url": artifact.source_url,
                        "proposed_value": {
                            "title": fact.get("title", "")[:200],
                            "claim": fact.get("excerpt", "")[:500],
                            "source_url": artifact.source_url,
                            "source_name": source.name,
                            "evidence_type": "media_report" if source.source_type == "media" else "official_website",
                            "confidence_level": 0.4,
                        },
                        "confidence_level": 0.4,
                    }, actor_id=actor_id or "system")
                    created += 1
                except Exception:
                    continue
            return await self._finish(db, run, "completed", http_status=status, content_hash=content_hash,
                                      previous_content_hash=prev_hash, source=source,
                                      candidates_found=created, change_created=created > 0)
        except Exception as e:
            code = self._classify_error(e)
            return await self._fail(db, run, code, source, str(e)[:500])

    # ────────────────────── Fetch with SSRF safety ──────────────────────

    async def _fetch_page(self, source, url: str):
        if self._fetch is not None:
            return await self._fetch(source, url)  # test fixture / injectable fetcher
        import httpx
        timeout = source.timeout_seconds or self.defaults.get("timeout_seconds", 10)
        max_size = source.max_content_size or self.defaults.get("max_content_size", 1048576)
        redirects = 0
        current = url
        async with httpx.AsyncClient(follow_redirects=False, timeout=timeout) as client:
            while True:
                resp = await client.get(current, headers={"User-Agent": "GEO-Universe-Observer/1.0"})
                if resp.status_code in (301, 302, 303, 307, 308):
                    redirects += 1
                    if redirects > MAX_REDIRECTS:
                        raise ValueError("too many redirects")
                    loc = resp.headers.get("location", "")
                    next_url = validate_redirect_url(loc if loc.startswith("http") else
                                                     current.rsplit("/", 1)[0] + "/" + loc.lstrip("/"))
                    validate_host_ip(urlparse(next_url).hostname)
                    current = next_url
                    continue
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", "60") or 60)
                    raise _HttpError(429, f"rate limited retry-after={retry_after}")
                if resp.status_code >= 500:
                    raise _HttpError(resp.status_code, f"server error {resp.status_code}")
                if resp.status_code == 404:
                    raise _HttpError(404, "not found")
                if resp.status_code == 403:
                    raise _HttpError(403, "forbidden")
                if len(resp.content) > max_size:
                    raise ValueError("response too large")
                return resp.status_code, resp.headers, resp.content


    # ────────────────────── Artifact + extraction ──────────────────────

    async def _save_artifact(self, db, run, source, url, status, headers, body, content_hash) -> ObservationArtifact:
        text = self._decode_text(body)
        title = self._extract_title(text)
        artifact = ObservationArtifact(
            run_id=run.id, source_id=source.source_id, node_id=source.node_id,
            source_url=url, canonical_url=url, content_hash=content_hash,
            content_type=(headers.get("content-type") or "").split(";")[0].strip(),
            title=title[:500] if title else None,
            extracted_text=text[:20000],  # bounded snapshot; never store full copyrighted pages
            source_trust_tier=source.trust_tier,
            retention_until=datetime.now(timezone.utc) + timedelta(days=source.retention_days),
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        return artifact

    def _decode_text(self, body: bytes) -> str:
        for enc in ("utf-8", "gb18030"):
            try:
                return body.decode(enc)
            except Exception:
                continue
        return body.decode("utf-8", errors="replace")

    def _extract_title(self, text: str) -> Optional[str]:
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1)).strip()[:300]
        return None

    def _extract_facts(self, artifact: ObservationArtifact) -> List[Dict]:
        """Deterministic extraction: title + JSON-LD/meta. AI may assist later."""
        facts = []
        text = artifact.extracted_text or ""
        if artifact.title:
            facts.append({
                "title": f"页面标题：{artifact.title}",
                "excerpt": artifact.title[:500],
                "node_id": artifact.node_id,
                "source_url": artifact.source_url,
            })
        # JSON-LD basic extraction (deterministic, no execution)
        for m in re.finditer(r'<script[^>]*type=.?application/ld\+json.?(.*?)</script>', text, re.S | re.I):
            raw = m.group(1).strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    desc = data.get("description") or data.get("about") or ""
                    if desc:
                        facts.append({
                            "title": data.get("name") or data.get("headline") or "JSON-LD 结构化事实",
                            "excerpt": str(desc)[:500],
                            "node_id": artifact.node_id,
                            "source_url": artifact.source_url,
                        })
            except Exception:
                continue
        return facts

    # ────────────────────── Helpers ──────────────────────

    def _classify_error(self, e) -> str:
        if isinstance(e, _HttpError):
            return f"http_{e.status}"
        msg = str(e).lower()
        if "ssrf" in msg or "blocked" in msg or "ip range" in msg or "dns" in msg:
            return "ssrf"
        if "too large" in msg:
            return "too_large"
        if "content-type" in msg or "content type" in msg:
            return "bad_content_type"
        if "timeout" in msg:
            return "timeout"
        if "redirect" in msg:
            return "redirect_limit"
        return "fetch_error"

    async def _fail(self, db, run: ObservationRun, code: str, source, reason: str) -> ObservationRun:
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error_code = code
        run.retry_count = (run.retry_count or 0) + 1
        source.consecutive_failures = (source.consecutive_failures or 0) + 1
        if source.consecutive_failures >= PAUSE_AFTER_FAILURES:
            source.paused = True
        source.next_run_at = datetime.now(timezone.utc) + timedelta(seconds=BACKOFF_BASE_SECONDS * min(source.consecutive_failures, 6))
        await db.commit()
        await db.refresh(run)
        return run

    async def _finish(self, db, run: ObservationRun, status: str, **kw) -> ObservationRun:
        run.status = status
        run.completed_at = datetime.now(timezone.utc)
        for k, v in kw.items():
            if k in ("http_status", "content_hash", "previous_content_hash", "error_code", "candidates_found", "change_created"):
                setattr(run, k, v)
        if "source" in kw and kw["source"]:
            src = kw["source"]
            src.consecutive_failures = 0
            src.last_success_at = datetime.now(timezone.utc)
            src.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=src.schedule_minutes or 1440)
        await db.commit()
        await db.refresh(run)
        return run


class _HttpError(Exception):
    def __init__(self, status: int, message: str = ""):
        super().__init__(message)
        self.status = status
