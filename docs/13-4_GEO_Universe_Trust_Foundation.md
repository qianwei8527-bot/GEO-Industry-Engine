---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.11 Trust Foundation - evidence verification + trust boundary
precedes:
  - C7 Node Demand Intelligence
interfaces_with:
  - Evidence
  - Learning Loop
  - Law Engine
  - Reputation Engine
  - Universe Home
  - Trust Boundary Dashboard
---

# GEO Universe Trust Foundation

> 目标：让 Universe 第一次拥有“经过验证的节点事实”，而不是只有 observed 声明。

---

## 一、验证链路

```text
Evidence
  ↓
verification_method
verification_result
  ↓
verified_by / verified_at
  ↓
Law Mutation
  ↓
Reputation Event
  ↓
Position / Story / Home 变化
```

## 二、Evidence 扩展字段

| 字段 | 说明 |
|---|---|
| verification_method | 验证方式，例如 `governance_review` / `universe_record_crosscheck` |
| verification_result | 验证结论，例如 `approved` / `rejected` |
| verified_by | 服务端审核者 UUID |
| verified_at | 验证时间 |

Migration：`c6g15a1b2c3d4_trust_foundation`。

## 三、API

```text
POST /api/v1/universe/trust/evidence/{evidence_id}/verify
POST /api/v1/universe/trust/nodes/{node_id}/law-mutation
GET  /api/v1/universe/trust/boundary/{node_id}
```

- 验证证据：reviewer/admin。
- Law Mutation：system_admin。
- Boundary：只读。

## 四、Trust Boundary Dashboard

- 路由：`/universe/trust`
- 展示：Verified Facts / Observed Facts / Synthetic Data / Unknown
- 同时展示 AI Answer fake/real 与 baseline eligibility

## 五、沙箱验证结果（龙腾AI科技）

本次在现有沙箱完成：

- 5 条 Universe 内部可交叉核对事实已标记 verified（方法：`universe_record_crosscheck`）
- 1 次 Law Mutation：`certification_trust_growth`
- Reputation Event 已持久化
- Universe Home 因果链已出现 Law 事件
- Home 信誉面板从空变为 `DEVELOPING / E / 19.9 / 7 events`

明确边界：

- 这是沙箱治理验证，不是外部网络核验。
- 真实世界 verified 仍依赖 C6.5-O 网络抓取与人工审核，本轮未伪造。

## 六、Home 顺序修复

- UniverseHomeService 先恢复 Reputation，再投影 Ecosystem Graph。
- 修复后重启服务因果链不再为空。

## 七、验证

- 后端全量回归：200 passed
- 前端 tsc：通过
- 前端 production build：通过
- Trust 页面：`/universe/trust` 返回 200
