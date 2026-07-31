---
status: draft
authority: design
version: v0.1
last_review: 2026-07-31
parent: 08_GEO_Universe_Reputation_Engine.md
role: design document — not implementation

governance_tier: Frozen Design — implementation must trace to this document
precedes:
  - C6 Transaction / Marketplace
interfaces_with:
  - C4 Future Connection Engine
  - C5.1 Reputation Engine
  - Context Engine
---

# GEO Universe Relationship Lifecycle — 关系生命周期

> C5.1 Reputation Engine 回答了“谁值得被信任”。
> C5.2 Relationship Lifecycle 回答“信任如何在节点之间形成”。
>
> 前面所有工作都在定义“个体生命”（Node）。
> 本文档开始定义“社会结构”（Relationship）。
>
> 这一步决定 GEO Universe 是数据库，还是一个真正的产业社会模拟系统。

---

## 第零章：文档定位

### 前置文档链

`
00_GEO_Universe_第一性原理.md  → 为什么 Universe 存在
01_GEO_Universe_产品哲学.md    → Universe 相信什么
02_Universe_世界规则.md        → 世界的基本规律
07_GEO_Universe_World_Engine.md → 世界如何运转
08_GEO_Universe_Reputation_Engine.md → 信任如何建立
09_GEO_Universe_Relationship_Lifecycle.md → 本文件：关系如何生长
`

### 本文档的职责

定义节点间关系的完整生命周期，从陌生到合作到信任到生态联盟。关系不是一条边，而是一个拥有自己历史、信誉和生命的实体。

---

## 第一章：关系第一性原理

### 1.1 一句话定义

> **Relationship 不是一条边，而是一段拥有自己历史、信誉和生命的关系实体。**

### 1.2 传统模型 vs Universe 模型

**错（传统图数据库）：**

`
Company A —— partner —— Company B
`

一条边。没有历史，没有信誉，没有生命。

**对（GEO Universe）：**

`
Relationship: A↔B

  Stage:     Collaborating
  Since:     2025-03
  Events:    12 interactions, 3 projects, 1 dispute resolved
  Trust:     B+ (77)
  Reputation: Relationship-specific: Delivery A, Communication B

  History:
    2025-03  Discovered via C4 Connection Engine
    2025-04  First contact → Introduction
    2025-05  First collaboration project
    2025-08  Project success + mutual endorsement
    2026-01  Second project, expanded scope
    2026-06  Strategic partnership discussion
`

### 1.3 关系也有信誉

这是 C5.2 最关键的设计决定：

`
Node A Reputation:  90  (企业本身信誉很高)
Node B Reputation:  85  (合作伙伴信誉也高)

But A↔B Relationship Trust:  55  (他们之间合作过 3 次，2 次失败)

结论：两个高信誉企业，不等于他们的关系信誉高。
`

**Relationship Reputation ≠ Node Reputation。** 这是必须锁死的。

### 1.4 关系不可删除

`
Relationship 一旦创建，不可删除。
可以终止（terminated），但历史保留。
这符合 Event Store 原则。
`

---

## 第二章：关系状态机

### 2.1 七阶段生命周期

`
                    DISCOVERY
                   发现
                       |
                       v
                  INTRODUCTION
                   初次接触
                       |
                       v
                  INTERACTION
                   互动
                       |
                       v
                 COLLABORATION
                   合作
                       |
                       v
                   EVIDENCE
                 产生证据
                       |
                       v
                    TRUST
                 形成信誉
                       |
                       v
                   ALLIANCE
                 生态联盟
`

### 2.2 各阶段定义

| 阶段 | 含义 | 触发条件 | 信誉门槛 |
|------|------|-------------|-----------|
| **DISCOVERY** | 被 C4 Connection Engine 发现为候选 | 未来路径匹配 + Reputation 满足最低门槛 | - |
| **INTRODUCTION** | 双方建立初次接触 | 一方发起请求，另一方确认 | - |
| **INTERACTION** | 正式互动（沟通、谈判、试点） | 双方均已确认 | - |
| **COLLABORATION** | 实质性合作开始 | 第一个项目/交易启动 | - |
| **EVIDENCE** | 合作产生了可验证的结果 | 项目完成 + 双方反馈 | 至少 1 个正面结果 |
| **TRUST** | 关系信誉已建立 | ≥3 个成功合作 + 双方信誉均达标 | Node Reputation 均≥ 60 |
| **ALLIANCE** | 战略性生态关系 | 长期合作 + 共同发展 + 双向推荐 | Node Reputation ≥ 80, Relationship Trust ≥ 70 |

### 2.3 状态跃迁规则

`python
# 只能向前，不能跳级
valid_transitions = {
    "DISCOVERY":    ["INTRODUCTION", "DISCOVERY"],     # 可以停留在发现阶段
    "INTRODUCTION": ["INTERACTION", "DISCOVERY"],      # 可以回退到发现
    "INTERACTION":  ["COLLABORATION", "DISCOVERY"],    # 无法合作则回退
    "COLLABORATION":["EVIDENCE", "INTERACTION"],       # 合作失败回到互动
    "EVIDENCE":     ["TRUST", "COLLABORATION"],        # 证据不足回到合作
    "TRUST":        ["ALLIANCE", "EVIDENCE"],          # 信任降低回到证据
    "ALLIANCE":     ["TRUST"],                         # 联盟破裂回到信任
}

# 终止状态（任何阶段均可触发）
TERMINATED = "TERMINATED"  # 关系结束，历史保留
`

---

## 第三章：核心数据模型

### 3.1 Relationship

`yaml
Relationship:
  relationship_id:   string          # 唯一 ID
  node_a_id:         string          # 主动方
  node_a_type:       string
  node_b_id:         string          # 被动方
  node_b_type:       string

  relationship_type: string          # partnership | client_vendor | strategic | ecosystem | mentor | investor

  stage:             enum            # DISCOVERY | INTRODUCTION | INTERACTION | COLLABORATION | EVIDENCE | TRUST | ALLIANCE | TERMINATED
  previous_stage:    string          # 上一个阶段（用于回溯）

  initiated_by:      string          # 谁发起的（node_a_id 或 node_b_id）
  initiated_at:      datetime

  last_activity_at:  datetime        # 最近一次活动时间
  stage_entered_at:  datetime        # 进入当前阶段的时间

  created_at:        datetime
  updated_at:        datetime

  # 关系层面的信誉
  relationship_trust:
    delivery:        float           # 双方交付可靠性 (0-100)
    communication:   float           # 沟通质量
    reliability:     float           # 稳定性
    overall:         float           # 关系信誉总分

  # 合作统计
  total_interactions: int
  total_projects:     int
  successful_projects: int
  failed_projects:    int
  total_value:        float          # 累计合作价值

  metadata:           Dict           # 扩展字段
`

### 3.2 RelationshipEvent

每一次关系变化都通过事件记录：

`yaml
RelationshipEvent:
  event_id:           string
  relationship_id:    string

  event_type:         enum
    # 状态变更
    - stage_transition          # 阶段跃迁
    - stage_regression          # 阶段回退
    - terminated                # 关系终止

    # 行为事件
    - contact_initiated         # 发起联系
    - contact_confirmed         # 确认联系
    - meeting_held              # 会议举行
    - proposal_sent             # 提案发送
    - proposal_accepted         # 提案接受
    - project_started           # 项目开始
    - project_completed         # 项目完成
    - project_failed            # 项目失败
    - feedback_received         # 收到反馈
    - endorsement_given         # 推荐对方
    - dispute_raised            # 争议
    - dispute_resolved          # 争议解决
    - renewal                   # 关系续约

  from_stage:         string          # 变化前阶段
  to_stage:           string          # 变化后阶段

  actor_id:           string          # 谁触发的
  description:        string

  # 信誉影响
  reputation_impact:  Dict            # 对关系信誉的影响
    dimension:        string          # delivery | communication | reliability
    change:           float           # 变化量

  evidence_refs:      List[string]    # 关联证据

  timestamp:          datetime
`

### 3.3 RelationshipReputation

与 Node Reputation 分离：

`yaml
RelationshipReputation:
  relationship_id:    string
  node_pair:          [string, string]

  dimensions:
    delivery_trust:   float     # 双方交付可靠性
    comm_trust:       float     # 沟通信誉
    reliability:      float     # 长期稳定性
    mutual_growth:    float     # 关系是否促进双方成长

  overall:            float     # 关系信誉总分 (0-100)
  level:              string    # A-E

  events_count:       int
  last_evaluated_at:  datetime
`

### 3.4 与 C5.1 Node Reputation 的关系

`
Node A Reputation  ——→  Relationship Reputation  ←——  Node B Reputation
      |                         |                         |
      v                         v                         v
  Capability              Delivery Trust              Capability
  Delivery                Communication               Delivery
  Relationship            Reliability                 Relationship
  Industry                Mutual Growth               Industry
  Innovation                                           Innovation
  Governance                                           Governance
  AI Recognition                                       AI Recognition
`

关系信誉受双方 Node Reputation 影响，但不等于两者平均。关系自己的历史事件最终决定其信誉。

---

## 第四章：与 C4 Connection Engine 的接口

### 4.1 连接前检查关系历史

C4 发现候选后，不直接推荐，而是先查询：

`python
# C4 调用 Relationship Engine
existing_rel = relationship_engine.get_relationship(node_a, node_b)

if existing_rel:
    if existing_rel.stage in ("TRUST", "ALLIANCE"):
        signal = "已有信任关系，建议深化合作"
    elif existing_rel.stage == "TERMINATED":
        signal = "曾有关系但已终止，原因: {reason}"
    else:
        signal = f"关系处于 {existing_rel.stage} 阶段"
else:
    signal = "新关系，建议从 Discovery 开始"
`

### 4.2 Future Alignment Score 升级

C4 的 5 因子评分增加第 6 个因子：

`
Future Alignment Score (v2):

  Capability Complementarity    30%
  Reputation Compatibility      20%   ← C5.1 动态信誉
  Future Path Match             20%
  Relationship History          15%   ← C5.2 新增
  Network Position              10%
  Historical Outcome             5%
`

---

## 第五章：与 C6 交易系统的接口

### 5.1 关系状态决定交易可能性

`
DISCOVERY/INTRODUCTION  → 仅展示信息，不开放交易
INTERACTION            → 可以发起咨询
COLLABORATION          → 可以进行小规模交易
EVIDENCE/TRUST         → 可以进行标准交易
ALLIANCE               → 可以进行大规模/战略交易
TERMINATED             → 不开放交易，展示终止原因
`

### 5.2 交易反哺关系信誉

`
Transaction Complete
        |
        v
Transaction Outcome (成功/失败/中立)
        |
        v
RelationshipEvent (project_completed / project_failed)
        |
        v
RelationshipReputation Update (增加或减少)
        |
        v
Node Reputation Update (通过 ReputationEvent)
`

---

## 第六章：最小版本范围 (C5.2 Scope)

### 6.1 后端

`
backend/app/universe/relationship_engine.py
`

核心类：

- Relationship — 数据类
- RelationshipEvent — 数据类
- RelationshipReputation — 数据类
- RelationshipStateMachine — 状态机
- RelationshipEngine — 主引擎

### 6.2 API

`
POST   /api/v1/relationships/create              创建关系 (DISCOVERY)
POST   /api/v1/relationships/{id}/transition      状态跃迁
POST   /api/v1/relationships/{id}/event           记录关系事件
GET    /api/v1/relationships/{node_id}            查询节点所有关系
GET    /api/v1/relationships/between/{a}/{b}      查询两个节点间关系
GET    /api/v1/relationships/{id}/reputation      获取关系信誉
GET    /api/v1/relationships/{id}/history         获取关系事件历史
`

### 6.3 配置文件

`
config/universe/relationship.yaml
`

### 6.4 不进 C5.2

- 关系可视化（图谱）— 留 C5.3 Universe Home
- 交易闭环 — 留 C6
- 关系智能推荐 — 留 C6

---

## 第七章：验收标准

### 输入

`
创建关系: 企业 A ↔ 服务商 B

事件序列:
  T+0:   Discovery (通过 C4 发现)
  T+7:   Introduction (发起联系)
  T+14:  Interaction (确认互动)
  T+30:  Collaboration (第一个项目启动)
  T+90:  Evidence (项目完成 + 双方好评)
  T+120: Trust (第二个项目成功)
`

### 输出

`
Relationship:
  Stage:     TRUST
  Trust:     B+ (72)

  History:
    DISCOVERY → INTRODUCTION → INTERACTION → COLLABORATION → EVIDENCE → TRUST

  Stats:
    Projects: 2/2 successful
    Total interactions: 14

  Reputation:
    Delivery:     A (88)
    Communication: B (65)
    Reliability:  B+ (72)
    Mutual Growth: A- (78)

  C4 Integration:
    Signal: "已有信任关系，建议深化合作"
`

---

## 第八章：Universe First Law Check

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | **服务哪个节点？** | 关系服务于两个节点，帮助它们理解彼此的历史和信任 |
| 2 | **帮节点解决什么问题？** | 回答“我和谁有什么样的关系，这个关系值得信任吗” |
| 3 | **增加了什么长期记忆？** | 每一次关系事件都是不可删除的社会记忆 |
| 4 | **是否增强未来连接能力？** | Relationship History 直接输入 C4，提升连接质量 |
| 5 | **关系信誉可解释吗？** | 每个分数都有溯源链：事件 → 影响 → 关系信誉 |
| 6 | **关系信誉可被篡改吗？** | 不可。只能追加事件，不能直接 set 分数 |

---

## 附录 A：与 08 Reputation Engine 的关系

08 定义的是 **Node Reputation**（节点信誉）。
09 定义的是 **Relationship Reputation**（关系信誉）。

两者关系：

`
Node Reputation (C5.1)     Relationship Reputation (C5.2)
       |                            |
       v                            v
  “这个节点值得信任吗？”      “这两个节点的关系值得信任吗？”
       |                            |
       +----------互为输入-----------+
`

Node Reputation 是 Relationship Reputation 的输入因子。
Relationship Outcome 反哺 Node Reputation（成功合作 → 提升节点信誉）。

---

> **冻结声明：** 本文档是 C5.2 的设计契约。所有代码实现必须可追溯至本文档中的模型、状态机和接口定义。如需修改，必须通过 Architecture Review。
