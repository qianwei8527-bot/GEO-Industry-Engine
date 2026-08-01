"""C6.5-O operational authenticity audit (real fetch attempt).

Fetches each real node's official source URL with bounded size, computes
content_hash from the actual response, records retrieved_at / final URL /
HTTP / Content-Type. Success upgrades to fetched/observed ONLY (never
auto-verified). Failures are classified and remain unverified_snapshot.
"""
import asyncio, json, os, sys, hashlib, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
import httpx
from sqlalchemy import select
from app.database import _get_session_factory
from app.models.company import Company
from app.models.evidence import Evidence

REAL_NAMES = ["清华大学", "北京大学", "复旦大学", "上海交通大学", "科大讯飞", "好未来",
              "网易有道", "视源股份", "中国科学院", "中国教育科学研究院",
              "国家教育行政学院", "中国教育装备行业协会"]
MAX_BYTES = 256 * 1024


def classify(exc, status=None) -> str:
    if status is not None:
        if status == 401: return "api_401"
        if status == 402: return "api_402"
        if status == 403: return "http_403"
        if status == 404: return "http_404"
        if status == 429: return "http_429"
        if status >= 500: return "provider_5xx"
        return f"http_{status}"
    msg = str(exc).lower()
    if "dns" in msg or "name or service" in msg or "getaddrinfo" in msg:
        return "dns_failure"
    if "tls" in msg or "ssl" in msg or "certificate" in msg:
        return "tls_failure"
    if "proxy" in msg:
        return "proxy_failure"
    if "connect" in msg or "timed out" in msg or "timeout" in msg or "unreachable" in msg:
        return "connect_failure"
    return "unknown_failure"


async def fetch_one(client, url):
    try:
        async with client.stream("GET", url, follow_redirects=True, timeout=15) as resp:
            body = b""
            async for chunk in resp.aiter_bytes():
                body += chunk
                if len(body) > MAX_BYTES:
                    return {"ok": False, "http": resp.status_code, "reason": "too_large",
                            "final_url": str(resp.url)}
            return {"ok": resp.status_code < 400, "http": resp.status_code,
                    "final_url": str(resp.url), "content_type": resp.headers.get("content-type", ""),
                    "body_len": len(body),
                    "content_hash": hashlib.sha256(body).hexdigest(),
                    "redirects": len(resp.history)}
    except Exception as e:
        return {"ok": False, "reason": classify(e), "http": None, "final_url": None}


async def main():
    rows = []
    async with httpx.AsyncClient(verify=True, timeout=15) as client:
        factory = _get_session_factory()
        async with factory() as db:
            for nm in REAL_NAMES:
                c = (await db.execute(select(Company).where(Company.name == nm))).scalars().first()
                if not c:
                    rows.append({"node": nm, "source": "-", "fetch_status": "unverified_snapshot",
                                 "http": None, "reason": "node missing"})
                    continue
                evs = (await db.execute(select(Evidence).where(Evidence.entity_id == c.id))).scalars().all()
                fetched_any = False
                for ev in evs:
                    url = ev.source_url or ""
                    official = ev.source_type == "official_website" or "身份" in (ev.claim or "")
                    if not url.startswith("http"):
                        rows.append({"node": nm, "url": url, "fetch_status": "unverified_snapshot",
                                     "http": None, "reason": "invalid_url", "official": official})
                        continue
                    r = await fetch_one(client, url)
                    if r["ok"]:
                        fetched_any = True
                        rows.append({"node": nm, "url": url, "fetch_status": "fetched_observed",
                                     "http": r["http"], "final_url": r["final_url"],
                                     "content_type": r.get("content_type", ""),
                                     "content_hash": r["content_hash"], "body_len": r.get("body_len", 0),
                                     "redirects": r.get("redirects", 0),
                                     "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                     "official": official, "reason": None})
                    else:
                        rows.append({"node": nm, "url": url, "fetch_status": "unverified_snapshot",
                                     "http": r.get("http"), "reason": r.get("reason", "fetch_failed"),
                                     "official": official})
            # write audit result file
            out = os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_sandbox_v1", "authenticity_audit.json")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "rows": rows}, f, ensure_ascii=False, indent=2)
            fetched = sum(1 for r in rows if r["fetch_status"] == "fetched_observed")
            failed = sum(1 for r in rows if r["fetch_status"] == "unverified_snapshot")
            print(f"AUDIT: {len(rows)} records, fetched={fetched}, unverified={failed}")
            from collections import Counter
            print("failure classes:", dict(Counter(r.get("reason") for r in rows if r.get("reason"))))
            # per-node official source availability
            for nm in REAL_NAMES:
                node_rows = [r for r in rows if r["node"] == nm and r.get("official")]
                ok = any(r["fetch_status"] == "fetched_observed" for r in node_rows)
                print(f"  {nm}: official {'FETCHED' if ok else 'UNVERIFIED'} ({len(node_rows)} official records)")

if __name__ == "__main__":
    asyncio.run(main())
