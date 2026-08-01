---
status: charter
authority: product
version: v0.1
last_review: 2026-08-01
role: C7 Node Demand Validation Layer — business reality charter (not implementation)
governance_tier: Living Document
precedes:
  - C7.1 Demand Intelligence
interfaces_with:
  - Reality / Observation / Evidence / Knowledge
  - Context / Position / Reputation
  - Connection / Transaction (future)
---

# GEO Universe Node Demand Framework — 商业真实性宪章

> 不是"我们能让世界运行"，而是"世界为什么必须进来"。
> 技术已经证明可以运行；这一章证明有人需要。

---

## 第一章：Node Demand First 法则（第零法则）

### 1.1 一句话定义

> 一切功能、引擎、页面和数据，必须能追溯到某个真实节点的真实需求；
> 不能回答"哪个节点、什么场景、什么问题、为什么现在必须解决"的功能，不进入准入。

### 1.2 为什么放在 Reality 上方

```
Human Reality（人的问题）
      |
      |  ← Demand 从这里进入
Demand
      |
Observation
      |
Evidence
      |
Knowledge
      |
Law
      |
Universe
      |
Position → Growth → Connection → Memory
```

现实不是从企业开始，而是从人的问题开始。企业之所以需要 GEO，是因为：
"100 个家长问题中，AI 推荐竞争者 80 次、推荐自己 5 次。"

### 1.3 与第一法则的关系

- 第一法则：Universe 服务每一个节点。
- 第零法则：节点为什么必须行动、为什么必须留在这里。

第一法则是世界观；第零法则是入场券。

---

## 第二章：DemandEvent 模型

DemandEvent 是 Universe 的"为什么"层——记录一个真实需求从提出到被满足的全过程。

### 2.1 字段契约（v0.1，冻结前可讨论）

```yaml
DemandEvent:
  event_id: string
  proposer_type: parent | enterprise | provider | student | teacher | government
  scenario: string              # 升学规划 / 采购决策 / 服务商选择 ...
  question_text: string         # 用户真实提出的问题
  decision_stage: research | comparison | shortlist | decision | post_purchase
  involved_nodes: [node_id]     # 学校 / 机构 / 课程 / 专家
  ai_answers: [artifact_id]     # 对应 AIAnswerArtifact
  mentioned_nodes: [node_id]    # AI 实际推荐了谁
  final_behavior: inquiry | consultation | transaction | none
  outcome: pending | won | lost | unknown
  impact_level: low | medium | high
  captured_at: datetime
  source: user_report | observation | partner_feed
  truth_status: observed | pending_review | verified | synthetic
```

### 2.2 核心不变式

- 问题来自真实人的真实场景；synthetic 仅用于实验，不得进入真实需求基线。
- 一次 DemandEvent 至少关联一个节点、一个 AI 回答、一个行为结果。
- 最终行为与结果必须可追溯（从问题 → 回答 → 行动 → 成交/流失）。

---

## 第三章：节点需求分类

按"谁 + 什么场景 + 什么问题"建立需求分类树：

### 3.1 教育科技特长生赛道（首批验证）

| 提出者 | 场景 | 典型问题 | 决策阶段 |
|---|---|---|---|
| 家长 | 升学规划 | "科技特长生值得报吗？" | research |
| 家长 | 机构选择 | "哪个机构适合我家孩子？" | comparison |
| 学生 | 课程选择 | "信息学竞赛还是机器人？" | research |
| 学校 | 合作采购 | "哪家课程服务商可信？" | shortlist |
| 机构 | 获客 | "为什么家长咨询后没成交？" | decision |
| 服务商 | 竞争 | "为什么 AI 总推荐竞品？" | comparison |

### 3.2 通用需求分类

- 认知需求：了解自己 / 了解对手 / 了解趋势
- 选择需求：选产品 / 选机构 / 选路径
- 信任需求：为什么信你 / 为什么不信你
- 成长需求：缺什么 / 下一步做什么
- 连接需求：该找谁 / 谁能帮我
- 交易需求：值得买吗 / 值多少

---

## 第四章：需求优先级算法（v0.1）

需求优先级 = f(频次, 紧迫度, 付费意愿, 可解决度, 生态价值)

```text
Priority =
  Frequency × 0.25      # 同类问题出现次数
+ Urgency    × 0.20      # 决策窗口（升学季 / 采购季）
+ Willingness× 0.25      # 用户愿投入的钱或时间
+ Solvability× 0.20      # Universe 现有能力能否显著改善
+ Ecosystem  × 0.10      # 是否带动多方节点参与
```

- 所有权重配置化，不硬编码。
- 低样本需求显示"样本不足"，不进入正式基线。
- 只能把"已验证的需求"用于产品决策；observed 需求只能作为线索。

---

## 第五章：需求 → 能力映射规则

任何新功能准入前必须填写映射：

```text
DemandEvent 场景
      ↓
节点：谁
      ↓
问题：什么
      ↓
现状：现在怎么解决、为什么不满意
      ↓
Universe 能力：哪个引擎/API/页面直接改善
      ↓
证据：现有 Observation / Evidence 能否支撑
      ↓
成本：投入多少，多久见效
```

### 5.1 现有能力映射示例

| 需求 | 现有能力 | 缺口 |
|---|---|---|
| 家长：选机构 | Connection + Reputation + Relationship | 缺少家长视角的 DemandEvent 数据 |
| 机构：为什么流失 | Decision + Memory | 缺少行为结果反馈 |
| 企业：AI 看不到我 | GEO Visibility + Evidence | 缺少真实 AI 基线 |
| 服务商：竞争者优势 | Competitor + Citation | 缺少竞争需求归因 |

---

## 第六章：功能准入机制

所有未来开发（Engine / Agent / View / Graph / Marketplace）必须通过以下检查：

1. **需求存在性**：至少 3 条真实 DemandEvent 或经审核的高频线索。
2. **节点指向性**：明确服务哪个节点、什么场景。
3. **能力复用**：优先复用现有 30 模型 / 100+ API / 10+ Engine。
4. **价值可测**：上线后有明确指标（成交率 / 咨询率 / 停留 / 复访）。
5. **不扩大污染**：不会让 synthetic 影响真实 Reputation / Position / Trust。
6. **成本受控**：不触发无预算的大模型调用或大规模采集。

不满足任一条件的，只记录为需求线索，不进入开发。

---

## 第七章：教育赛道验证方案（首批）

### 7.1 验证闭环

```
家长问题（真实）
      ↓
DemandEvent 捕获
      ↓
AI 回答观察（DeepSeek Smoke 后扩展）
      ↓
企业缺口分析
      ↓
Evidence 补充任务
      ↓
内容/运营动作
      ↓
AI 回答变化（再次观察）
      ↓
咨询/成交反馈
      ↓
Reputation 更新
```

### 7.2 首批验证对象

- 真实家长问题（社区/问卷/访谈，明确授权与隐私边界）
- 已入沙盒的真实教育节点（科大讯飞 / 好未来 / 网易有道 / 视源股份）
- 仿真节点仅用于流程压测，不进入真实需求基线

### 7.3 验证门槛

- 至少 30 条真实 DemandEvent（3 个问题 × 10 个家长/机构）
- 每条关联 AI 回答与行为结果
- 至少 5 个节点产生"需求 → 行动 → 结果"闭环
- 能回答：家长为什么咨询 A 而不是 B、企业为什么值得为此付费

---

## 附录：项目阶段定位（Alpha）

- ✅ 世界规则 / 节点 / 观察 / 记忆 / 信誉 / 关系 / 未来 / 连接
- ✅ 真实性边界（Fake vs Real vs Observed vs Verified）
- 🟡 真实需求数据（无：网络与凭证受限）
- 🟡 真实节点（当前为可追溯仿真沙盒）
- 🟡 真实结果反馈（无交易 / 咨询闭环数据）

> **本宪章冻结声明：** C7 及其后所有功能开发必须可追溯至本文档的需求链路。
> 未证明"为什么必须进入这个世界"，不继续扩展基础设施。
