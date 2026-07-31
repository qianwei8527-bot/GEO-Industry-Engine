---
status: draft
authority: design
version: v0.1
last_review: 2026-07-31
parent: 09_GEO_Universe_Relationship_Lifecycle.md
role: design document — not implementation

governance_tier: Frozen Design
precedes:
  - C6 Transaction / Marketplace
interfaces_with:
  - C4 Future Connection Engine
  - C5.1 Reputation Engine
  - C5.2 Relationship Lifecycle Engine
  - Context Engine
  - Possibility Graph
---

# GEO Universe Relationship Intelligence Engine — 关系智能引擎

> C4 回答“可能连接谁”。
> C5.1 回答“谁值得信任”。
> C5.2 回答“关系如何成长”。
> C5.3 回答“为什么这个连接值得发生”。
>
> 这是交易发生前的智能层。把 Connection Candidate 升级为 Relationship Opportunity。

---

## 第零章：文档定位

### 前置文档链

`
07_GEO_Universe_World_Engine.md          → 世界运行原理
08_GEO_Universe_Reputation_Engine.md     → 信任物理学
09_GEO_Universe_Relationship_Lifecycle.md → 关系生命周期
10_GEO_Universe_Relationship_Intelligence.md → 本文件：关系智能推演
`

### 本文档的职责

定义 Relationship Opportunity 的计算模型，以及 C4 → C5.2 → C5.3 的融合接口。将分散的能力模块闭合为统一的关系推荐链路。

---

## 第一章：关系智能第一性原理

### 1.1 一句话定义

> **Relationship Intelligence Engine 不是推荐系统。它是将 Node Context、Possibility Graph、Reputation 和 Relationship History 融合为一个问题的答案：为什么这两个节点应该建立关系？**

### 1.2 传统推荐 vs Universe 推演

**错（传统 B2B 推荐）：**

`
A需要 B → 标签匹配 → 推荐
`

不可解释。不可验证。不可追溯。

**对（Universe’）：**

`
Node A Context (我是谁，我在哪，我缺什么)
      +
Possibility Graph (A 未来可能去哪)
      +
Node B Context + Reputation (B 是谁，值得信任吗)
      +
Relationship History (A-B 之前合作过吗)
      +
Capability Gap Analysis (B 能填补 A 的缺口吗)
      =
Relationship Opportunity Report
`

### 1.3 三个核心问题

| 问题 | 来源 | 输出 |
|------|------|------|
| 为什么推荐他们合作？ | Context + Possibility | 能力互补分析 |
| 历史合作怎么样？ | C5.2 Relationship History | 关系信誉 + 成功率 |
| 失败风险是什么？ | Reputation + Gap | 风险信号列表 |

---

## 第二章：RelationshipOpportunity 数据模型

`yaml
RelationshipOpportunity:
  opportunity_id:       string
  node_a_id:            string
  node_b_id:            string

  # 为什么推荐
  reasons:
    capability_gap:     List[Dict]    # A缺什么，B有什么
    future_alignment:   float          # B能帮A达到未来状态吗
    reputation_match:   float          # 双方信誉兼容性

  # 历史合作
  existing_relationship: Optional[Dict]  # 是否已有关系
  relationship_stage:   string          # 当前阶段
  relationship_trust:   float           # 关系信誉

  # 预期价值
  expected_value:
    capability_gain:    float           # 能力提升预估 (0-1)
    growth_acceleration: float          # 成长加速 (0-1)
    strategic_value:    float           # 战略价值 (0-1)
    overall:            float           # 综合预期价值

  # 风险评估
  risks:
    reputation_risk:    List[str]       # 信誉风险
    capability_risk:    List[str]       # 能力风险
    relationship_risk:  List[str]       # 关系风险
    market_risk:        List[str]       # 市场风险

  # 建议行动
  recommended_action:   string          # 一句话建议
  next_steps:           List[Dict]      # 具体步骤

  confidence:           float           # 综合置信度 (0-1)
  generated_at:         datetime
`

---

## 第三章：C4 → C5.2 → C5.3 融合接口

### 3.1 升级后的连接链路

`
C4 Connection Engine
  discover_connections(node_id)
        |
        v
  ConnectionCandidate (初步筛选)
        |
        v
C5.3 Relationship Intelligence
  evaluate_opportunity(candidate)
        |
        |  查询 C5.1 Reputation
        |  查询 C5.2 Relationship History
        |  查询 Possibility Graph
        |  计算 Capability Gap
        |
        v
  RelationshipOpportunity (深度评估)
        |
        v
C5.2 Relationship Lifecycle
  create_relationship() → UNKNOWN
        |
        v
  State Machine → CONNECTED → ACTIVE → ...
`

### 3.2 RelationshipOpportunityScore

`
Opportunity Score =

  Capability Complementarity    × 0.30   (C4)
+ Future Path Alignment         × 0.20   (Possibility Graph)
+ Reputation Compatibility      × 0.20   (C5.1)
+ Relationship History Quality  × 0.15   (C5.2)
+ Strategic Value Potential     × 0.15   (C5.3 新增)
`

### 3.3 风险检测规则

`
IF candidate.reputation.status == "UNKNOWN":
    → risk: "insufficient_reputation_data"

IF existing_relationship AND existing_relationship.stage == "ENDED":
    → risk: "previous_relationship_ended", show reason

IF candidate.delivery_trust < 40:
    → risk: "low_delivery_trust"

IF relationship_history.failure_rate > 0.3:
    → risk: "high_historical_failure_rate"
`

---

## 第四章：最小版本范围 (C5.3 Scope)

### 4.1 后端

`
backend/app/universe/relationship_intelligence.py
`

- RelationshipOpportunity — 数据类
- OpportunityEvaluator — 评估器
- RelationshipIntelligenceEngine — 主引擎

### 4.2 API

`
POST /api/v1/universe/intelligence/evaluate
  输入: {node_a_id, node_b_id}
  输出: RelationshipOpportunity

GET  /api/v1/universe/intelligence/opportunities/{node_id}
  输出: 节点的所有关系机会
`

### 4.3 不进 C5.3

- UI 可视化 — 留 C5.4 Universe Home
- 交易闭环 — 留 C6

---

## 第五章：验收标准

### 输入

`
节点 A: 星辰AI营销科技
  Context:  Active Provider, Capability缺 Data
  Future:   180天进入 GEO Authority
  Reputation: Capability A, Delivery B+

候选 B: 某GEO数据服务商
  Context:  Established Provider
  Capability: Data Intelligence Lv4
  Reputation: Overall A, Delivery A
  History:   无

候选 C: 某低信誉服务商
  Reputation: UNKNOWN
`

### 输出

`
RelationshipOpportunity (A-B):
  reasons:
    capability_gap: “A缺 Data分析能力，B拥有 Data Lv4”
    future_alignment: 0.88
    reputation_match: 0.85

  expected_value: 0.82
  risks: [“缺少历史合作”]
  recommended_action: “建议建立初步合作关系，从小项目开始”
  confidence: 0.78

RelationshipOpportunity (A-C):
  reputation_match: 0.0
  risks: [“信誉数据不足”, “无法评估能力”]
  recommended_action: “建议等待更多信誉数据”
  confidence: 0.15
`

---

## 第六章：Universe First Law Check

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | **服务哪个节点？** | 服务于发起连接的节点，帮助它判断“为什么这个连接值得发生” |
| 2 | **帮节点解决什么问题？** | 从“可能连接谁”到“应该连接谁”的质变 |
| 3 | **增加了什么长期记忆？** | 每次机会评估结果可追溯，形成推荐历史 |
| 4 | **是否增强未来连接能力？** | 机会评估直接输入 C5.2 关系创建 |

---

> **冻结声明：** 本文档是 C5.3 的设计契约。实现时必须贯穿 C4 → C5.2 → C5.3 的融合链路，不得独立实现为另一个推荐系统。
