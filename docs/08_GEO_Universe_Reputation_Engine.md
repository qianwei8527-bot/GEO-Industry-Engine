---
status: draft
authority: design
version: v1.1
last_review: 2026-07-31
parent: 07_GEO_Universe_World_Engine.md
role: design document — not implementation

governance_tier: Frozen Design — implementation must trace to this document; changes require Architecture Review
precedes:
  - C5.2 Relationship Lifecycle Engine
  - C5.3 Universe Home
interfaces_with:
  - C4 Future Connection Engine
  - Context Engine
  - Capability Engine
  - Memory Engine
---

# GEO Universe Reputation Engine —— 信任物理学

> C4 Connection Engine 证明了：如果信誉只是一个 score 字段，Universe 会退化成推荐系统。
> Reputation Engine 是 Universe 对一个节点长期行为结果的可信度记忆系统。
>
> 本文档定义：信誉如何出生、如何增长、如何衰减、如何传播。不是评分算法，而是信任演化机制。

---

## 第零章：文档定位

### 前置文档链

`
00_GEO_Universe_第一性原理.md  → 为什么 Universe 存在
01_GEO_Universe_产品哲学.md    → Universe 相信什么
02_Universe_世界规则.md        → 世界的基本规律
03_Universe_Dynamic_Evolution.md → 时间维度如何演化
04_Universe_UI_Design.md       → 用户如何感知
05_GEO_Universe_V6_能力地图.md → Universe 有什么能力
06_GEO_Universe_V6_产品架构.md → 如何实现这些能力
07_GEO_Universe_World_Engine.md → 世界如何运转
08_GEO_Universe_Reputation_Engine.md → 本文件：信任如何建立与演化
`

### 本文档的职责

定义 Reputation 不是属性而是演化结果，规定信誉事件的数据模型、多维度计算规则、权重衰减机制、与 Capability / Connection / Relationship 的接口契约。

### 为什么不是代码

C5.1 是架构分水岭。信誉模型一旦错误，后续的交易、认证、社区、B2B 都会变成普通平台。本文档将第一性原理和边界锁死，代码实现必须追溯至本文档。

---

## 第一章：信誉第一性原理

### 1.1 一句话定义

> **Reputation Engine 是 Universe 对一个节点长期行为结果的可信度记忆系统。**

三个关键词：

| 关键词 | 含义 | 反例 |
|--------|------|------|
| **长期** | 信誉在时间中累积，不反映瞬时热度 | 不是热搜、排行榜 |
| **行为结果** | 信誉来源于真实发生并被验证的事件 | 不是自我声明、广告声明 |
| **可信度** | 信誉是概率性判断，不是绝对真值 | 不是评分、星级 |

### 1.2 信誉不是属性，而是演化结果

**错（传统数据库）：**

`
Company { reputation: 85 }
`

静态字段。不知道 85 从何而来，不知道现在该上升还是下降，不知道哪个维度可信。

**对（GEO Universe）：**

`
Reputation = f(所有历史 ReputationEvent 的加权累计)
            × 时间衰减
            × 来源可信度
`

Reputation 不是 Node 的字段。Reputation 是 Event 的计算结果。

### 1.3 信誉和 Capability 的本质区别

这是 Universe 比普通数据库强的地方：

| 维度 | Capability | Reputation |
|------|-----------|------------|
| 回答的问题 | 能不能做？ | 别人相信你能不能做？ |
| 数据来源 | 能力声明 + Evidence | 行为结果 + 外部验证 |
| 变化速度 | 慢（需要积累证据） | 中等（每次事件都更新） |
| 可自声明 | 是 | 否（需外部来源） |
| 例如 | AI Agent Lv5 | 但 0 个案例 → 信誉低 |

一个节点可以拥有高 Capability 但低 Reputation（能力未经验证）。反之，低 Capability 但高 Reputation 是不成立的——没有能力支撑的信誉是泡沫。

### 1.4 信誉的不可篡改性

`
Reputation Score 不得通过 API 直接 set。
只能通过 ReputationEvent 追加变化。
Reputation 的历史不可删除（Event Store 原则）。
`

这是和传统 CRUD 最大的区别。信誉是 Append-only Log 的计算视图。

---

## 第二章：Reputation Vector —— 多维信誉

### 2.1 为什么不要单一分数

单一分数（如“85 分”）等同于大众点评评分，无法回答：

- 这个企业在哪个方面可信？
- 是技术能力强，还是交付靠谱？
- 是行业认可，还是客户认可？

### 2.2 七维信誉向量

`
                     Reputation
                        |
    ---------------------------------------------------------
    |       |        |        |       |        |         |
Capability  Delivery  Relationship  Industry  Innovation  Governance  AI Recognition
Trust     Trust     Trust         Trust     Trust       Trust       Trust
能力可信   交付可信   合作可信       行业认可   创新能力     规范程度     AI识别可信
`

### 2.3 各维度定义

| **AI Recognition Trust** | AI 系统对该节点的认知与推荐可信度 | AI 索引覆盖、被 Agent 引用、知识图谱中出现 | AI 搜索中不可见、被误归类 |

| 维度 | 定义 | 正面事件示例 | 负面事件示例 |
|------|------|-------------|-------------|
| **Capability Trust** | 能力是否被真实验证 | 认证通过、项目案例、能力证明 | 能力过期、声明夸大被发现 |
| **Delivery Trust** | 项目交付是否可靠 | 客户成功、按时交付、质量达标 | 失败交付、客户投诉、延期 |
| **Relationship Trust** | 合作中是否诚信 | 长期合作、双方互评高、重复合作 | 合作中断、违约、纠纷 |
| **Industry Trust** | 行业是否认可 | 行业奖项、协会成员、被引用 | 行业抵制、资格取消 |
| **Innovation Trust** | 创新是否持续 | 新能力发布、技术突破、研发投入 | 技术停滞、抄袭纠纷 |
| **Governance Trust** | 是否合规规范 | 合规认证、审计通过、数据安全 | 违规、安全事故、监管处罚 |

### 2.5 维度独立性

每个维度独立计算、独立衰减、独立查询。例如：

`
星辰AI：
  Capability:    A   (能力被 12 个 Evidence 验证)
  Delivery:      B+  (3 个成功项目，1 次延期)
  Relationship:  A   (5 个长期合作，双向好评)
  Innovation:    A-  (持续发布新能力)
  Governance:    B   (基础合规，尚未获得高级认证)
`

各维度不强制聚合。需要总体评分时使用加权聚合（权重可配置）。

### 2.6 ReputationStatus —— N/A ≠ 0

这是 Univese 与普通评分平台的本质区别。

普通平台：新节点 = 0 分 → 用户理解为“很差”。
Universe：新节点 = N/A → 含义是“世界还不了解它”。

**状态枚举：**

`python
class ReputationStatus(Enum):
    UNKNOWN = "N/A"          # 无足够证据，世界尚未形成判断
    DEVELOPING = "developing" # 正在积累证据，已有初步认知
    ESTABLISHED = "established" # 信誉已建立，有稳定证据支撑
    TRUSTED = "trusted"      # 信誉得到多方验证
    AUTHORITY = "authority"  # 行业权威，信誉不可置疑
`

**状态跃迁规则：**

`
N/A ──(第一个 ReputationEvent)──→ DEVELOPING
DEVELOPING ──(≥3 个正面事件 + overall > 50)──→ ESTABLISHED
ESTABLISHED ──(≥10 个正面事件 + overall > 75)──→ TRUSTED
TRUSTED ──(整体 A- 以上 + 行业影响力 > 80)──→ AUTHORITY

任何状态 ←──(长期无新事件, >365天)──→ 向 N/A 回落
`

**C4 Connection Engine 在遇到 N/A 时的行为：**
- 不惩罚（N/A ≠ 0 分）
- 不奖励（N/A ≠ 默认高分）
- 标注为“lack of evidence”（让用户知情决策）

**代码中严禁出现：**
`python
# ❌ 禁止
score = 0  # 默认 0 分

# ✅ 正确
score = None  # 无数据
status = ReputationStatus.UNKNOWN
`

---

## 第三章：核心数据模型

### 3.1 ReputationEvent

信誉的核心单元。所有信誉变化必须通过 ReputationEvent 记录。

`yaml
ReputationEvent:
  id:               string          # 唯一 ID
  node_id:          string          # 所属节点
  node_type:        string          # company | provider | ai_agent | government

  event_type:       enum            # 事件类型（见 3.2）
  dimension:        enum            # 影响维度（见 2.3）

  impact:           enum            # positive | negative | neutral

  base_weight:      float           # 基础权重 (0-10)
  evidence_weight:  float           # 证据类型权重 (0.3-1.0)
  source_reliability: float         # 来源可信度 (0.3-1.0)
  effective_weight: float           # = base_weight × evidence_weight × source_reliability

  source_type:      string          # certificate | customer | partner | observation | government
  source_id:        string          # 来源实体 ID
  source_detail:    string          # 来源描述（如“ISO 9001 认证”）

  evidence_refs:    List[string]    # 关联 Evidence ID 列表

  description:      string          # 人类可读描述

  timestamp:        datetime        # 事件发生时间
  recorded_at:      datetime        # 事件记录时间
`

### 3.2 事件来源层 —— 谁证明了什么

同一个事件（如 customer_success），来源不同，可信度完全不同：

| 来源 | 含义 | 可信度权重 | 示例 |
|------|------|-----------|------|
| government | 政府/官方 | 1.0 | 政府认证、监管通过 |
| association | 行业协会 | 0.9 | 行业奖项、协会成员 |
| enterprise_customer | 企业客户 | 0.85 | 大客户验收确认 |
| partner | 合作伙伴 | 0.8 | 合作方互评 |
| smb_customer | 中小企业客户 | 0.7 | 中小企业反馈 |
| self_report | 自我声明 | 0.3 | 企业自行上传 |
| ai_observation | AI 观察 | 0.5 | AI 自动发现与推断 |
| anonymous | 匿名 | 0.3 | 匿名评价 |

**核心原则：事件不是“发生了什么”，而是“谁证明了什么”。**

source_weight 字段在 ReputationEvent 中存储，默认为 source_type 对应的 source_reliability 值。可被具体证据的 evidence_weight 进一步调整。

### 3.3 事件类型枚举

`
capability_verified      # 能力被验证（Evidence 通过审核）
certification_passed     # 认证通过
certification_expired    # 认证过期
customer_success         # 客户项目成功
customer_failure         # 客户项目失败/投诉
partnership_completed    # 合作项目完成
partnership_terminated   # 合作终止
industry_award           # 行业奖项
industry_citation        # 被行业引用
innovation_release       # 新能力/产品发布
compliance_audit_passed  # 合规审查通过
compliance_violation     # 合规违规
peer_endorsement         # 同行推荐
negative_feedback        # 负面反馈
relationship_established # 新关系建立
relationship_strengthened # 关系增强
`

### 3.4 ReputationSnapshot —— Event 是事实，Snapshot 是计算结果

类似 NodeSnapshot 与 GeoEvent 的关系。ReputationEvent 是事实层（不可变），ReputationSnapshot 是计算视图（可重建）。

**为什么需要 Snapshot？**

1. **算法可迭代**：2027 年修改权重，必须能重新计算 2026 年的信誉。如果只存最终分数，历史不可重建。
2. **性能**：每次查询不必遍历全部历史事件。
3. **审计**：Snapshot 带有 computed_at 和 lgorithm_version，可追溯“这个分数是用什么参数算出来的”。

`yaml
ReputationSnapshot:
  snapshot_id:        string
  node_id:            string
  algorithm_version:  string          # 计算时使用的算法版本号

  dimensions:
    capability:
      score:          float
      level:          string
      event_count:    int
      contributing_event_ids: List[string]  # 参与本次计算的事件 ID

    delivery:         {同上}
    relationship:     {同上}
    industry:         {同上}
    innovation:       {同上}
    governance:       {同上}
    ai_recognition:   {同上}

  overall_score:       float
  overall_level:       string
  status:              enum          # UNKNOWN | DEVELOPING | ESTABLISHED | TRUSTED | AUTHORITY
  trend:               enum          # rising | stable | declining
  trend_momentum:      float         # -1.0 ~ 1.0

  computed_at:         datetime
  event_range_start:   datetime      # 参与计算的最早事件时间
  event_range_end:     datetime      # 参与计算的最新事件时间
  total_events:        int           # 参与计算的事件总数

  is_current:          boolean       # 是否是最新快照
`

**数据流：**

`
ReputationEvent (事实，不可变)
        |
        v
ReputationCalculator (算法，可配置)
        |
        v
ReputationSnapshot (计算结果，可重建)
        |
        v
ReputationProfile (对外的 API 视图，从最新 Snapshot 生成)
`

### 3.5 ReputationProfile

每个节点对外的信誉视图，由最新 ReputationSnapshot 生成。

`yaml
ReputationProfile:
  node_id:            string
  node_type:          string

  dimensions:
    capability:
      score:          float     # 0-100
      level:          string    # A+ / A / A- / B+ / B / B- / C / D / E
      event_count:    int       # 该维度事件总数
      last_updated:   datetime

    delivery:         {同上}
    relationship:     {同上}
    industry:         {同上}
    innovation:       {同上}
    governance:       {同上}

  overall_score:      float     # 加权聚合分 (0-100)
  overall_level:      string    # 综合等级

  trend:              enum      # rising | stable | declining
  trend_momentum:     float     # -1.0 ~ 1.0

  computed_at:        datetime  # 上次计算时间
  event_count_total:  int       # 总事件数
`

### 3.6 Profile 的计算时机

- **实时**：不要求。单次查询不触发全量重算。
- **增量**：新 ReputationEvent 写入时，增量更新受影响的维度。
- **全量**：定期（默认每周）全量重算，确保一致性。
- **按需**：API POST /reputation/recalculate/{node_id} 触发。

---

## 第四章：权重与衰减模型

### 4.1 Evidence Weight（证据类型权重）

不同来源的证据对信誉的影响权重不同：

`yaml
evidence_weights:
  government_certification:  1.0    # 政府/官方认证
  industry_certification:    0.9    # 行业协会认证
  customer_verified:         0.9    # 客户验证
  partner_endorsement:       0.8    # 合作伙伴推荐
  case_study_published:      0.7    # 公开案例
  peer_reviewed:             0.7    # 同行评审
  ai_observation:            0.5    # AI 自动观察
  self_declared:             0.3    # 自我声明
`

### 4.2 Source Reliability（来源可信度）

`yaml
source_reliability:
  government:           1.0
  industry_association: 0.9
  enterprise_customer:  0.85
  smb_customer:         0.7
  individual_user:      0.6
  ai_inferred:          0.5
  anonymous:            0.3
`

### 4.3 Time Decay（时间衰减）

信誉会老化。5 年前的案例对当前信誉的判断价值下降。

使用指数衰减模型：

`
effective_score = event_score × e^(-λ × age_in_years)
`

其中 λ（衰减系数）按事件类型配置：

`yaml
time_decay:
  # half_life: 该类型事件的半衰期
  certification:
    half_life_days: 730    # 认证两年衰减一半
  project_success:
    half_life_days: 365    # 项目成功一年衰减一半
  project_failure:
    half_life_days: 540    # 失败事件衰减更慢（更持久）
  industry_award:
    half_life_days: 365
  innovation_release:
    half_life_days: 180    # 创新更快过期
  partnership:
    half_life_days: 180
  compliance_violation:
    half_life_days: 1095   # 违规记录三年才衰减一半（长期影响）
`

λ 由半衰期计算：λ = ln(2) / half_life_years

### 4.4 聚合权重

当需要 Overall Score 时，各维度加权聚合（可配置）：

`yaml
aggregation_weights:
  capability:       0.22
  delivery:         0.22
  relationship:     0.18
  industry:          0.10
  innovation:        0.08
  governance:        0.08
  ai_recognition:    0.12
`

---

## 第五章：信誉的生命周期

### 5.1 出生

节点创建时，ReputationProfile 不存在。第一个 ReputationEvent 写入时创建 Profile，所有维度初始化为 N/A（无数据，不是 0）。

这区别于新节点=低信誉：N/A 表示“尚无判断”，0 表示“有负面证据”。C4 Connection Engine 在遇到 N/A 时不惩罚也不奖励。

### 5.2 成长

每次正面 ReputationEvent：对应维度 score += effective_weight。
每次负面 ReputationEvent：对应维度 score -= effective_weight。

Score 范围为 0-100。超出边界时截断。

### 5.3 衰减

每周对所有维度应用时间衰减：每个历史事件的有效权重按半衰期衰减。衰减后的 Profile 重新计算。

如果一个节点长期没有新事件，其 Profile 逐渐向 N/A 回落（信任需要持续维持）。

### 5.4 传播（受限）

关系层面的信任传播：A 信任 B，B 信任 C，A 对 C 有间接信任加成。

**核心限制：传播有方向，不能跨维度。**

`
合作成功事件 可以影响：  Delivery Trust + Relationship Trust
            不能影响：  Innovation Trust, Governance Trust, AI Recognition Trust

行业奖项事件 可以影响：  Industry Trust + AI Recognition Trust
            不能影响：  Delivery Trust, Relationship Trust
`

**传播公式：**

`
IndirectTrust(A, C) = RelationshipTrust(B) × RelationshipStrength(A, B) × RelationshipStrength(B, C) × DampingFactor
`

DampingFactor 默认 0.5（信任每次传播衰减一半）。

**传播限制规则表：**

| 源维度 | 可传播至 | 不可传播至 |
|--------|---------|-----------|
| Capability | Industry, AI Recognition | Delivery, Relationship, Governance |
| Delivery | Capability（轻度）, Relationship | Innovation, Governance |
| Relationship | Relationship（直接连接）, Capability（轻度） | Innovation, Governance, AI Recognition |
| Industry | AI Recognition, Capability | Delivery, Governance |
| Innovation | AI Recognition, Industry | Delivery, Relationship |
| Governance | 无可传播 | 所有 |
| AI Recognition | Industry, Capability | Delivery, Relationship |

**最大传播跳数：** 3（默认）。超过 3 跳的间接关系不参与信誉计算。

**第一版范围：** 仅实现 1 跳传播（直接关系）。多跳传播留 C5.2。

### 5.5 死亡

节点删除时，ReputationEvent 不删除（Append-only Log 原则）。Profile 标记为 archived。历史事件保留用于统计分析。

---

## 第六章：与现有模块的接口

### 6.1 与 C4 Connection Engine

**现在（无 Reputation Engine）：**

`python
# C4 从候选池的静态 trust 字段读取
trust_compat = candidate["trust"] / 100.0  # 静态值
`

**改造后：**

`python
# C4 从 Reputation Engine 获取动态信誉
profile = reputation_engine.get_profile(candidate_id)
trust_compat = profile.get_dimension("delivery").score / 100.0  # 动态计算

# Connection Score 重构：
Connection Score = Capability Match    × 0.35
                 + Future Alignment    × 0.25
                 + Reputation Profile  × 0.25   # ← 替代原 Trust Compatibility
                 + Relationship History × 0.15
`

### 6.2 与 Context Engine

Context Engine 的 NodeContext 增加 
eputation_profile 字段：

`python
NodeContext:
  identity:           {...}
  current_position:   {...}
  historical_memory:  {...}
  capability_state:   {...}
  reputation_profile: {...}   # ← 新增
  relationship_context: {...}
`

### 6.3 与 Capability Engine

Capability 回答“能不能做”，Reputation 回答“别人信不信”。两者独立但互验证。

- Capability Lv5 但没有 Reputation 支撑 → 能力声明存疑
- Reputation A 但 Capability 低 → 不可能（信誉必须有能力基础）
- 交叉校验触发 Capability Review Flag

### 6.4 与 Memory Engine

`python
# ReputationEvent 是 Memory 的子类关系
Facts → Evidence → ReputationEvent → Stories
`

Memory 记录“发生了什么”，Reputation 解释“因此变得多可信”。

### 6.5 与 C5.2 Relationship Lifecycle

关系状态演进依赖信誉：

`
Unknown ──(双方信誉达标)──→ Candidate ──(首次接触)──→ Connected
Connected ──(有合作事件)──→ Collaborating ──(成功结果)──→ Verified Partner
Verified Partner ──(长期+高信誉)──→ Strategic Relationship
`

每个状态跃迁都有最低信誉阈值要求。详见 C5.2 设计文档。

---

## 第七章：YAML 配置化

所有权重、衰减参数、维度定义通过 YAML 配置，不硬编码。

**配置文件位置：** config/universe/reputation.yaml

`yaml
version: "1.0"

dimensions:
  - id: capability
    label: "能力信誉"
    label_en: "Capability Trust"
    aggregation_weight: 0.25
  - id: delivery
    label: "交付信誉"
    label_en: "Delivery Trust"
    aggregation_weight: 0.25
  - id: relationship
    label: "合作信誉"
    label_en: "Relationship Trust"
    aggregation_weight: 0.20
  - id: industry
    label: "行业认可"
    label_en: "Industry Trust"
    aggregation_weight: 0.12
  - id: innovation
    label: "创新能力"
    label_en: "Innovation Trust"
    aggregation_weight: 0.10
  - id: governance
    label: "规范程度"
    label_en: "Governance Trust"
    aggregation_weight: 0.08

event_types:
  capability_verified:
    dimension: capability
    impact: positive
    base_weight: 8.0
  certification_passed:
    dimension: capability
    impact: positive
    base_weight: 9.0
  certification_expired:
    dimension: capability
    impact: negative
    base_weight: -5.0
  customer_success:
    dimension: delivery
    impact: positive
    base_weight: 7.0
  customer_failure:
    dimension: delivery
    impact: negative
    base_weight: -9.0
  partnership_completed:
    dimension: relationship
    impact: positive
    base_weight: 6.0
  partnership_terminated:
    dimension: relationship
    impact: negative
    base_weight: -7.0
  industry_award:
    dimension: industry
    impact: positive
    base_weight: 8.0
  innovation_release:
    dimension: innovation
    impact: positive
    base_weight: 6.0
  compliance_audit_passed:
    dimension: governance
    impact: positive
    base_weight: 7.0
  compliance_violation:
    dimension: governance
    impact: negative
    base_weight: -10.0
  peer_endorsement:
    dimension: relationship
    impact: positive
    base_weight: 5.0

evidence_weights:
  government_certification: 1.0
  industry_certification: 0.9
  customer_verified: 0.9
  partner_endorsement: 0.8
  case_study_published: 0.7
  peer_reviewed: 0.7
  ai_observation: 0.5
  self_declared: 0.3

source_reliability:
  government: 1.0
  industry_association: 0.9
  enterprise_customer: 0.85
  smb_customer: 0.7
  individual_user: 0.6
  ai_inferred: 0.5
  anonymous: 0.3

time_decay:
  certification:
    half_life_days: 730
  project_success:
    half_life_days: 365
  project_failure:
    half_life_days: 540
  industry_award:
    half_life_days: 365
  innovation_release:
    half_life_days: 180
  partnership:
    half_life_days: 180
  compliance_violation:
    half_life_days: 1095

level_thresholds:
  A_plus: 95
  A: 85
  A_minus: 78
  B_plus: 70
  B: 60
  B_minus: 50
  C: 40
  D: 25
  E: 0
`

---

## 第八章：最小版本范围（C5.1 Scope）

### 8.1 后端

新增文件：

`
backend/app/universe/reputation_engine.py
`

核心类：

- ReputationEvent — 数据类
- ReputationProfile — 数据类
- ReputationCalculator — 计算引擎
- ReputationEngine — 主引擎（单例）

### 8.2 API

`
POST   /api/v1/reputation/event              # 写入信誉事件
GET    /api/v1/reputation/node/{node_id}     # 获取节点信誉 Profile
GET    /api/v1/reputation/history/{node_id}  # 获取信誉事件历史
POST   /api/v1/reputation/recalculate/{node_id}  # 触发重算
`

### 8.3 配置文件

`
config/universe/reputation.yaml
`

### 8.4 接入范围（第一批）

从已有系统接入，不创建新数据源：

- Evidence（已有）→ reputation event 当 evidence 被验证
- Certification（已有）→ reputation event 当认证通过
- GeoEvent（已有）→ reputation event 当事件包含信誉影响
- Relationship（已有）→ reputation event 当合作完成

### 8.5 不进 C5.1

- 前端可视化（留 C5.2）
- 关系传播算法完整实现（留 C5.2）
- 时间衰减定时任务（C5.1 用简单实现，C5.2 用生产级调度）

---

## 第九章：信誉解释器 (Reputation Explanation)

### 9.1 为什么需要解释器

GEO Universe 与普通推荐系统最大的区别不是给出结果，而是**解释为什么**。

AI 时代用户不会相信一个没有理由的分数。如果 Reputation API 只返回：
`json
{ "score": 82 }
`
用户无法区分这是“能力信誉高”还是“交付信誉高”，也不知道“82 分是哪来的”。

### 9.2 ReputationExplanation 数据模型

`yaml
ReputationExplanation:
  node_id:            string

  overview:
    status:           enum          # UNKNOWN | DEVELOPING | ESTABLISHED | TRUSTED | AUTHORITY
    overall_score:    float
    overall_level:    string
    summary:          string        # 一句话总结（如“交付记录优秀，但行业认证不足”）

  dimension_breakdown:              # 每个维度的详细解释
    capability:
      score:          float
      level:          string
      top_contributors:              # 影响最大的 3 个事件
        - event_id:   string
          description: string
          impact:     string  # "+8"
          date:       string
      risk_flags:     List[string]  # 风险提示

    delivery:         {同上}
    relationship:     {同上}
    industry:         {同上}
    innovation:       {同上}
    governance:       {同上}
    ai_recognition:   {同上}

  trajectory:                       # 变化轨迹（最近 90 天）
    - date:           string
      event:          string
      change:         string  # "+8" or "-5"

  risk_signals:                    # 全局风险信号
    - signal:         string       # 如“近 180 天缺少新证据”
      severity:      enum         # low | medium | high

  recommendations:                 # AI 生成的建议
    - action:         string       # 如“建议补充行业认证以提升 Industry Trust”
      target_dimension: string
`

### 9.3 API 响应格式

`
GET /api/v1/reputation/node/{node_id}
`

返回 ReputationExplanation（而非裸分数）：

`json
{
  "node_id": "comp-001",
  "overview": {
    "status": "TRUSTED",
    "overall_score": 82,
    "overall_level": "A-",
    "summary": "交付记录优秀，行业认证待补强。AI 系统中已有较好可见度。"
  },
  "dimension_breakdown": {
    "capability": {
      "score": 88,
      "level": "A",
      "top_contributors": [
        {
          "event_id": "ev-001",
          "description": "GEO 认证通过",
          "impact": "+9",
          "date": "2026-01"
        }
      ],
      "risk_flags": []
    },
    "delivery": {
      "score": 72,
      "level": "B+",
      "top_contributors": [
        {
          "event_id": "ev-002",
          "description": "完成客户项目 ×3",
          "impact": "+21",
          "date": "2026-03"
        }
      ],
      "risk_flags": []
    },
    "ai_recognition": {
      "score": 68,
      "level": "B+",
      "top_contributors": [
        {
          "event_id": "ev-005",
          "description": "被 AI Agent 引用",
          "impact": "+5",
          "date": "2026-06"
        }
      ],
      "risk_flags": ["AI 搜索覆盖率仅 40%"]
    }
  },
  "trajectory": [
    {"date": "2026-01", "event": "获得认证", "change": "+9"},
    {"date": "2026-03", "event": "成功交付×2", "change": "+14"},
    {"date": "2026-05", "event": "同行推荐", "change": "+5"},
    {"date": "2026-07", "event": "负面反馈×1", "change": "-6"}
  ],
  "risk_signals": [
    {"signal": "近 180 天缺少新认证证据", "severity": "medium"}
  ],
  "recommendations": [
    {"action": "建议补增行业奖项或认证，提升 Industry Trust", "target_dimension": "industry"}
  ]
}
`

### 9.4 验收标准

### 输入

`
节点: 星辰AI营销科技

事件序列:
  2026-01: 获得 ISO 认证          (certification_passed,  +9)
  2026-03: 客户项目成功            (customer_success,       +7)
  2026-03: 客户项目成功            (customer_success,       +7)
  2026-05: 合作伙伴推荐            (peer_endorsement,       +5)
  2026-07: 一次负面反馈            (negative_feedback,      -6)
`

### 输出

`
Reputation Profile:

  Capability Trust:     A   (88)  [认证通过 — 来源: 政府, 权重: 1.0]
  Delivery Trust:       B+  (72)  [2次成功交付 — 衰减后有效分]
  Relationship Trust:   A-  (76)  [合作推荐]
  Industry Trust:       N/A       [无行业事件]
  Innovation Trust:     N/A       [无创新事件]
  Governance Trust:     B   (64)  [通过合规审查]

  Overall:              82  (A-)

  变化轨迹:
    认证: +9
    成功交付 ×2: +14
    推荐: +5
    负面: -6
    当前趋势: rising

  C4 Connection Engine 查询:
    为什么推荐这个伙伴？
    未来路径匹配:    92%
    信誉匹配:        87%  ← Reputation Engine 提供
    历史合作成功:    90%
`

---

## 第十章：Universe First Law Check

任何 Reputation Engine 的实现必须通过以下检查：

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | **服务哪个节点？** | 信誉服务于每一个节点，帮助它被世界正确认知 |
| 2 | **帮节点解决什么问题？** | 回答“我的信誉从何而来”和“为什么别人信任我” |
| 3 | **增加了什么长期记忆？** | 每一次信誉事件都是不可删除的世界记忆 |
| 4 | **是否增强未来连接能力？** | 信誉直接输入 C4 Connection Engine，提升连接质量 |
| 5 | **信誉可解释吗？** | 每个分数都有溯源链：事件 → 权重 → 来源 → 衰减 |
| 6 | **信誉可被篡改吗？** | 不可。只能追加事件，不能直接 set 分数 |

---

## 附录 A：与 07 World Engine 的关系

07 文档中 World Engine 的“五齿轮”之一就是 Reputation：

`
Observation → Event → Graph → Memory → Reputation
`

本文档是对 Reputation 齿轮的展开设计。

07 定义的 Reputation 职责：
> “从长期记忆中计算动态信誉”

本文档细化：
- 如何计算（ReputationEvent → 加权 → 衰减 → 聚合）
- 计算什么（六维向量，非单一分数）
- 在何处使用（C4 Connection / C5.2 Relationship）
- 如何保证可信（Append-only / 可溯源 / 不可篡改）

## 附录 B：与未来 C5.2 Relationship Lifecycle 的关系

C5.2 的关系状态机将依赖 Reputation Engine 提供阈值判断：

`
Unknown → Candidate:         双方 overall_score > 40
Candidate → Connected:      首次接触（无信誉门槛）
Connected → Collaborating:  有 ReputationEvent(partnership)
Collaborating → Verified:   delivery_trust > 60 且 relationship_trust > 50
Verified → Strategic:       overall_score > 80 且 relationship_age > 1年
`

本文档已预留接口。具体关系状态机设计见 C5.2 文档。

---

> **冻结声明：** 本文档是 C5.1 的设计契约。所有代码实现必须可追溯至本文档中的模型、公式和接口定义。如需修改，必须通过 Architecture Review。
