---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C7 Node Demand Intelligence - DemandEvent engine
governance_tier: Implemented (prototype)
precedes:
  - C7.4 Demand Driven Connection
  - C8 GEO Vertical World Model
interfaces_with:
  - DemandEvent
  - Capability
  - Evidence
  - Reputation
  - Universe Rules
---

# GEO Universe Demand Intelligence

> Demand 不是问答库，而是“为什么有人需要这个节点”的底层事件层。

## 一、第二条法则

- 第一法则：Universe 服务每个节点。
- 第二法则：**Demand creates Connection**。

连接不是因为两个节点存在关系，而是因为需求产生缺口，才寻找能力、形成连接、产生结果、沉淀信誉。

## 二、DemandEvent 模型

```text
actor_id / actor_type / actor_label
scenario / question_text
objective / pain / existing_solution
missing_capability
decision_stage
involved_nodes / mentioned_nodes / ai_answer_ids
matched_node_ids
final_behavior / outcome / impact_level / priority
source / truth_status / is_synthetic / may_affect_real_metrics
captured_at
```

边界：

- `synthetic` DemandEvent 不得影响真实节点。
- `observed` 只能作为线索，不进入正式基线。
- 只有 `verified` 需求可用于产品决策。

## 三、Demand Gap Analysis

```text
missing_capability
    ↓
Capability 匹配节点
    ↓
Evidence 覆盖（verified 优先）
    ↓
Reputation 覆盖
    ↓
coverage_score
    ↓
gap_score = 1 - max(coverage)
```

当前权重：

```text
verified/3     -> 0.6
evidence/10    -> 0.2
reputation/100 -> 0.2
```

## 四、API

```text
POST /api/v1/universe/demand/events
GET  /api/v1/universe/demand/events
POST /api/v1/universe/demand/events/{event_id}/analyze
```

- 创建事件：登录用户，actor 来自服务端会话。
- 分析：返回 matched_nodes 与 universe_rule。
- synthetic 创建时 `may_affect_real_metrics=false`。

## 五、验证

- 后端全量回归：213 passed
- C7 定向测试：5/5 通过
- Migration：`c6g16a1b2c3d4_demand_event`

## 六、C7.4 Demand Driven Connection

- 独立实体：`connection_candidates`，不复用 Marketplace Match。
- 评分链：Capability -> Evidence -> Reputation -> Trust -> Connection Value，权重来自 `config/universe/demand_connection.yaml`。
- 高分只表示 proposed connection，不表示官方推荐。
- accepted / completed 不直接改变 Reputation。
- synthetic DemandEvent 只能生成 synthetic Candidate，`may_affect_real_metrics=false`。
- observed 只作线索；正式决策（qualified / accepted / completed）要求 verified demand。

## 七、后续

- C7 数据接入：真实家长/企业问题，关联 AIAnswerArtifact 与行为结果。
