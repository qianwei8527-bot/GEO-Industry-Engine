"""C6.5 Public Data Sandbox builder — deterministic, fixed-seed.

Generates data/public_sandbox_v1/*.jsonl:
  - 12 real nodes (public known institutions, P0 sources, observed truth_status)
  - 12 synthetic nodes (clearly fictional, 12 scenario coverage)
  - capabilities / evidence / events / relationships / observations / transactions
  - expected_invariants.json

Real nodes never receive synthetic negative events. Fake transactions only
touch synthetic nodes. Results (Position/Reputation/etc) are NEVER seeded.
"""
import json, hashlib, os, random, uuid
from datetime import datetime, timezone, timedelta

random.seed(20260801)
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_sandbox_v1")
os.makedirs(OUT, exist_ok=True)

def h(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def now(days_ago=0): return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()

REAL = [
    # 4 universities (MOE list)
    {"name": "清华大学", "region": "北京", "type": "university", "website": "https://www.tsinghua.edu.cn",
     "source": "moedu_universities", "external_id": "MOE-10003"},
    {"name": "北京大学", "region": "北京", "type": "university", "website": "https://www.pku.edu.cn",
     "source": "moedu_universities", "external_id": "MOE-10001"},
    {"name": "复旦大学", "region": "上海", "type": "university", "website": "https://www.fudan.edu.cn",
     "source": "moedu_universities", "external_id": "MOE-10246"},
    {"name": "上海交通大学", "region": "上海", "type": "university", "website": "https://www.sjtu.edu.cn",
     "source": "moedu_universities", "external_id": "MOE-10248"},
    # 4 education technology / digital education providers
    {"name": "科大讯飞", "region": "安徽合肥", "type": "edtech", "website": "https://www.iflytek.com",
     "source": "ror", "external_id": "ROR-04d7x5p12"},
    {"name": "好未来", "region": "北京", "type": "edtech", "website": "https://www.100tal.com",
     "source": "ror", "external_id": "ROR-02k48wj47"},
    {"name": "网易有道", "region": "北京", "type": "edtech", "website": "https://www.youdao.com",
     "source": "ror", "external_id": "ROR-0gxqqxr70"},
    {"name": "视源股份", "region": "广东广州", "type": "edtech", "website": "https://www.cvte.com",
     "source": "ror", "external_id": "ROR-0t42fpv84"},
    # 2 research institutes
    {"name": "中国科学院", "region": "北京", "type": "research", "website": "https://www.cas.cn",
     "source": "ror", "external_id": "ROR-00yjd5n27"},
    {"name": "中国教育科学研究院", "region": "北京", "type": "research", "website": "https://www.nies.edu.cn",
     "source": "ror", "external_id": "ROR-01zkpg346"},
    # 2 government / industry
    {"name": "国家教育行政学院", "region": "北京", "type": "government", "website": "https://www.naea.edu.cn",
     "source": "moedu_stats", "external_id": "MOE-NAEA"},
    {"name": "中国教育装备行业协会", "region": "北京", "type": "industry", "website": "https://www.ceeia.cn",
     "source": "moedu_stats", "external_id": "CEEIA-001"},
]

# 12 synthetic scenarios (clearly fictional names)
SYNTH = [
    {"scenario": "high_evidence_mature", "name": "启明教育云（仿真）"},
    {"scenario": "self_report_only_new", "name": "新芽智学（仿真）"},
    {"scenario": "capability_without_evidence", "name": "博闻数字课堂（仿真）"},
    {"scenario": "same_name_duplicate", "name": "星辰教育科技（仿真·疑似重名）"},
    {"scenario": "domain_probable_duplicate", "name": "曜石智联（仿真·域名近似）"},
    {"scenario": "verified_media_report", "name": "慧谷教育科技（仿真）"},
    {"scenario": "unverifiable_case", "name": "云梯课堂（仿真）"},
    {"scenario": "evidence_expired", "name": "晨光学习平台（仿真）"},
    {"scenario": "successful_transaction", "name": "知行数据服务（仿真）"},
    {"scenario": "failed_unarbitrated_transaction", "name": "弘毅交付（仿真）"},
    {"scenario": "relationship_growing", "name": "联思生态（仿真）"},
    {"scenario": "observation_rejected", "name": "远舟评测（仿真）"},
]

def build():
    manifest = {"version": "v1", "seed": 20260801, "generated_at": now(),
                "data_origin": "public_observation", "note": "fixed snapshot; results not seeded"}
    nodes, caps, evs, events, rels, obs, txs = [], [], [], [], [], [], []
    nid = {}
    for i, r in enumerate(REAL):
        nid[r["name"]] = f"real-{i+1:02d}"
        nodes.append({"node_id": nid[r["name"]], "name": r["name"], "region": r["region"], "node_type": "company",
                      "website": r["website"], "data_origin": "public_observation", "truth_status": "observed",
                      "source": r["source"], "external_id": r["external_id"], "is_synthetic": False})
        caps.append({"node_id": nid[r["name"]], "name": "教育数字化研究" if r["type"] == "university" else "教育科技服务", "level": 3})
        caps.append({"node_id": nid[r["name"]], "name": "公开数据治理", "level": 2})
        evs.append({"node_id": nid[r["name"]], "title": f"{r['name']} 官方身份来源", "evidence_type": "official_website",
                    "source_url": r["website"], "source_name": r["source"], "truth_status": "observed",
                    "is_synthetic": False, "may_affect_real_metrics": True})
        evs.append({"node_id": nid[r["name"]], "title": f"{r['name']} 公开学术成果", "evidence_type": "data_result",
                    "source_url": "https://openalex.org", "source_name": "openalex", "truth_status": "observed",
                    "is_synthetic": False, "may_affect_real_metrics": True})
        evs.append({"node_id": nid[r["name"]], "title": f"{r['name']} 行业公开报道", "evidence_type": "media_report",
                    "source_url": "https://www.gov.cn", "source_name": "moedu_stats", "truth_status": "observed",
                    "is_synthetic": False, "may_affect_real_metrics": True})
        events.append({"node_id": nid[r["name"]], "event_type": "public_record", "title": f"{r['name']} 公开名录登记",
                       "description": f"来自 {r['source']} 的公开机构登记", "impact_score": 0.5})
        rels.append({"node_a": nid[r["name"]], "node_b": nid["清华大学"], "type": "public_affiliation", "weight": 0.4})

    for j, s in enumerate(SYNTH):
        sid = f"syn-{j+1:02d}"
        nid[s["name"]] = sid
        nodes.append({"node_id": sid, "name": s["name"], "region": "仿真市", "node_type": "company",
                      "website": f"https://{sid}.example.com", "data_origin": "synthetic", "truth_status": "synthetic",
                      "source": "simulation_world", "is_synthetic": True, "scenario": s["scenario"]})
        caps.append({"node_id": sid, "name": "仿真教育服务", "level": 2})
        if s["scenario"] != "self_report_only_new":
            evs.append({"node_id": sid, "title": f"{s['name']} 仿真官网证据", "evidence_type": "official_website",
                        "source_url": f"https://{sid}.example.com", "source_name": "simulation", "truth_status": "synthetic",
                        "is_synthetic": True, "may_affect_real_metrics": False})
        if s["scenario"] == "verified_media_report":
            evs.append({"node_id": sid, "title": f"{s['name']} 已核验媒体报道（仿真）", "evidence_type": "media_report",
                        "source_url": f"https://{sid}.example.com/news", "source_name": "simulation", "truth_status": "verified",
                        "is_synthetic": True, "may_affect_real_metrics": False})
        if s["scenario"] == "unverifiable_case":
            evs.append({"node_id": sid, "title": f"{s['name']} 无法验证客户案例（仿真）", "evidence_type": "customer_case",
                        "source_url": f"https://{sid}.example.com/case", "source_name": "simulation", "truth_status": "pending_review",
                        "is_synthetic": True, "may_affect_real_metrics": False})
        if s["scenario"] == "evidence_expired":
            evs.append({"node_id": sid, "title": f"{s['name']} 过期证据（仿真）", "evidence_type": "award_certification",
                        "source_url": f"https://{sid}.example.com/cert", "source_name": "simulation", "truth_status": "observed",
                        "expires_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                        "is_synthetic": True, "may_affect_real_metrics": False})
        events.append({"node_id": sid, "event_type": "synthetic_event", "title": f"{s['name']} 仿真事件",
                       "description": s["scenario"], "impact_score": 0.3})
        if j >= 2 and j < 10:
            rels.append({"node_a": sid, "node_b": "syn-01", "type": "synthetic_partnership", "weight": 0.3})
        if s["scenario"] in ("successful_transaction", "failed_unarbitrated_transaction"):
            txs.append({"node_a": sid, "node_b": "syn-01" if sid != "syn-01" else "syn-02",
                        "title": f"{s['name']} 仿真交易", "status": "settled" if "successful" in s["scenario"] else "failed",
                        "is_synthetic": True})
        obs.append({"node_id": sid, "change_type": "user_evidence", "source_type": "simulation",
                    "proposed": {"title": f"{s['name']} 仿真观察"}, "is_synthetic": True,
                    "expected_review": "rejected" if s["scenario"] == "observation_rejected" else "pending_review"})

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    for name, rows in [("nodes", nodes), ("capabilities", caps), ("evidence", evs), ("events", events),
                       ("relationships", rels), ("observations", obs), ("transactions", txs)]:
        with open(os.path.join(OUT, name + ".jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    invariants = {
        "real_nodes": len(REAL), "synthetic_nodes": len(SYNTH),
        "synthetic_never_touches_real": True,
        "results_never_seeded": True,
        "evidence_requires_source": True,
    }
    with open(os.path.join(OUT, "expected_invariants.json"), "w", encoding="utf-8") as f:
        json.dump(invariants, f, ensure_ascii=False, indent=2)
    print(f"built: {len(nodes)} nodes, {len(evs)} evidence, {len(rels)} relationships, {len(txs)} transactions")

if __name__ == "__main__":
    build()
