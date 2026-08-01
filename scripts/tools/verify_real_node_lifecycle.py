"""
GEO Universe Phase D0.1 - Real Node Lifecycle Validation

Verifies that a single real enterprise can enter Universe and run the
complete growth chain:

  Observation -> Evidence -> Identity -> Position -> Reputation
  -> Possibility -> Connection

This is the core proof that Universe is a living system, not a feature stack.
"""
import sys, io, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from datetime import datetime, timezone, timedelta

results = {"passed": 0, "failed": 0, "chain": []}

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results["passed" if condition else "failed"] += 1
    results["chain"].append({"stage": name, "status": status, "detail": detail})
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))

print("=" * 66)
print("  GEO Universe Phase D0.1 - Real Node Lifecycle Validation")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 66)

NODE_ID = "real-company-001"
NODE_TYPE = "company"

# ---------------------------------------------------------------
# Stage 1: Observation - enter the node from real-world facts
# ---------------------------------------------------------------
print("\n-- Stage 1: Observation (real enterprise enters Universe) --")

real_facts = [
    ("company_profile", "企业成立于2019年，总部位于上海，专注AI营销科技"),
    ("official_site", "官网提供GEO服务、内容营销、AI Agent开发三类产品"),
    ("product_line", "GEO内容优化、AI搜索可见度分析、企业AI知识库"),
    ("service_case", "服务过3家世界500强企业客户"),
    ("customer_list", "公开客户：某快消品牌、某新能源汽车、某金融机构"),
    ("industry_news", "2026年获得行业GEO创新奖提名"),
    ("certification", "通过ISO 27001信息安全管理体系认证"),
    ("team_profile", "团队规模120人，其中技术团队60人"),
    ("partner_network", "与2家数据服务商、1家行业协会建立合作"),
]

memory = None
from app.universe.memory_engine import MemoryEngine, get_memory_engine
memory = get_memory_engine()

observed = 0
for cat, stmt in real_facts:
    fact = memory.record_fact(node_id=NODE_ID, node_type=NODE_TYPE,
                              statement=stmt, category=cat, source="observation")
    ev = memory.attach_evidence(fact.fact_id, "url", f"https://example.com/evidence/{cat}")
    memory.verify_evidence(ev.evidence_id, "universe-observer")
    observed += 1

check("9 real-world facts observed", observed == len(real_facts),
      f"{observed} facts recorded with verified evidence")
check("Facts persisted in Memory layer", memory.stats()["total_facts"] >= len(real_facts))

# ---------------------------------------------------------------
# Stage 2: Evidence - every fact has verifiable proof
# ---------------------------------------------------------------
print("\n-- Stage 2: Evidence (verifiable proof attached) --")
facts = memory.get_facts(NODE_ID)
all_have_evidence = all(len(memory.get_evidence_for_fact(f.fact_id)) >= 1 for f in facts)
check("Every fact has evidence", all_have_evidence)
check("Evidence verified", all(e.verified for f in facts for e in memory.get_evidence_for_fact(f.fact_id)))

# ---------------------------------------------------------------
# Stage 3: Identity - Universe knows who this node is
# ---------------------------------------------------------------
print("\n-- Stage 3: Identity (Context Engine) --")
from app.universe.context_engine import get_context_engine, NodeContext
ctx = get_context_engine().understand(NODE_ID, NODE_TYPE, {
    "name": "星辰AI营销科技",
    "description": "AI营销科技服务商，专注GEO与AI搜索优化",
    "industry_id": "ai-marketing",
    "geo_score": 72,
    "trust_score": 68,
    "evidence_count": len(real_facts),
    "capability_count": 5,
    "relationship_count": 3,
    "certification_count": 1,
})
check("Identity created", ctx.identity.get("name") == "星辰AI营销科技", ctx.identity.get("name", ""))
check("Node type resolved", ctx.identity.get("node_type") == "company")

# ---------------------------------------------------------------
# Stage 4: Position - where is this node in the industry?
# ---------------------------------------------------------------
print("\n-- Stage 4: Position (6-dimension coordinates) --")
pos = ctx.current_position.get("position", {})
check("Industry rank computed", pos.get("industry_rank") is not None,
      f"Top {round(pos.get('industry_rank', 0) * 100)}%")
check("Reputation level assigned", pos.get("reputation_level") in ("A", "B", "C", "D", "E"),
      pos.get("reputation_level", "N/A"))
check("Growth stage assigned", pos.get("growth_stage") in
      ("position", "selfknow", "action", "provision", "accumulate", "reputation"),
      pos.get("growth_stage", "N/A"))
check("Influence score 0-100", 0 <= pos.get("influence_score", 0) <= 100,
      f"score={pos.get('influence_score', 0)}")
check("Narrative generated", bool(ctx.current_position.get("interpretation", {}).get("narrative", "")))

# ---------------------------------------------------------------
# Stage 5: Reputation - trust accumulates from events
# ---------------------------------------------------------------
print("\n-- Stage 5: Reputation (events -> snapshot -> explanation) --")
from app.universe.reputation_engine import get_reputation_engine
re = get_reputation_engine()
re.record_event(NODE_ID, NODE_TYPE, "certification_passed",
                "ISO 27001 certification obtained", "government")
re.record_event(NODE_ID, NODE_TYPE, "customer_success",
                "Completed GEO optimization for 3 enterprise clients", "enterprise_customer")
re.record_event(NODE_ID, NODE_TYPE, "customer_success",
                "AI visibility improved 35% for a Fortune 500 brand", "enterprise_customer")
re.record_event(NODE_ID, NODE_TYPE, "peer_endorsement",
                "Recommended by AI Marketing Industry Association", "association")
re.record_event(NODE_ID, NODE_TYPE, "innovation_release",
                "Released AI Agent-based GEO analysis tool", "self_report")
snap = re.recalculate(NODE_ID, NODE_TYPE)
check("Reputation snapshot created", snap is not None and snap.status != "UNKNOWN",
      f"status={snap.status}, score={snap.overall_score}")
check("7-dimension vector populated", len(snap.dimensions) == 7,
      f"{len(snap.dimensions)} dimensions")
exp = re.get_explanation(NODE_ID)
check("Explanation generated", bool(exp.summary) or bool(exp.recommendations))

# ---------------------------------------------------------------
# Stage 6: Possibility - what can this node become?
# ---------------------------------------------------------------
print("\n-- Stage 6: Possibility (future state graph) --")
from app.universe.possibility_engine import get_possibility_engine
pe = get_possibility_engine()
try:
    graph = pe.project(ctx)
    states = graph.states
    transitions = graph.transitions
    check("Possibility graph generated", len(states) > 1, f"{len(states)} states")
    horizons = {s.horizon_days for s in states.values() if s.horizon_days > 0}
    check("30/90/180 day horizons", all(h in horizons for h in (30, 90, 180)),
          f"horizons: {sorted(horizons)}")
    check("Transitions connect states", len(transitions) >= 1, f"{len(transitions)} transitions")
    needs = graph.get_all_required_connections()
    check("Connection needs identified", len(needs) >= 1, f"{len(needs)} needs")
except Exception as e:
    check("Possibility graph generated", False, str(e))

# ---------------------------------------------------------------
# Stage 7: Connection - who can help this node reach its future?
# ---------------------------------------------------------------
print("\n-- Stage 7: Connection (future-path candidates) --")
from app.universe.connection_engine import get_connection_engine
ce = get_connection_engine()
try:
    report = ce.discover_connections(NODE_ID, NODE_TYPE)
    check("Connection report generated", report is not None)
    check("Candidates found", len(report.candidates) > 0,
          f"{len(report.candidates)} candidates")
    if report.candidates:
        top = sorted(report.candidates, key=lambda x: x.future_alignment_score, reverse=True)[0]
        check("Top candidate scored", top.future_alignment_score > 0,
              f"{top.candidate_name}: {top.future_alignment_score:.0%}")
except Exception as e:
    check("Connection report generated", False, str(e))

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n" + "=" * 66)
total = results["passed"] + results["failed"]
pct = round(results["passed"] / total * 100, 1) if total > 0 else 0
print(f"  NODE LIFECYCLE: {results['passed']}/{total} checks passed ({pct}%)")
print(f"  Verdict: {'LIVING NODE' if results['failed'] == 0 else 'PARTIAL'}")
print("=" * 66)

report = {
    "timestamp": datetime.now().isoformat(),
    "phase": "D0.1",
    "node_id": NODE_ID,
    "node_name": "星辰AI营销科技",
    "chain": results["chain"],
    "summary": {"passed": results["passed"], "failed": results["failed"], "total": total},
    "verdict": "LIVING NODE" if results["failed"] == 0 else "PARTIAL",
}
print("\n" + json.dumps(report, indent=2, ensure_ascii=False))
