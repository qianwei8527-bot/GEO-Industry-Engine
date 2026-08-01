---
status: audit
authority: implementation
version: v0.1
last_review: 2026-08-01
role: C6.1 pre-development reuse matrix
---

# C6.1 复用矩阵 — Continuous Learning Loop

| C6.1 需求 | 现有组件 | 直接复用 | 缺口 |
|---|---|---|---|
| Observation 接收 | /api/v1/observation/ingest + CandidateChange | ⚠️ | 面向新概念信号；需节点级 node_id 输入 |
| Candidate Change | candidate_changes 表 | ⚠️ | 缺 node_id/before/proposed/impact/dedup_hash/affected_engines/applicable_rules/review_status/actor |
| KnowledgeCandidate | knowledge_candidates 表 | ✅（概念层保留） | 无 |
| Evidence | evidence 表 | ✅ | 无 |
| GeoEvent | geo_events 表 | ✅ | 无 |
| NodeSnapshot | node_snapshots 表 | ✅ | 无 |
| Memory | MemoryEngine | ✅ | 无 |
| Event Store | app/domain/event_store.py（内存） | ⚠️ | 非持久化；用 GeoEvent 持久化 |
| Reputation Event | ReputationEngine（内存 EventStore） | ❌ | 无持久化表；需 reputation_events 表 + DB 恢复/rebuild |
| 调度 | 无 APScheduler（仅 celery） | - | 本阶段事件驱动，不新增 |
| 审核策略 | 无 | ❌ | learning.yaml 配置 |
| 数据质量 | NodeActivationService._data_quality 单一分数 | ❌ | 拆六维 + 权重配置 |

## 决策

1. 扩展现有 candidate_changes 表（1 个 migration 加列），不新建另一套 Change 模型
2. 新增 reputation_events 表（信誉事实来源持久化）
3. 新增 config/universe/learning.yaml（审核/去重/影响映射/时间窗/数据质量权重）
4. LearningLoopService 为应用编排服务（非 Engine）
