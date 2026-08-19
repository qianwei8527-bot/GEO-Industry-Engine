---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C8.2 World State Engine
governance_tier: Implemented (prototype)
precedes:
  - C8.3 (待定)
interfaces_with:
  - WorldProjectionService
  - WorldStateSnapshot
  - WorldBinding / EvidenceClaim / DemandEvent / ConnectionCandidate
---

# GEO Universe World State Engine

> World State 是派生状态，不是新的 Universal Fact。

## 一、输入

```text
world_code
world_version
projection_as_of
state_scope
projection_manifest_hash
aggregation_rule_version
aggregation_config_hash
```

## 二、Scope 隔离

- production：只使用 verified production projection
- observation：verified + observed，单独统计
- simulation：允许 synthetic，仅测试

三种 Scope 不混合；simulation 不进入正式状态、趋势或真实指标。

## 三、状态维度

- Node：唯一节点数、角色分布
- Capability Supply：唯一 `entity + concept` 计数，多 Claim 不膨胀
- Demand：按 concept 聚合，verified 单独统计
- Evidence/Claim：verified Evidence、verified Claim、Binding 覆盖
- Connection：proposed / qualified / accepted / completed
- Outcome：pending / claimed / verified
- Unknown / Excluded：未映射、证据不足、Claim 不足、Truth 不足、Source Drift

## 四、结构性 Gap

- capability_gap：verified demand 无 verified supply
- trust_gap：潜在 supply 缺 verified Claim/Binding
- connection_gap：供需存在但无 production connection
- outcome_gap：completed 无 verified outcome Claim
- semantic_gap：事实存在但无法映射当前 World Concept

每个 Gap 包含 gap_type、concept_code、source_fact_ids、calculation_rule、excluded_reasons、state_scope。

## 五、禁止

- 不新增 World Score / Industry Health Score / Opportunity Score
- 不新增垂直 Reputation Score
- 不做供需价值排名
- 分母为零返回 null/not_applicable

## 六、快照

- 通用 `world_state_snapshots` 表，无行业专属表
- 快照发布后不可修改
- Fact 变化时标记 `stale`，生成新快照，不覆盖旧快照
- 相同规范化输入生成一致 snapshot hash

## 七、API

```text
POST /api/v1/universe/world-state/generate
GET  /api/v1/universe/world-state/snapshots
GET  /api/v1/universe/world-state/{snapshot_id}
GET  /api/v1/universe/world-state/{snapshot_id}/summary
GET  /api/v1/universe/world-state/{snapshot_id}/concepts/{concept_code}
GET  /api/v1/universe/world-state/{snapshot_id}/gaps
GET  /api/v1/universe/world-state/{snapshot_id}/unknown
GET  /api/v1/universe/world-state/{snapshot_id}/source-chain
GET  /api/v1/universe/world-state/{snapshot_id}/integrity
```

静态 `/snapshots` 在动态 `{snapshot_id}` 之前。

## 八、验证

- C8.2 定向测试：9/9 通过
- 后端全量回归：244 passed
- Migration：`c6g23a1b2c3d4_world_state_snapshot`
