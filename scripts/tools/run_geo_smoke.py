"""C6.4-R Real GEO Observation Smoke Runner.

Run in an environment with real API credentials and network:
  1. Sets OPENAI_API_KEY / ANTHROPIC_API_KEY (or others) via env
  2. Runs preflight (budget gate, provider readiness, price known)
  3. Executes 2 providers x 3 questions x 2 repetitions = 12 calls
  4. Saves real raw answers, citations, mentions
  5. Prints a Smoke report (never claims baseline)

Usage:
  $env:OPENAI_API_KEY=...; $env:ANTHROPIC_API_KEY=...
  python scripts/tools/run_geo_smoke.py
"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.database import _get_session_factory
from app.services.geo_visibility import GEOVisibilityService

SMOKE_QUESTION_KEYS = ["brand_recognition_1", "provider_recommendation_1", "expert_explanation_1"]
SMOKE_PROVIDERS = ["openai", "claude"]  # fall back to whatever is configured


async def main():
    svc = GEOVisibilityService()
    status = svc.provider_status()
    print("=" * 60)
    print("C6.4-R REAL SMOKE")
    print("=" * 60)
    configured = [k for k, v in status.items() if v.get("configured")]
    print("Providers:", json.dumps(status, ensure_ascii=False, indent=2))
    if not configured:
        print("\nBLOCKED: no real API credentials configured (OPENAI_API_KEY/ANTHROPIC_API_KEY/etc).")
        print("Set credentials in environment and re-run. No fake data will be produced.")
        return 1
    providers = [p for p in SMOKE_PROVIDERS if p in configured] or configured[:2]
    print(f"\nUsing providers: {providers} (only real, configured providers)")

    # Budget preflight (must pass)
    for p in providers:
        pre = svc.preflight(p, SMOKE_QUESTION_KEYS, repetitions=2)
        print(f"preflight {p}: allowed={pre.get('allowed')} cost={pre.get('estimated_max_cost')} reasons={pre.get('reasons')}")
        if not pre.get("allowed"):
            print(f"BLOCKED: {p} preflight failed")
            return 1

    # Execute smoke (real)
    factory = _get_session_factory()
    async with factory() as db:
        results = []
        for p in providers:
            r = await svc.execute(db, node_id="smoke-node", provider=p,
                                  question_keys=SMOKE_QUESTION_KEYS, repetitions=2, baseline=False)
            results.append(r)
            print(f"\n[{p}] status={r.get('status')} answers={r.get('answers')} cost={r.get('estimated_cost')} mode={r.get('observation_mode')}")

    print("\n" + "=" * 60)
    print("SMOKE COMPLETE")
    ok = sum(1 for r in results if r.get("status") == "completed" and r.get("answers", 0) > 0)
    print(f"Real calls succeeded: {ok}/{len(results)} runs; answers only counted when not placeholder.")
    print("Baseline NOT claimed; full 180-call run requires admin budget confirmation.")
    print("=" * 60)
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
