---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C8.3 World State Transition Engine
governance_tier: Implemented (prototype)
precedes:
  - C8.4 (待定)
interfaces_with:
  - WorldStateSnapshot
  - WorldStateTransition
  - WorldStateService
---

# GEO Universe World State Transition

> 只检测两个可信状态之间的可证明变化，不预测趋势、不解释因果。

## 一、可比性门禁

正式 Transition 必须同时满足：

- world_code 相同
- world_version 相同（不同属于 model diff）
- state_scope 相同
- aggregation_rule_version 相同
- aggregation_config_hash 相同（不同属于 methodology change）
- from.as_of < to.as_of
- 两个快照内容完整且 hash 校验通过

不满足时返回 `non_comparable` 及明确原因。

## 二、变化类型

- projection_entity_added / removed
- role_binding_added / removed
- capability_supply_added / removed
- demand_added / updated / closed
- evidence_or_claim_verified / revoked_or_expired
- connection_status_changed
- outcome_claimed / verified / revoked
- gap_opened / persisted / resolved
- unknown_added / resolved
- excluded_added / resolved

“从投影中移除”只报告移除，不表述为节点退出行业。

## 三、Gap 生命周期

- capability_gap：只有 eligible verified supply 出现后解决
- trust_gap：只有结构化 Claim/Binding 验证后解决
- connection_gap：只有合规 production connection 出现后解决
- outcome_gap：只有 verified outcome Claim 出现后解决

completed Connection 本身不能解决 outcome_gap。

## 四、Source Drift

- 旧快照引用的 Fact 原地变化时标记 `historical_source_drift`
- Transition 只能生成诊断结果，不能发布为 fully auditable production transition
- stale 状态不修改原快照 payload 或 snapshot hash

## 五、Transition 持久化

- 通用不可变 `world_state_transitions` 表，无行业专属表
- 固化 from/to snapshot、兼容性、hash、rule/config、change manifest、transition hash
- 相同输入产生相同 transition hash，重复请求幂等

## 六、API

```text
POST /api/v1/universe/world-state/transitions/generate
GET  /api/v1/universe/world-state/transitions
GET  /api/v1/universe/world-state/transitions/compatibility
GET  /api/v1/universe/world-state/transitions/{transition_id}
GET  .../{transition_id}/changes
GET  .../{transition_id}/gaps
GET  .../{transition_id}/source-chain
GET  .../{transition_id}/integrity
```

## 七、禁止

不输出增长/衰退、趋势、因果、机会判断、推荐或任何 World/Opportunity/Trend Score。

## 八、验证

- C8.3 定向测试：6/6 通过
- 后端全量回归：250 passed
- Migration：`c6g24a1b2c3d4_world_state_transition`
