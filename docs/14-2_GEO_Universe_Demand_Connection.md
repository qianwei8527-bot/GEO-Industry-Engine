---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C7.4 Demand Driven Connection
governance_tier: Implemented (prototype)
precedes:
  - C8 GEO Vertical World Model
interfaces_with:
  - DemandEvent
  - Capability
  - Evidence
  - Reputation
  - Trust Foundation
---

# GEO Universe Demand Driven Connection

> 连接候选不是推荐；连接行为不等于信誉。

## 一、闭环

```text
Demand Event
  -> Gap Analysis
  -> Connection Candidate
  -> Trust Qualification
  -> Human/Rule Decision
  -> Connection Outcome
  -> Demand Event 回写
```

## 二、模型

`connection_candidates`：

- demand_event_id / source_node_id / target_node_id
- connection_type / matched_capabilities / evidence_ids
- capability_score / evidence_score / reputation_score / trust_score / connection_score
- explanation / rule_version / deduplication_hash
- truth_status / status / decision_source / may_affect_real_metrics / outcome
- decided_by / decision_reason / created_at / updated_at

## 三、评分链（C7.4-R 收口）

```text
capability_score = clamp(matched capability level, 0..1)
evidence_score   = clamp(verified_count / 3 * verified_weight, 0..1)
reputation_score = clamp(reputation.total_score / 100, 0..1)
trust_score      = clamp(evidence_score * 0.6 + reputation_score * 0.4, 0..1)
connection_score = clamp(capability*0.35 + evidence*0.25 + reputation*0.20 + trust*0.20, 0..1)
```

- 只有 verified Evidence 可提高 evidence/trust/connection 分数。
- observed/synthetic Evidence 只记录为 `observed_evidence_count` / `synthetic_evidence_count` 线索。
- 权重全部来自 `config/universe/demand_connection.yaml`（v1.1.0），Service 不硬编码。
- 每个候选固化 `rule_version`、`config_version`、`config_hash`、Evidence IDs 与全部评分分量。

## 四、边界

1. 缺口不是需求真相。
2. 高分不是推荐。
3. 连接不反向制造信誉。
4. synthetic 不进入真实世界。

状态机（C7.4-R）：

```text
proposed -> qualified -> accepted -> completed
proposed/qualified -> rejected
```

- verified + production：可 qualified/accepted/completed。
- observed：qualified 仅 internal/simulation；accepted/completed 仅 simulation。
- synthetic：全部正式流程仅 simulation，`may_affect_real_metrics=false`。
- accepted/completed 不调用 Reputation / Law。

truth_status 合成规则：

```text
synthetic = demand.synthetic OR demand.truth=synthetic OR target含synthetic evidence
verified  = demand.truth=verified AND target含verified evidence
observed  = 其余情况
```

## 五、API

```text
POST /api/v1/universe/demand/candidates/generate
GET  /api/v1/universe/demand/candidates
GET  /api/v1/universe/demand/candidates/{candidate_id}
POST /api/v1/universe/demand/candidates/{candidate_id}/decision
POST /api/v1/universe/demand/candidates/{candidate_id}/outcome
GET  /api/v1/universe/demand/candidates/boundary
```

## 六、验证

- C7.4 定向测试：5/5 通过
- 后端全量回归：213 passed
- Migration：`c6g17a1b2c3d4_demand_connection` + `c6g18a1b2c3d4_demand_connection_hardening`
- 数据库唯一约束：`UNIQUE(demand_event_id, target_node_id, connection_type)`
