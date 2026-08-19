---
status: audit
authority: implementation
version: v0.1
last_review: 2026-08-01
role: C6.2 pre-development auth reuse matrix
---

# C6.2 认证能力复用矩阵
> **历史/实现记录（2026-08-11 归档标注）**：本文档为恒域世界 V10.6 之前的演进记录，仅用于理解历史设计与已实现能力；发生冲突时以 V10.6 上位架构为准（docs/恒域世界_V10.6_四阶段演进架构总纲_含参考平台.md、docs/17-2_恒域世界_V10.6_整体重构_细节设计方案.md）。

| C6.2 需求 | 现有能力 | 复用 | 缺口 |
|---|---|---|---|
| 用户身份 | User（email/password_hash/role/tenant_id） | ✅ | 无 |
| 密码哈希 | bcrypt（passlib） | ✅ | 无 |
| Access Token | JWT + SECRET_KEY + ACCESS_TOKEN_EXPIRE_MINUTES | ✅ | 无 |
| 登录 | POST /auth/login | ✅ | 无 refresh/logout/me |
| 当前用户 | deps.get_current_user（HTTPBearer） | ✅ | 无角色校验依赖 |
| 平台角色 | User.role: admin/enterprise/... | ⚠️ | 需 REVIEWER |
| 节点角色 | 无 | ❌ | NodeMembership 表 |
| 用户-公司关系 | Company.owner_id（FK users.id） | ⚠️ | 单 owner；需 membership |
| Onboarding 用户绑定 | OnboardingSession 无 user_id | ❌ | 加 user_id 列 |
| 权限配置 | 无 | ❌ | access_control.yaml |
| 审计日志 | 无 | ❌ | AuditLog 表 |
| 交易 actor | Transaction actor_id 客户端提交 | ❌ | 改为服务端身份 |
