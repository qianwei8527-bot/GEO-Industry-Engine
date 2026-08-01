---
status: audit
authority: implementation
version: v0.1
last_review: 2026-08-01
role: C6.0 pre-development reuse matrix
---

# C6.0 复用矩阵 — Real Node Onboarding Audit

## 一、复用矩阵

| C6.0 需求 | 现有模型/API/服务 | 可直接复用 | 缺口 |
|---|---|---|---|
| 企业身份 | Company(Entity joined-inheritance) + IdentityProfile + /companies + /universe/identity/profile | ✅ | 无 |
| 行业赛道 | Industry + /industries（name/code/parent_id/level） | ✅ | 无 |
| 产品服务 | Company.business_scope + Capability | ⚠️ 部分 | 产品服务列表无独立模型，存 onboarding data_json + business_scope |
| 能力 | Capability（company_id/name/level/category/evidence_ids） | ✅ | 无 |
| 证据 | Evidence | ⚠️ 部分 | 缺 source_name / source_description / occurred_at → 最小加列（1 个 migration） |
| 目标方向 | NodeSnapshot + MemoryEngine | ✅ | 激活时写入快照与记忆 |
| 节点激活 | D0 验证脚本编排逻辑 | ✅（提取为 NodeActivationService） | 无 |
| 生命周期状态 | GrowthStage + Reputation + NodeSnapshot | ✅ | 激活时写入 |
| Home 跳转 | GET /universe/home/{type}/{id} | ✅ | 无 |
| 草稿保存 | 无 | ❌ | 新增最小 OnboardingSession 表（1 个 migration） |
| 激活幂等 | 无 | ❌ | OnboardingSession.idempotency_key 唯一约束 |

## 二、新增内容（最小集）

1. `OnboardingSession` 模型 + 1 个 migration
   - 表：onboarding_sessions（草稿 JSONB + 状态 + 幂等键）
   - evidence 加 3 列：source_name、source_description、occurred_at
2. `config/universe/onboarding.yaml`（步骤字段、必填、证据类型、阈值）
3. `NodeActivationService`（应用层编排，非新 Engine）
4. `POST/GET/PATCH .../onboarding/*` API
5. 前端 `/universe/join` 六步向导

## 三、不新增

- 不新增 Engine（复用 Context/Position/Reputation/Possibility/Connection/Memory）
- 不新增 Agent
- 不新增支付/会员/订单
- 不开发爬虫
- 不使用 Mock 数据
