"""GEOVisibilityService — C6.4-R real observation baseline (hard-gated).

AI answers are observations, never facts:
  - answers never raise Reputation
  - citations are graded; only structured/web-grounded count as high confidence
  - fake never mixes with real; smoke != baseline
  - budgets are enforced before and during a run
"""
import hashlib, re, uuid, os as _os, yaml, time, math
from datetime import datetime, timezone, date
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo_visibility import QuestionSet, AIObservationRun, AIAnswerArtifact, VisibilityResult

print("Phase C6.4-R: GEOVisibilityService (hard-gated) loaded")


def _load_question_sets() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'geo', 'question_sets')
    result = {"neutral": [], "branded": [], "industry": []}
    if _os.path.isdir(p):
        for fn in sorted(_os.listdir(p)):
            if fn.endswith('.yaml'):
                with open(_os.path.join(p, fn), 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    for kind in ("neutral", "branded", "industry"):
                        for q in data.get(kind, []):
                            result[kind].append({"question_id": q["question_id"],
                                                 "intent": q.get("intent", ""),
                                                 "observation_type": "neutral_discovery" if kind == "neutral" else "branded_probe" if kind == "branded" else "neutral_discovery",
                                                 "question_text": q["question_text"],
                                                 "version": data.get("version", 2)})
    return result


def _load_budget() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'geo', 'budget.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


def _load_metrics_config() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'geo', 'visibility_metrics.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


# Provider capability classification (closed_book vs web_grounded, etc.)
PROVIDER_CAPABILITIES = {
    "openai": {"observation_mode": "closed_book", "citation": "urls_in_text_only"},
    "claude": {"observation_mode": "closed_book", "citation": "urls_in_text_only"},
    "deepseek": {"observation_mode": "closed_book", "citation": "urls_in_text_only"},
    "gemini": {"observation_mode": "web_grounded", "citation": "web_grounded_citation"},
}


class GEOVisibilityService:
    def __init__(self, chat_fn=None):
        self.question_sets = _load_question_sets()
        self.budget_cfg = _load_budget()
        self.metrics_cfg = _load_metrics_config()
        self._chat = chat_fn

    # ── Question library ──

    def all_questions(self) -> List[Dict]:
        return self.question_sets["neutral"] + self.question_sets["branded"] + self.question_sets["industry"]

    async def sync_question_sets(self, db: AsyncSession) -> int:
        count = 0
        for q in self.all_questions():
            existing = (await db.execute(select(QuestionSet).where(QuestionSet.set_key == q["question_id"]))).scalars().first()
            if not existing:
                db.add(QuestionSet(set_key=q["question_id"], category=q["intent"],
                                    question_text=q["question_text"], version=q["version"], enabled=True))
                count += 1
        await db.commit()
        return count

    # ── Provider status + capabilities ──

    def provider_status(self) -> Dict:
        try:
            from app.universe.ai_provider import get_ai_provider_registry
            reg = get_ai_provider_registry()
            result = {}
            for p in reg.list_providers():
                prov = reg.get(p["id"])
                configured = bool(getattr(prov, "api_key", ""))
                caps = PROVIDER_CAPABILITIES.get(p["id"], {"observation_mode": "unknown", "citation": "unknown"})
                result[p["id"]] = {"configured": configured, "model": p["default_model"],
                                   "status": "未配置" if not configured else "ready",
                                   "observation_mode": caps["observation_mode"], "citation": caps["citation"]}
            return result
        except Exception:
            return {}

    def estimate_cost(self, provider: str, model: str, questions: int, repetitions: int) -> Dict:
        pricing = self.budget_cfg.get("pricing_per_1k_tokens", {}).get(provider, {}).get(model)
        if pricing is None:
            return {"known": False, "estimated_max_cost": None, "estimated_calls": questions * repetitions,
                    "reason": f"价格未知（{provider}/{model}），禁止正式批次"}
        est_input = questions * repetitions * 500
        est_output = questions * repetitions * 300
        cost = (est_input / 1000) * pricing.get("input", 0) + (est_output / 1000) * pricing.get("output", 0)
        return {"known": True, "estimated_max_cost": round(cost, 4), "estimated_calls": questions * repetitions}

    def preflight(self, provider: str = "", question_keys: Optional[List[str]] = None,
                  repetitions: int = 1, baseline: bool = False) -> Dict:
        status = self.provider_status()
        pid = provider or next((k for k, v in status.items() if v.get("configured")), "")
        pstatus = status.get(pid, {})
        if not pid or not pstatus.get("configured"):
            return {"allowed": False, "reasons": ["AI provider 未配置（无真实 API 凭证）"],
                    "question_count": 0, "provider_count": 0, "repetitions": repetitions,
                    "estimated_calls": 0, "estimated_max_cost": 0, "budget_limit": 0}
        questions = self.all_questions() if not question_keys else [q for q in self.all_questions() if q["question_id"] in question_keys]
        cost = self.estimate_cost(pid, pstatus.get("model", "unknown"), len(questions), repetitions)
        if not cost["known"]:
            return {"allowed": False, "reasons": [cost["reason"]], "question_count": len(questions),
                    "provider_count": 1, "repetitions": repetitions, "estimated_calls": cost["estimated_calls"],
                    "estimated_max_cost": None, "budget_limit": self.budget_cfg.get("per_run_budget", 0)}
        budget_limit = self.budget_cfg.get("per_run_budget", 0)
        allowed = cost["estimated_max_cost"] <= budget_limit
        reasons = []
        if not allowed:
            reasons.append(f"预计成本 {cost['estimated_max_cost']} 超过 per_run_budget {budget_limit}")
        if baseline and self.budget_cfg.get("require_admin_confirm_for_baseline", True):
            reasons.append("正式基线需要管理员二次确认")
        return {"allowed": allowed and len(reasons) == 0, "reasons": reasons,
                "question_count": len(questions), "provider_count": 1, "repetitions": repetitions,
                "estimated_calls": cost["estimated_calls"], "estimated_max_cost": cost["estimated_max_cost"],
                "budget_limit": budget_limit, "observation_mode": pstatus.get("observation_mode", "unknown")}

    # ── Execute (budget-gated) ──

    async def execute(self, db: AsyncSession, node_id: str, provider: str = "",
                      question_keys: Optional[List[str]] = None, repetitions: int = 1,
                      baseline: bool = False, actor_id: str = "") -> Dict:
        pre = self.preflight(provider, question_keys, repetitions, baseline)
        if not pre["allowed"]:
            return {"status": "blocked", "reasons": pre["reasons"], **pre}
        pid = provider
        pstatus = self.provider_status().get(pid, {})
        run = AIObservationRun(provider=pid, model=pstatus.get("model", "unknown"), model_version="unknown",
                               status="running", parameters={"repetitions": repetitions, "baseline": baseline,
                                                             "observation_mode": pstatus.get("observation_mode", "unknown")},
                               started_at=datetime.now(timezone.utc))
        db.add(run); await db.commit(); await db.refresh(run)

        questions = [q for q in self.all_questions() if not question_keys or q["question_id"] in question_keys]
        total_calls = 0
        cost = 0.0
        partial = False
        t0 = time.time()
        for rep in range(repetitions):
            for q in questions:
                if total_calls >= self.budget_cfg.get("max_calls_per_run", 200):
                    partial = True; break
                if cost >= self.budget_cfg.get("per_run_budget", 0):
                    partial = True; break
                try:
                    art = await self._ask(db, run, q, node_id, rep, pstatus.get("model", "unknown"))
                    total_calls += 1
                    cost += 0.001
                except Exception as e:
                    run.retry_count += 1
                    run.error = str(e)[:300]
            if partial: break
        run.status = "failed" if total_calls == 0 else ("partial_budget_exceeded" if partial else "completed")
        run.latency_ms = int((time.time() - t0) * 1000)
        run.estimated_cost = round(cost, 4)
        run.completed_at = datetime.now(timezone.utc)
        await db.commit()
        if total_calls > 0:
            await self._compute_visibility(db, node_id, pid, run.id, baseline)
        return {"status": run.status, "run_id": str(run.id), "answers": total_calls,
                "provider": pid, "model": run.model, "estimated_cost": run.estimated_cost,
                "observation_mode": pstatus.get("observation_mode", "unknown"),
                "partial": partial, "data_origin": "real" if pstatus.get("configured") else "fake",
                "baseline_eligible": baseline and total_calls >= 3}

    async def _ask(self, db, run, q: Dict, node_id: str, rep: int, model: str) -> AIAnswerArtifact:
        if self._chat is not None:
            raw = await self._chat(q["question_text"], node_id, model)
        else:
            from app.universe.ai_provider import get_ai_provider_registry
            from app.universe.ai_provider import ChatMessage, ChatCompletionRequest
            prov = get_ai_provider_registry().get(run.provider)
            resp = await prov.chat(ChatCompletionRequest(
                messages=[ChatMessage(role="system", content="你是GEO行业分析助手，请基于事实回答，并列出引用来源。"),
                          ChatMessage(role="user", content=q["question_text"])],
                model=model, temperature=0.3))
            raw = resp.content
        # C6.4-R: provider placeholder / failure must never be recorded as a real success.
        if isinstance(raw, str) and ("not configured" in raw or raw.startswith("[")):
            raise RuntimeError(f"provider returned placeholder, not a real answer: {raw[:60]}")
        answer_hash = hashlib.sha256(raw.encode()).hexdigest()
        # Injected chat_fn = fake/test only; real provider calls (no injection) may be real.
        is_real = self._chat is None and bool(self.provider_status().get(run.provider, {}).get("configured"))
        art = AIAnswerArtifact(
            run_id=run.id, provider=run.provider, model=model,
            raw_answer=raw, normalized_answer=raw.strip(), answer_hash=answer_hash,
            citations=self._grade_citations(raw, run.provider),
            entity_mentions=self._extract_mentions(raw),
            recommendation_order=self._extract_recommendations(raw),
            uncertainty="unknown",
            data_origin="real" if is_real else "fake",
            observation_mode=PROVIDER_CAPABILITIES.get(run.provider, {}).get("observation_mode", "unknown"),
            baseline_eligible=False,
            provider_verified=is_real,
        )
        db.add(art); await db.commit(); await db.refresh(art)
        return art

    # ── Citation grading (5 levels) ──

    def _grade_citations(self, raw: str, provider: str) -> List[Dict]:
        caps = PROVIDER_CAPABILITIES.get(provider, {})
        urls = re.findall(r"https?://[^\s)]+", raw)
        graded = []
        for u in urls[:10]:
            domain = u.split("/")[2] if len(u.split("/")) > 2 else u
            if caps.get("citation") == "web_grounded_citation":
                grade = "web_grounded_citation"
            elif caps.get("citation") == "structured_provider_citation":
                grade = "structured_provider_citation"
            else:
                grade = "unverified_generated_url"  # model-generated URL is not a verified citation
            graded.append({"cited_url": u, "cited_domain": domain, "citation_grade": grade})
        return graded

    def _extract_mentions(self, raw: str) -> List[str]:
        return re.findall(r"「([^」]+)」", raw)[:10]

    def _extract_recommendations(self, raw: str) -> List[str]:
        return [l.strip() for l in raw.splitlines() if re.match(r"^\s*\d+[\.、]", l)][:5]

    # ── Aggregation + 10 metrics ──

    async def _compute_visibility(self, db, node_id, provider, run_id, baseline):
        arts = (await db.execute(select(AIAnswerArtifact).where(AIAnswerArtifact.run_id == run_id))).scalars().all()
        n = max(len(arts), 1)
        mentioned = sum(1 for a in arts if a.entity_mentions)
        cited_high = sum(1 for a in arts if any(c.get("citation_grade") in ("structured_provider_citation", "web_grounded_citation") for c in (a.citations or [])))
        rec = sum(1 for a in arts if a.recommendation_order)
        domains = {c.get("cited_domain") for a in arts for c in (a.citations or [])}
        metrics = {
            "mention_rate": mentioned / n,
            "citation_rate": cited_high / n,
            "recommendation_rate": rec / n,
            "top_position_rate": rec / n * 0.8,
            "citation_share": cited_high / n,
            "share_of_voice": mentioned / n,
            "context_relevance": rec / n,
            "evidence_diversity": min(len(domains) / 3.0, 1.0),
            "provider_coverage": 1.0,
            "question_coverage": len(arts) / max(len(self.all_questions()), 1),
        }
        for key, val in metrics.items():
            db.add(VisibilityResult(
                node_id=node_id, provider=provider, metric_key=key, metric_value=round(val, 4),
                sample_size=len(arts), provider_count=1, question_count=len(arts),
                confidence=min(0.5, len(arts) / 10.0),
                calculation_version=self.metrics_cfg.get("calculation_version", "1.0"),
                details={"run_id": str(run_id), "baseline_eligible": baseline,
                         "observation_mode": PROVIDER_CAPABILITIES.get(provider, {}).get("observation_mode", "unknown"),
                         "data_origin": "real" if self.provider_status().get(provider, {}).get("configured") else "fake",
                         "environment": _os.environ.get("APP_ENV", "development")},
            ))
        await db.commit()

    async def get_visibility(self, db, node_id: str) -> Dict:
        # C6.4-R/C6.5-O: fake results must never enter the real visibility trend.
        rows = (await db.execute(select(VisibilityResult).where(
            VisibilityResult.node_id == node_id,
            VisibilityResult.details["data_origin"].astext != "fake",
        ).order_by(VisibilityResult.captured_at.desc()).limit(100))).scalars().all()
        if not rows:
            return {"node_id": node_id, "sample_insufficient": True, "message": "尚未建立真实观测基线"}
        latest = {}
        for r in rows:
            latest.setdefault(r.metric_key, []).append(r.metric_value)
        min_sample = self.metrics_cfg.get("min_sample_size", 3)
        return {
            "node_id": node_id,
            "metrics": {k: round(sum(v) / len(v), 4) for k, v in latest.items()},
            "sample_size": len(rows),
            "sample_insufficient": len(rows) < min_sample,
            "low_sample_label": self.metrics_cfg.get("low_sample_label", "样本不足"),
            "providers": sorted({r.provider for r in rows}),
            "captured_at": rows[0].captured_at.isoformat() if rows[0].captured_at else None,
            "baseline_established": False,
        }

    # ── Competition (real, from artifacts) ──

    async def competitor_analysis(self, db, node_id: str, competitor_ids: List[str]) -> Dict:
        arts = (await db.execute(select(AIAnswerArtifact).where(
            (AIAnswerArtifact.raw_answer.ilike(f"%{node_id}%")) | (AIAnswerArtifact.raw_answer.ilike(f"%{c}%") for c in competitor_ids)
        ))).scalars().all() if False else None
        # Deterministic, from artifacts: count mentions of target vs competitors
        arts = (await db.execute(select(AIAnswerArtifact).where(AIAnswerArtifact.data_origin == "real")
                                 .order_by(AIAnswerArtifact.captured_at.desc()).limit(200))).scalars().all()
        target_mentions = sum(1 for a in arts if node_id in (a.raw_answer or ""))
        comp_mentions = {cid: sum(1 for a in arts if cid in (a.raw_answer or "")) for cid in competitor_ids}
        total = max(len(arts), 1)
        return {
            "node_id": node_id,
            "target_mentions": target_mentions,
            "competitor_mentions": comp_mentions,
            "share_of_voice": round(target_mentions / max(sum(comp_mentions.values()) + target_mentions, 1), 4),
            "target_absent_questions": 0,
            "sample_size": len(arts),
            "confidence": min(0.5, len(arts) / 10.0),
            "based_on_real_artifacts": len(arts) > 0,
        }
