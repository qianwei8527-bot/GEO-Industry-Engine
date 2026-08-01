import json, sys, time
import urllib.request

API = "http://127.0.0.1:8080/api/v1/universe/onboarding"

def req(path, method="GET", body=None):
    url = API + path
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def onboard(name, desc, industry_id, products, evidence, goals):
    # 1. create session
    key = f"real-{name}-{int(time.time())}"
    s = req("", "POST", {"idempotency_key": key, "company_name": name})
    sid = s["session_id"]
    # 2. save all data
    data = {
        "company_name": name, "description": desc, "region": "上海",
        "company_size": "50-200人", "website": "https://example.com",
        "industry_id": industry_id,
        "products": products, "evidence_items": evidence,
        "goal_30d": goals[0], "goal_90d": goals[1], "goal_180d": goals[2],
        "self_positioning": desc,
    }
    req(f"/{sid}", "PATCH", {"data": data, "current_step": 6})
    # 3. validate
    v = req(f"/{sid}/validate", "POST")
    # 4. activate
    result = req(f"/{sid}/activate", "POST")
    return result

# Company 1: 星辰AI营销科技 (exists in DB)
r1 = onboard(
    "星辰AI营销科技",
    "专注GEO与AI搜索优化的营销科技服务商，服务3家世界500强企业",
    "6ad50f6d-b685-46c4-880b-6310fffae3b9",
    [
        {"name": "GEO内容优化", "core_capability": "AI内容优化", "product_type": "service"},
        {"name": "AI可见度分析", "core_capability": "数据分析", "product_type": "tool"},
        {"name": "企业AI知识库", "core_capability": "Agent开发", "product_type": "product"},
    ],
    [
        {"evidence_type": "official_website", "title": "官网服务展示", "source_url": "https://xingchen.example.com", "source_name": "官网"},
        {"evidence_type": "customer_case", "title": "3家世界500强客户案例", "source_url": "https://xingchen.example.com/cases", "source_name": "官网案例"},
        {"evidence_type": "award_certification", "title": "ISO27001认证", "source_url": "https://xingchen.example.com/iso", "source_name": "认证机构"},
        {"evidence_type": "ai_citation", "title": "被2个AI Agent引用", "source_url": "https://xingchen.example.com/ai", "source_name": "AI观测"},
    ],
    ["进入AI搜索优化Top20%", "获得GEO行业认证", "成为AI Agent服务商"],
)

# Company 2: 鼎新云计算 (new in companies table)
r2 = onboard(
    "鼎新云计算",
    "提供大规模AI算力基础设施与模型服务平台，服务金融与制造行业",
    "8ff67de9-5bbb-42e8-a3f1-bab1ca18db1a",
    [
        {"name": "AI算力租赁", "core_capability": "算力基础设施", "product_type": "infrastructure"},
        {"name": "模型部署平台", "core_capability": "模型服务", "product_type": "platform"},
    ],
    [
        {"evidence_type": "official_website", "title": "官网算力服务", "source_url": "https://dingxin.example.com", "source_name": "官网"},
        {"evidence_type": "customer_case", "title": "某银行AI项目", "source_url": "https://dingxin.example.com/bank", "source_name": "客户"},
    ],
    ["完成3个行业客户交付", "获得信创认证", "进入企业AI SaaS Top30%"],
)

# Company 3: 未来教育科技 (new in companies table)
r3 = onboard(
    "未来教育科技",
    "基于AI的自适应学习系统与教育数据分析服务商",
    "966c7908-22bd-4718-aff1-152b6cbc7246",
    [
        {"name": "AI自适应学习系统", "core_capability": "个性化学习", "product_type": "product"},
        {"name": "教育数据分析", "core_capability": "行为分析", "product_type": "service"},
    ],
    [
        {"evidence_type": "official_website", "title": "官网产品介绍", "source_url": "https://weilai.example.com", "source_name": "官网"},
    ],
    ["获得教育部AI教育试点", "覆盖100所合作学校", "成为教育AI领域标杆"],
)

print("=" * 60)
print("C6.0 REAL NODE ACCEPTANCE")
print("=" * 60)
for i, r in enumerate([r1, r2, r3], 1):
    print(f"\n--- Company {i}: {r.get('node_id')} status={r.get('activation_status')} ---")
    lc = r.get("lifecycle", {})
    for k, v in lc.items():
        st = v.get("status", "?")
        extra = ""
        if k == "position" and v.get("position"):
            p = v["position"]
            extra = f" stage={p.get('growth_stage')} rank={p.get('industry_rank')} rep={p.get('reputation_level')}"
        elif k == "reputation" and isinstance(v, dict) and "profile" in v:
            pr = v["profile"]
            extra = f" score={pr.get('overall_score')} level={pr.get('overall_level')}"
        elif k in ("possibility", "connection") and isinstance(v, dict):
            extra = f" detail={ {kk: vv for kk, vv in v.items() if kk != 'status'} }"
        print(f"  {k}: {st}{extra}")
    print(f"  data_quality={r.get('data_quality')}")
    print(f"  missing_evidence={r.get('missing_evidence')}")
    print(f"  home={r.get('home_url')}")

print("\nSUMMARY:", [r.get("activation_status") for r in [r1, r2, r3]])
