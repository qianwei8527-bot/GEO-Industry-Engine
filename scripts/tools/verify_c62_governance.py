import json, urllib.request, urllib.error, uuid

API = "http://127.0.0.1:8080/api/v1"

def req(path, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def register(email, name, password="Test12345!"):
    return req("/auth/register", "POST", {"email": email, "password": password, "name": name})

# 1. Create three users
import time
suffix = uuid.uuid4().hex[:6]
admin_email = f"opc-admin-{suffix}@x.com"
owner_email = f"owner-{suffix}@x.com"
reviewer_email = f"reviewer-{suffix}@x.com"

_, a = register(admin_email, "OPC管理员")
_, o = register(owner_email, "企业所有者")
_, r = register(reviewer_email, "独立审核员")
admin_tok, owner_tok, reviewer_tok = a["access_token"], o["access_token"], r["access_token"]
print("users created:", admin_email, owner_email, reviewer_email)

# Promote admin + reviewer roles directly in DB via admin endpoint? Use direct SQL through API? Use /users? We'll do direct via backend import in a subprocess? Simpler: use the register response role is individual. We need admin/reviewer role.
# Update roles via direct DB (scripted below using service)
import asyncio, sys
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")
from sqlalchemy import select
from app.database import _get_session_factory
from app.models.user import User, UserRole

async def set_roles():
    factory = _get_session_factory()
    async with factory() as db:
        ua = (await db.execute(select(User).where(User.email == admin_email))).scalars().first()
        ur = (await db.execute(select(User).where(User.email == reviewer_email))).scalars().first()
        uo = (await db.execute(select(User).where(User.email == owner_email))).scalars().first()
        ua.role = UserRole.ADMIN
        ur.role = UserRole.REVIEWER
        await db.commit()
        print("roles set: admin", ua.id, "reviewer", ur.id, "owner", uo.id)
        return str(ua.id), str(ur.id), str(uo.id)
admin_id, reviewer_id, owner_id = asyncio.run(set_roles())

# 2. Owner creates onboarding session (auth required) and activates -> node_owner
code, s = req("/universe/onboarding", "POST", {"idempotency_key": f"c62-{suffix}", "company_name": f"治理验收企业{suffix}"}, owner_tok)
print("owner create session:", code, s.get("session_id")[:8] if isinstance(s, dict) and s.get("session_id") else s)
sid = s["session_id"]
data = {
    "company_name": f"治理验收企业{suffix}", "description": "C6.2 权限验收企业",
    "region": "上海", "company_size": "50-200人", "website": "https://gov.example.com",
    "industry_id": "ca076aa7-1bce-431a-b852-7e1a38381af6",
    "products": [{"name": "GEO服务", "core_capability": "AI优化"}],
    "evidence_items": [{"evidence_type": "official_website", "title": "官网", "source_url": "https://gov.example.com"}],
    "goal_30d": "验证治理", "goal_90d": "通过验收", "goal_180d": "稳定运行",
}
code, _ = req(f"/universe/onboarding/{sid}", "PATCH", {"data": data, "current_step": 6}, owner_tok)
code, act = req(f"/universe/onboarding/{sid}/activate", "POST", None, owner_tok)
print("activate:", code, act.get("activation_status"))
node_id = act.get("node_id")

# 3. Other user cannot read owner draft
code, _ = req(f"/universe/onboarding/{sid}", "GET", None, reviewer_tok)
print("reviewer read owner draft ->", code, "(expect 403)")

# 4. Owner submits evidence change
code, cc = req("/universe/observations", "POST", {
    "node_id": node_id, "change_type": "user_evidence",
    "evidence_summary": "新增行业认证证据", "proposed_value": {"title": "行业认证", "source_url": "https://cert.example.com", "evidence_type": "award_certification"},
}, owner_tok)
print("owner submit evidence ->", code, cc.get("review_status") if isinstance(cc, dict) else cc)
change_id = cc.get("id")

# 5. Owner cannot verify (no verify permission)
code, _ = req("/universe/observations", "POST", {
    "node_id": node_id, "change_type": "evidence_verification_change",
    "proposed_value": {"evidence_id": str(uuid.uuid4()), "verified_by": owner_id},
}, owner_tok)
print("owner try verify ->", code, "(expect 403)")

# 6. Owner cannot approve (not reviewer)
code, _ = req(f"/universe/changes/{change_id}/approve", "POST", {"actor": owner_id, "reason": "self"}, owner_tok)
print("owner approve ->", code, "(expect 403)")

# 7. Reviewer approves (server-side actor)
code, appr = req(f"/universe/changes/{change_id}/approve", "POST", {"reason": "证据来源可信"}, reviewer_tok)
print("reviewer approve ->", code, appr.get("review_status") if isinstance(appr, dict) else appr, "actor=", (appr.get("actor_id") or "")[:8] if isinstance(appr, dict) else "")

# 8. Admin applies (system only)
code, ap = req(f"/universe/changes/{change_id}/apply", "POST", None, admin_tok)
print("admin apply ->", code, ap.get("review_status") if isinstance(ap, dict) else ap)

# 9. Unauthorized no token
code, _ = req(f"/universe/changes/{change_id}", "GET")
print("no token read ->", code, "(expect 401)")

# 10. Home shows learning history with verifier
code, hist = req(f"/universe/nodes/{node_id}/learning-history", "GET", None, owner_tok)
print("owner learning history ->", code, len(hist.get("history", [])) if isinstance(hist, dict) else hist)
print("DONE")
