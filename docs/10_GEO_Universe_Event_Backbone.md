---
status: design
authority: architecture
version: v0.1
last_review: 2026-08-01
role: C6.6.5 Universe Event Backbone — design contract, not implementation
governance_tier: Frozen Design
precedes:
  - C6.7 Law Engine
  - C6.8 Living World Model
  - C6.9 Ecosystem Graph
interfaces_with:
  - Universe Registry / Node / Memory / Reputation / Relationship / Transaction / Learning Loop
---

# GEO Universe Event Backbone — 统一事件时空设计

> 目标：让所有领域事件进入同一个时空，使 Universe 能够回答
> "世界发生过什么、为什么、由什么规则驱动、如何改变节点状态"，
> 并且服务器重启后不会失忆、不会自相矛盾。

---

## 一、问题定义

当前事件分散在多个"领域专属"存储中：

| 事件源 | 现有存储 | 持久化 | 可统一查询 |
|---|---|---|---|
| ReputationEvent | reputation_events 表 | ✅ | 需单独查询 |
| GeoEvent | geo_events 表 | ✅ | 需单独查询 |
| TransactionEvent | transaction_events 表 | ✅ | 需单独查询 |
| CandidateChangeAudit | candidate_change_audits 表 | ✅ | 需单独查询 |
| RelationshipEvent | RelationshipEventStore（内存） | ❌ | 需单独查询 |
| MemoryFact / MemoryEvent | MemoryEngine（内存） | ❌ | 需单独查询 |
| Event ORM（通用） | events 表 | ✅ | 需单独查询 |

**缺口不是"没有记忆"，而是记忆没有统一时空。**

---

## 二、UniverseEvent 统一模型（设计）

### 2.1 核心事件结构

```yaml
UniverseEvent:
  event_id: string            # 全局唯一（领域事件可复用其 id）
  node_id: string             # 主节点
  related_node_ids: [string]  # 关联节点（影响网络）
  domain: string              # reputation | relationship | observation | transaction | memory | governance | system
  event_type: string          # 保留领域原类型（如 certification_passed / collaboration_completed）
  occurred_at: datetime       # 世界时间（不可变）
  recorded_at: datetime       # 入簿时间
  actor_id: string            # 服务端身份（C6.2 后不可客户端伪造）
  source: string              # event | api | observation | rule_engine | user | system
  rule_ids: [string]          # 触发本事件的规则（若有）
  payload: object             # 领域原始载荷（保留完整）
  state_delta: object         # 期望的节点状态变化（可选，由 Rule 计算）
  version: int                # 幂等 / 并发
  causality: string           # parent_event_id 或 correlation_id（原因链）
```

### 2.2 设计原则

1. **Event 是事实，State 是投影。** 数据库不保存"最终分数"作为唯一真相；保存事件，Position/Reputation/Growth 由投影重建。
2. **领域事件保留，不删除、不重写。** Event Backbone 是统一视图 + 统一索引，不替换领域表。
3. **幂等写入。** `(event_id)` 唯一；同一事件重复投递不产生副作用。
4. **因果链。** `causality.correlation_id` 串联 Observation → Evidence → CandidateChange → Apply → Reputation 的完整链路。
5. **Rule 驱动。** Event 进入 Rule Engine，规则产生 `state_delta`，State 投影应用 delta；禁止 Engine 内散落 `if xxx: score += y`。

---

## 三、领域 Event 如何纳入统一时空

### 3.1 三种集成方式（按优先级）

1. **视图投影（推荐首版）**：不新增物理表，`UniverseEventView` 查询各领域表 → 归一化为统一结构。零迁移，立即获得统一时间线。
2. **统一索引表（v2）**：新增 `universe_events` 索引表（event_id、node_id、domain、type、occurred_at、correlation_id、source_table、source_id），各领域写入时同步插入索引；历史数据迁移回填。
3. **事件总线（v3）**：写入即广播到 Rule Engine / 投影器 / 通知，统一表成为主事实源（Event Sourcing 方向）。

### 3.2 领域事件映射表

| 领域事件 | 统一 domain | 统一 event_type | node_id 来源 | 持久化 |
|---|---|---|---|---|
| reputation_events.event_type | reputation | 同左 | node_id | ✅ DB |
| geo_events.event_type | observation | 同左 | source_node_id | ✅ DB |
| transaction_events.event_type | transaction | 同左 | 从 transaction.node_a/b 解析 | ✅ DB |
| candidate_change_audits.to_status | governance | change_{from}->{to} | change.node_id | ✅ DB |
| relationship event_type | relationship | 同左 | rel.node_a/b | ❌ 内存（待补） |
| memory fact.category | memory | memory_fact | node_id | ❌ 内存（待补） |
| events(event ORM).event_type | general | 同左 | entity_id | ✅ DB |

---

## 四、时间线如何查询

### 4.1 统一 Timeline Query（设计）

```
GET /universe/memory/timeline/{node_id}?domains=&from=&to=&types=
```

返回（已由 C6.6 MemoryUniverseService 原型验证）：

```json
{
  "node_id": "…",
  "count": 42,
  "timeline": [
    {"ts": "2026-03-01T…", "domain": "reputation", "type": "certification_passed",
     "title": "…", "description": "…", "source": "reputation_event",
     "correlation_id": "…", "rule_ids": ["R04"]}
  ]
}
```

### 4.2 索引维度

- `(node_id, occurred_at)`：节点全历史
- `(domain, event_type)`：世界级统计
- `(correlation_id)`：因果链回放
- `(rule_ids)`：规则影响审计

---

## 五、如何驱动 Rule（Law Layer 前置契约）

### 5.1 事件 → 规则评估 → 状态变化

```
UniverseEvent
    ↓
Rule Engine（C6.7）
    ↓ 匹配 event_type / domain / node_type
Rule Evaluation
    ↓
State Delta（示例）
  { node_id, dimension: "trust", delta: +8, reason: "certification_passed", rule_id: "R09" }
    ↓
State Projection（Reputation / Position / Growth）
    ↓ 追加 Memory
    ↓ 触发下游 Event（可选，因果链延续）
```

### 5.2 规则不可变性

- Rules 与权重只允许通过治理流程修改（system_admin + 审计），任何 Event 不得自动改变规则。
- 每次 State 投影必须记录 `rule_ids` 与 `calculation_version`，支持"为什么是这个分数"。

---

## 六、如何影响 Node State

### 6.1 状态投影模型

```
Node State = f(UniverseEvents × 当前 Rules × 时间衰减)
```

- **Reputation**：ReputationEvent 投影（现有 ReputationEngine，DB 事实源）
- **Position**：PositionEngine 从 State 输入计算（行业排名/能力/增长/影响）
- **Growth**：GrowthStage 从 Evidence/Event 演化
- **Memory**：MemoryFact/MemoryEvent 为事件语义层（故事）
- **Relationship**：RelationshipEvent 投影关系信誉

### 6.2 一致性要求

- 重启后：从 DB 事件重建 State（Reputation 已支持 restore；Relationship/Memory 待补）
- 幂等重放：同一事件集 + 同一规则版本 → 同一 State
- 禁止内存 State 覆盖 DB 事实源

---

## 七、与 Node Demand First 的关系

Event Backbone 是 Universe Core 基础设施；Node Demand First 是准入宪章。
需求（DemandEvent）未来作为 `domain: demand` 的事件进入同一时空，但不改变本设计：

> 先把世界建起来，再让真实需求进入这个世界。

---

## 八、实施顺序建议（供 C6.6.5 后续）

1. **P0**：统一时间线视图（已有 C6.6 原型，扩 domains 覆盖 Relationship/Memory）
2. **P0**：RelationshipEvent / MemoryFact 持久化（见持久化审计）
3. **P1**：`universe_events` 索引表 + 历史回填
4. **P1**：Rule Engine 消费 Event（C6.7 前置）
5. **P2**：事件总线 / 因果链自动生成

> **冻结声明：** 本文档是 Event Backbone 设计契约。实现时禁止删除领域事件、禁止把分数作为唯一真相、禁止 Engine 内散落规则判断。
