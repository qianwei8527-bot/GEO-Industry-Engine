---
status: audit
authority: implementation
version: v0.1
last_review: 2026-08-01
role: C6.5 pre-development reuse matrix
---

# C6.5 复用矩阵
> **历史/实现记录（2026-08-11 归档标注）**：本文档为恒域世界 V10.6 之前的演进记录，仅用于理解历史设计与已实现能力；发生冲突时以 V10.6 上位架构为准（docs/恒域世界_V10.6_四阶段演进架构总纲_含参考平台.md、docs/17-2_恒域世界_V10.6_整体重构_细节设计方案.md）。

| 需求 | 现有组件 | 复用 | 说明 |
|---|---|---|---|
| 机构身份 | Company/Entity + IdentityProfile + Onboarding | ✅ | 经 service 导入 |
| 能力 | Capability | ✅ | 经 LearningLoop/直接 service |
| 证据 | Evidence | ✅ | 含 source_name/url/occurred_at |
| 事件 | GeoEvent | ✅ | append-only |
| 快照 | NodeSnapshot | ✅ | 引擎派生写入 |
| 外部来源 | ObservationSource/Run/Artifact | ✅ | 不建第二套采集 |
| 变化审核 | CandidateChange + AuditLog + LearningLoop | ✅ | 不建第二套 |
| 关系 | Relationship | ✅ | C5.2 经 service |
| 交易 | TransactionEngine | ✅ | 仅仿真节点 |
| 信誉事实 | reputation_events + ReputationEngine | ✅ | DB 事实源 |
| AI 回答隔离 | AIAnswerArtifact.data_origin | ✅ | fake 不混 real |
| 数据标识 | data_origin/truth_status | ⚠️ | 需最小扩展：evidence 无 truth_status/is_synthetic/may_affect_real_metrics |

决策：
1. 不建第二套采集/Evidence/Event/Relationship
2. 导入统一走 service（Onboarding/LearningLoop/Governance/ExternalObservation）
3. Position/Reputation/Possibility/Connection 由引擎计算，不写种子结果
4. migration：Evidence 加 truth_status/is_synthetic/may_affect_real_metrics（明确缺口）
