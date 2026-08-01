"""C6.3 Gate 0: durable refresh token revocation, rotation, family reuse, role grant."""
import sys, uuid, time
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import httpx

BASE = "http://127.0.0.1:8080/api/v1"


def reg(c, email, name):
    return c.post(BASE + "/auth/register", json={"email": email, "password": "Test12345!", "name": name}).json()


class TestRefreshTokenGate0:
    def setup_method(self):
        self.c = httpx.Client(base_url=BASE, timeout=10)
        self.suffix = uuid.uuid4().hex[:6]

    def teardown_method(self):
        self.c.close()

    def test_rotation_and_reuse_revokes_family(self):
        email = "rot-" + self.suffix + "@x.com"
        r = reg(self.c, email, "旋转测试")
        rt1 = r["refresh_token"]
        resp = self.c.post("/auth/refresh", json={"refresh_token": rt1})
        assert resp.status_code == 200, resp.text
        rt2 = resp.json()["refresh_token"]
        assert rt2 != rt1
        resp1 = self.c.post("/auth/refresh", json={"refresh_token": rt1})
        assert resp1.status_code == 401
        resp2 = self.c.post("/auth/refresh", json={"refresh_token": rt2})
        assert resp2.status_code == 401

    def test_logout_durable_after_refresh(self):
        email = "log-" + self.suffix + "@x.com"
        r = reg(self.c, email, "登出测试")
        at = r["access_token"]; rt = r["refresh_token"]
        out = self.c.post("/auth/logout", json={"refresh_token": rt}, headers={"Authorization": "Bearer " + at})
        assert out.status_code == 200
        resp = self.c.post("/auth/refresh", json={"refresh_token": rt})
        assert resp.status_code == 401

    def test_non_admin_cannot_grant_role(self):
        email = "plain-" + self.suffix + "@x.com"
        r = reg(self.c, email, "普通用户")
        target = reg(self.c, "tgt-" + self.suffix + "@x.com", "目标用户")
        tid = target["user"]["id"]
        resp = self.c.patch("/auth/users/" + tid + "/role",
                            json={"role": "reviewer"}, headers={"Authorization": "Bearer " + r["access_token"]})
        assert resp.status_code == 403