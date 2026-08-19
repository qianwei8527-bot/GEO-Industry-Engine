---
status: audit_complete
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.10.5 Universe Integrity Audit - node value acceptance
precedes:
  - C7 Node Demand Intelligence
---

# C6.10 Universe Alpha 节点价值验收报告

> 审计目标：验证一个真实节点进入 Universe 后，是否获得“进入前无法获得”的认知与决策信息。
> 审计方式：DB 数据核对 + `/api/v1/universe/node/company/{id}/home` 聚合结果核验。

---

## 一、受审计节点

| 项目 | 值 |
|---|---|
| 节点名称 | 龙腾AI科技 |
| 节点 ID | c9da900b-1715-4d7f-8982-80f7b5c42451 |
| 类型 | company |
| 描述 | 行业龙头企业，GEO综合评分最高，拥有完整的AI可见度优化体系 |
| GEO Score | 59 |

## 二、数据快照

| 层 | 数量 | 状态 |
|---|---|---|
| Evidence | 20 | 全部 `observed`，0 synthetic |
| Verified Evidence | 0 | 尚未形成可信事实层 |
| Capability | 6 | 已关联 |
| Relationship | 5 | 3 cooperation / 2 competition |
| Reputation Event | 4 | 已持久化 |
| GeoEvent | 233 | 已入库 |
| NodeSnapshot | 82 | 已入库 |
| KnowledgeCandidate | 19 | 18 adopted / 1 observed，0 synthetic |
| AI Answer Artifact | 1200 | 全部 `fake`，0 baseline_eligible |
| Future State | 6 | 可投影 |
| Connection Need | 7 | 可投影 |
| Connection Candidate | 10 | 可投影 |

## 三、节点闭环检查

1. 身份：PASS，`龙腾AI科技` + entity_type 完整。
2. 证据：PASS（数量），但全部为 observed，缺 verified。
3. 记忆：PARTIAL，DB 有 82 个 snapshot / 233 个事件，但 Home 内存 timeline facts 为 0，MemoryEngine 持久化仍未完整接入 Home。
4. 位置：PASS，growth_stage=reputation、industry_rank=0.7、reputation_level=E。
5. 关系：PASS，5 条关系可投影。
6. 未来：PASS，6 个未来状态 + 7 个连接需求。
7. 机会：PASS，10 个连接候选。

结论：节点闭环骨架成立，但“可信证据→信誉”尚未形成强闭环。

## 四、时间闭环检查

- 过去：82 个 snapshot、233 个 GeoEvent。
- 原因：4 个 Reputation Event 可投影 causality chain。
- 影响：关系、位置、信誉状态可读。
- 变化：信誉 E、阶段 reputation。
- 未来：6 个未来状态、7 个连接需求、10 个候选。

时间链结构 PASS；时间深度 PARTIAL：当前事件时间戳集中在同一日期，尚未形成真实 180 天演化证据。

## 五、真实性边界检查

| 边界 | 结果 |
|---|---|
| observed 不自动成为 verified | PASS |
| synthetic 不进入真实节点信誉 | PASS（0 synthetic） |
| Fake AI Answer 不进 baseline | PASS（1200 fake，0 eligible） |
| observed 不直接提升信誉 | PASS（当前无 verified 事件，信誉未由 observed 提升） |
| failed transaction 不扣真实信誉 | PASS（既有 C6-T1 回归覆盖） |

## 六、节点价值验收

### 1. 进入前知道什么

企业名称、行业、描述、GEO Score、6 个能力、5 条关系、20 条 observed 证据。

### 2. 进入后新增什么认知

- 行业位置：Top 70%，低于中位数。
- 信誉状态：E，增长阶段已到 reputation 但可信证据不足。
- 因果链：4 个信誉事件的演化原因。
- 未来路径：6 个状态、7 个连接需求。
- 下一步：10 个连接候选。

### 3. 哪些信息以前无法获得

- 行业相对位置。
- 未来 30/90/180 天状态投影。
- 能力/信誉缺口与连接需求。
- 关系网络的结构化投影。
- AI 可见度基线状态（当前仅 fake，隔离正确）。

### 4. 哪些决策因此改变

- 应优先补齐 verified Evidence，而不是继续堆积 observed 数据。
- 应围绕 7 个连接需求选择下一步合作。
- 应处理竞争力短板：2 条 competition 关系已进入视野。
- 应把未来状态作为内容/认证投入顺序的依据。

### 5. 哪些功能值得继续建设

| 优先级 | 事项 | 原因 |
|---|---|---|
| P0 | Evidence verification 工作流 | 当前 20 条证据全部 observed，信誉无法真正建立 |
| P0 | MemoryEngine 接入 Home timeline | 当前 82 snapshot 未反映到 Home 故事层 |
| P1 | 真实 AI Observation | 当前 1200 条全部 fake，可见度基线不可用 |
| P1 | 关系元数据与 stage | 当前 DB 关系无 stage/trust 深度 |
| P2 | 时间深度 | 当前事件集中同一天，无法支持 180 天演化叙事 |

## 七、审计结论

- Universe Core Alpha：PASS。
- 节点价值入口：PASS，节点进入后确实获得新增认知与决策依据。
- 真实性边界：PASS。
- 可信事实层：PARTIAL，verified=0 是当前最大短板。
- 时间演化层：PARTIAL，结构完整但时间深度不足。

## 八、C7 准入建议

可以进入 C7 Demand Intelligence，但建议把以下两件事作为 C7 的并行前提：

1. 先让现有节点至少完成 1 条 verified Evidence，验证“审核→信誉→Home 变化”完整闭环。
2. 不要把 C7 做成问题数据库，必须保持 Demand Event → Node → Capability → Evidence → Outcome 的可追溯链路。
