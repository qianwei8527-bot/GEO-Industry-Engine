---
status: stable
authority: living
version: v1.0
last_review: 2026-07-31
approved_by: CTO
parent: 06_GEO_Universe_V6_产品架构.md
role: operational principles document

governance_tier: Living Specification — evolves as Universe grows; not a frozen spec

---

# GEO Universe World Engine —— 世界运行原理

> 00-06 号文档回答了为什么存在、相信什么、世界是什么、有什么能力、如何实现。
> 本文件回答此前未被完整定义的问题：**这个世界是如何运转的？**
>
> World Engine 不是一组新功能。它是让 Universe 从静态数据库变成会自己生长的产业世界的运行机制层。

---

## 第零章：文档定位

### 前置文档链

00_GEO_Universe_第一性原理.md → 为什么 Universe 存在
01_GEO_Universe_产品哲学.md → Universe 相信什么
02_Universe_世界规则.md → 世界的基本规律
03_Universe_Dynamic_Evolution.md → 时间维度如何演化
04_Universe_UI_Design.md → 用户如何感知
05_GEO_Universe_V6_能力地图.md → Universe 有什么能力
06_GEO_Universe_V6_产品架构.md → 如何实现这些能力
07_GEO_Universe_World_Engine.md → 本文件：世界如何运转

### 本文档的职责

定义 Universe 的运行循环、变化处理机制、输出模型，以及工程约束。后续所有 Agent、API、数据管道、定时任务的设计必须引用本文档中的运行原理，不得自行发明与本文档冲突的运转逻辑。
## 第一章：World Engine 不是四个模块，是一个循环

### 1.1 为什么不是模块

如果将 Observation、Event、Graph、Reputation 定义为四个独立模块，容易导致各自拥有独立的数据流和状态，集成时需要额外协调层，新增观察源或输出通道时需要修改多个模块。

实际上，它们不是并列关系，而是一个闭环的五个阶段：

```
Observation（观察）
        ↓
Event（事件化）
        ↓
Graph（关系演化）
        ↓
Memory（沉淀记忆）
        ↓
Reputation（形成信誉）
        ↓
再次观察……
```

### 1.2 五齿轮定义

| 齿轮 | 职责 | 输入 | 输出 |
|------|------|------|------|
| Observation | 检测世界发生了什么值得记录 | 外部信号（新闻、API、用户行为、Agent 扫描） | Candidate Change（候选变化） |
| Event | 将候选变化转化为 Universe 可理解的事件 | Candidate Change | GeoEvent + 受影响节点列表 |
| Graph | 根据事件更新节点关系和结构 | GeoEvent + 当前图谱 | 更新后的 Relationship 集合 |
| Memory | 将变化持久化为可回溯的历史 | 更新后的节点状态 | NodeSnapshot + History 记录 |
| Reputation | 从长期记忆中计算动态信誉 | Memory 序列 | Reputation Score + Trust Profile |

### 1.3 循环特性

- **闭环**：Reputation 的变化本身又成为新的 Observation 输入（信誉上升 → 被同行观察 → 触发新关系）
- **异步**：五个齿轮可以独立运行在不同时间尺度上（Observation 每天多次，Reputation 每周计算，Memory 即时写入）
- **可插拔**：新增观察源只需接入 Observation 层，新增输出通道只需从 Reputation/Memory 层导出

---

## 第二章：世界运行第一原则

### 2.1 核心原则

> **Universe 不记录状态，而记录变化。**

传统数据库回答「现在有什么」。Universe 回答「什么发生了变化」。

### 2.2 为什么

- 静态状态是任何数据库都能提供的，AI 大模型也能通过搜索获取
- **变化**才是 Universe 的不可替代资产：谁在上升、谁在衰退、什么关系正在形成、哪个赛道在加速
- 变化是信誉的基础：没有历史变化记录，信誉只是一个数字；有变化记录，信誉是一个可溯源的故事

### 2.3 工程含义

- NodeSnapshot 不是「当前数据快照」，而是「自上次快照以来的差异记录」
- GeoEvent 不是通知，是触发世界状态变更的因果链起点
- 每次 API 写入必须附带 `change_reason`（变化原因），不能只更新数值

---

## 第三章：Observation 不是采集，是「什么值得记录」

### 3.1 传统采集的失败模式

许多系统将 Observation 等同于数据采集：爬虫抓取 → 存入数据库 → 展示。这会导致数据冗余、信号淹没、维护负担。

### 3.2 Universe Observation 的定义

Observation 回答的不是「发生了什么」，而是：

> **发生了什么事，值得 Universe 记住并做出反应？**

### 3.3 Observation 的输出：Candidate Change

Observation 不输出原始数据。它输出 Candidate Change（候选变化），包含：

```
Candidate Change {
    change_type:     // 变化类型（新节点 / 关系变化 / 分数变化 / 阶段跃迁 / 外部事件）
    affected_nodes:  // 受影响的节点 ID 列表
    signal_strength: // 信号强度（0-1，低于阈值的被过滤）
    evidence:        // 变化依据（来源 URL、API 响应摘要、Agent 分析结论）
    suggested_action:// 建议 Universe 采取的行动（创建 / 更新 / 关联 / 通知）
    certainty_level: // 确定性等级（A / B / C）
}
```
---

## 第四章：三种确定性，不是三种自动化程度

### 4.1 为什么不用「自动/半自动/人工」

这三个词描述的是**执行方式**，而非**信息质量**。Universe 关心的是变化的可靠程度，而不是谁来执行。

### 4.2 Level A：确定变化（Deterministic）

变化依据充分、可直接验证。Universe 自动接受并更新。

**示例**：Evidence 数量 +1、Relationship 新增（双方确认）、Snapshot 生成、Score 基于规则引擎计算。

**工程约束**：Level A 变化写入后自动触发下游齿轮，无需等待。

### 4.3 Level B：推断变化（Inferred）

变化有证据但需要确认。Observation 提出，进入待确认队列。确认后按 Level A 处理。

**示例**：发现新公司、推断合作关系、发现行业细分赛道、Agent 分析建议。

**工程约束**：Level B 变化进入 pending_changes 实体，附带证据摘要和置信度分数。确认后转为 Level A。

### 4.4 Level C：规则变化（Governed）

这不是数据变化，而是 Universe 自身的物理定律变化。必须经过治理流程。

**示例**：Universe Rule 修改、评分模型参数变更、认证标准变更、节点生命周期定义调整。

**工程约束**：Level C 变化必须通过项目宪章定义的架构审议流程。变更后需要回灌历史数据进行影响评估。

### 4.5 确定性等级与齿轮的关系

```
Observation 输出 → 标记 certainty_level
        ↓
Level A → 自动进入 Event → Graph → Memory → Reputation
Level B → 进入待确认队列 → 确认后 = Level A
Level C → 进入治理流程 → 批准后更新 World Engine 规则定义
```

---

## 第五章：Universe 最终输出什么

### 5.1 不是地图、报告或 Agent 回答

地图、报告、Panel、Agent 回答都是**呈现形式**，不是 Universe 的核心输出。

### 5.2 三种核心输出

#### Position（位置）

> 你在哪里？

不是一个分类标签，而是一个多维坐标：产业维度、能力维度、竞争维度、时间维度、信誉维度。Position 由 Graph 层维护：一个节点的位置不是孤立定义的，而是由它和周围节点的关系网络决定的。

API 端点：`GET /universe/position/{node_id}`

#### Trajectory（轨迹）

> 你是怎么走到这里的？

不是时间线列表，而是阶段变化的因果链：每个阶段跃迁的触发事件、关键证据、能力变化。Trajectory 由 Memory 层维护：NodeSnapshot 序列 + GeoEvent 因果链。

API 端点：`GET /universe/evolution/{node_id}`

#### Possibility（可能性）

> 未来有哪些可能？

不是预测（Prediction），而是基于当前位置、成长轨迹、生态关系的可能性空间。Universe 不替用户决定未来，它展示可能的路径及其依据。Possibility 不来自单一 AI 模型，而是来自 Universe 自身的多维数据：相似节点的成长路径（Memory）、行业趋势方向（Graph + Event）、能力缺口与机会（Reputation + Position）。

API 端点：`GET /universe/possibilities/{node_id}`

### 5.3 与 AI 大模型的分工

| 维度 | AI 大模型 | GEO Universe |
|------|----------|--------------|
| 回答「你在哪里」 | 可以生成一个答案 | 给出精确的多维坐标，持续更新 |
| 回答「你怎么来的」 | 只能猜测 | 有完整的 NodeSnapshot 历史链 |
| 回答「未来往哪走」 | 基于通用知识预测 | 基于同类节点的真实演化路径 + 你的当前位置 |

核心原则：

> **Universe 不提供答案，而提供坐标、记忆与可能性。**
---

## 第六章：与现有架构的关系

### 6.1 World Engine 在 V6 架构中的位置

```
                 GEO Universe
                      |
        --------------------------------
        |              |               |
   世界认知层       智能增长层        价值连接层
   (Perception)    (Growth)        (Connection)
        |              |               |
   Universe Core   AI Engine       Ecosystem
        |
   ┌─────────────────────────────────┐
   │       World Engine（本层）       │
   │  Observation → Event → Graph    │
   │       → Memory → Reputation     │
   └─────────────────────────────────┘
        |
   ─────────────────────────────
   Data / API / Agent / Frontend
```

World Engine 位于能力层之下、数据层之上。它是能力层的数据引擎。

### 6.2 现有组件如何映射到 World Engine

| 现有组件 | World Engine 角色 |
|----------|------------------|
| EnterpriseDiagnostician Agent | Observation 的一种来源（内部诊断） |
| GEOObservationAgent（规划中） | Observation 的主动扫描来源 |
| NodeSnapshot 模型 | Memory 层的持久化实现 |
| GeoEvent 模型 | Event 层的持久化实现 |
| Reputation 模型 | Reputation 层的输出存储 |
| Relationship 模型 | Graph 层的输出存储 |
| Node Evolution API | Trajectory 输出的 API 实现 |
| IntelligencePanel | Position + Trajectory + Possibility 的前端呈现 |

### 6.3 不改变现有 API 契约

World Engine 是**内部运行机制**，不改变已有的 API 端点。现有 API 继续工作，但底层数据写入和更新逻辑遵循 World Engine 的五齿轮流程。

---

## 第七章：工程约束

### 7.1 Observation 管道设计约束

- 所有观察源必须通过统一的 Observation.register(candidate_change) 接口写入
- 禁止观察源直接写入 Entity / Company / Relationship 表（绕过 Event 和 Graph 齿轮）
- 每个 Candidate Change 必须携带 source 字段（标识观察者：agent / user / api / crawler / system）
- 每个 Candidate Change 必须携带 certainty_level（A / B / C）

### 7.2 Snapshot 分辨率约束

- 每个节点至少保留 30 天内的每日快照（snapshot_type=daily）
- 30-180 天：每周快照（snapshot_type=weekly）
- 180 天以上：月度快照（snapshot_type=monthly）
- 事件触发快照（snapshot_type=event）：不限数量，保留全部
- 历史快照可以降采样，但不可删除

### 7.3 Reputation 计算约束

- Reputation 必须基于 Memory 层的序列数据计算，不能基于当前瞬时状态
- 信誉计算必须可解释：每个 Reputation Score 的变更必须引用具体的事件 ID 和快照 ID
- 信誉更新周期：每周至少一次全量计算，Level A 事件触发即时增量更新

### 7.4 新增观察源的最低要求

任何新增观察源接入时必须满足：

```
1. 定义观察范围（观察哪些节点类型、哪些维度）
2. 定义输出格式（Candidate Change schema）
3. 定义信号强度阈值（低于阈值的候选变化不进入 Event 层）
4. 定义确定性等级策略（哪些情况输出 Level A，哪些 Level B）
```


### 7.5 新功能评审过滤器（CTO 决策参考）

任何新功能提案在进入架构评审前，必须先回答三个问题：

1. **它增加了新的 Evidence 吗？** —— 是否让 Universe 观察到此前无法捕获的变化？
2. **它增加了新的 Knowledge 吗？** —— 是否让 Universe 理解了此前无法归类的节点或关系？
3. **它完善了已有的 Law 吗？** —— 是否让 Universe 的治理能力变得更精确或更完整？

如果三个答案都是 **否**，该功能大概率属于 UI 优化、流程改进或展示层调整，而非 Universe 核心能力的增强。此类功能可以做，但优先级应服从于能产生 Evidence / Knowledge / Law 增量的特性。

这个过滤器不对外公开，但作为 CTO 和架构团队评审任何 Sprint 范围时的决策基线。
---

## 第八章：Sprint 6 引导

### 8.1 从 Living Sandbox 到 World Engine

Sprint 5.3-B 完成的是 Living Sandbox（生命沙盘）：固定节点、固定关系、固定事件，人工设计。Sprint 6 的目标是让 Universe 开始**自己生长**。

### 8.2 第一个可运转齿轮序列

Sprint 6 的最小可运转目标：跑通一条完整的 Observation → Event → Graph → Memory → Reputation 链路，产生一个非人工写入的节点状态变更。

顺序：

Sprint 6.1: Observation Pipeline —— 实现 Candidate Change 统一接口，接入首个外部观察源，实现 Level A/B 分类和 Level B 待确认队列

Sprint 6.2: Event Engine —— 将 Candidate Change 转化为 GeoEvent，计算受影响节点范围，触发 Graph 更新

Sprint 6.3: Graph + Memory —— 根据 Event 自动更新 Relationship，生成 NodeSnapshot 并标记 change_reason，实现 Snapshot 降采样策略

Sprint 6.4: Reputation Engine —— 基于 Memory 序列计算动态信誉，实现信誉变化可解释性，输出至 IntelligencePanel

Sprint 6.5: Universe 自更新验证 —— 端到端验证一条非人工变化链，文档化第一个自动生长的证据

### 8.3 验收标准

Sprint 6 的唯一验收标准：

> **Universe 在没有预先定义该概念的前提下，通过 Observation → Candidate Change → Knowledge → Law 的完整链路，成功吸收并治理一个全新的节点类型。**

拆解如下：

1. 存在一个节点类型，在种子数据和当前 World Model 中不存在（如 AI Employee、AI Agent Provider 等）
2. Observation 通过外部信号检测到该概念的多次出现，生成 Candidate Change（Evidence 层）
3. Candidate Change 积累达到阈值，触发 World Model 的 Knowledge 更新——承认该概念为一个新的节点类型
4. Universe Rules（Law 层）为该新节点类型分配合适的能力边界（可以成长 / 可以建立信誉 / 不能作为营业主体等）
5. 整个链路的前端呈现可追溯：从原始信号到 Evidence、到 Knowledge 更新、到 Law 约束

---

### 8.4 开发硬约束：Universe First Law Check

任何新功能提案、Sprint 规划、Agent 设计，在进入开发前必须回答四个问题：

1. **它服务哪个节点？** —— 企业？服务商？个人？投资者？政府？AI Agent？如果没有明确的服务对象，不是 Universe 能力。
2. **它帮节点解决什么问题？** —— 认识自己（Position）？判断位置（Benchmark）？找到资源（Connection）？获得机会（Marketplace）？提升能力（Growth）？建立信任（Reputation）？预见变化（Future）？
3. **它增加了什么长期记忆？** —— 是否产生可追溯的 Evidence、可积累的 Knowledge、可演化的 Law？如果功能只消费数据而不沉淀记忆，是展示层优化而非 Universe 核心增强。
4. **它是否增强未来连接能力？** —— 节点是否能因为这个功能而更准确地定位自己、更高效地建立连接、更早地发现机会？

四个问题分别对应 Universe 的四个核心价值：

| 问题 | 对应价值 | 工程映射 |
|------|---------|---------|
| 服务哪个节点？ | 存在目的 | Identity / Node Type |
| 解决什么问题？ | Position / Growth / Connection | 07 Chapter 5 三种输出 |
| 增加什么记忆？ | Evidence / Knowledge / Law | 07 Chapter 9 三层认知 |
| 增强连接能力？ | Future Possibility | Observation + Trajectory |

如果四个答案中有三个以上为**否**，该功能大概率属于 UI 优化、流程改进或展示层调整，而非 Universe 核心能力的增强。此类功能可以做，但优先级必须服从于能产生 Position / Growth / Connection / Evidence / Knowledge / Law 增量的特性。

此检查是 7.5（新功能评审过滤器）的必要前置条件：任何功能必须先通过 First Law Check，再进入三层过滤器评审。

## 第九章：Toward Industry World Model（方向，非规范）

### 9.1 Industry World Model（Draft —— 方向，非冻结规范）

GEO Universe 的核心资产不是数据、Agent、地图或规则。

核心资产是**产业世界模型**——一个持续维护产业中身份、关系、演化、信誉、规则和可能性的动态系统。

> 大模型训练通用世界模型（World Model），能够回答各种问题。
> GEO Universe 建立产业世界模型（Industry World Model），持续维护一个会生长的产业宇宙。

**本草案为方向性说明。** 正式的 Industry World Model 文档（`08_GEO_Universe_Industry_World_Model.md`）将在 World Engine 跑通第一个齿轮、积累足够的真实 Observation 数据后独立成文。World Model 不应被设计出来，而应从 Observation 中沉淀出来。

#### World Model 的生成路径

```
Observation（持续观察）
        ↓
Candidate Change（候选变化积累）
        ↓
Event（变化模式识别）
        ↓
Graph（新关系类型涌现）
        ↓
Node Evolution（节点类型分化）
        ↓
World Model（认知结构沉淀）

#### Evidence / Knowledge / Law：Universe 的三层认知

World Engine 的五齿轮表面上流转的是数据，实际上流转的是三种不同性质的东西：

| 层 | 回答的问题 | 产物 | 是否可直接自动化 |
|---|-----------|------|----------------|
| Observation | **发生了什么？** | Evidence（证据） | 大部分可以 |
| Living World Model | **这是什么？** | Knowledge（知识） | 部分可以，需要治理 |
| Universe Rules | **它可以做什么？** | Law（规则） | 不能随意自动改变 |

这三者不是上下级，而是三种不同的责任：

```
Observation（观察世界）
        ↓ produces
Evidence（证据积累）
        ↓ informs
Knowledge（形成认知）
        ↓ constrains
Law（约束行为）
        ↓ governs
Universe（世界运转）
```

- **Evidence** 不是数据，是可追溯的变化记录。Observation 产生它，Memory 保存它。
- **Knowledge** 不是分类，是 Universe 当前已经学会理解世界的方式。Graph 只是 Knowledge 的空间表达——Graph 不是产品，地图不是中心。
- **Law** 不是配置，是 Knowledge 的约束边界。Rule Engine 执行它，Reputation 反映它。

这意味着以后不再说"数据"——Universe 的资产是 Evidence、Knowledge 和 Law 的持续积累。

#### 五齿轮的重新理解

在上述三层模型下，五齿轮真正流动的是：

```
Observation → Event → Knowledge → Memory → Reputation
```

- Graph 不是独立齿轮，是 Knowledge 的空间可视化
- Memory 不是单纯的存储，是 Evidence 的时间沉淀
- Reputation 不是单纯的分数，是 Law 在时间维度上的累积表达

```

World Model 不是 Universe 的输入，是 Universe 的**输出**。它不是一张预设的分类表，而是 Universe 对某个产业**当前认知状态**的结构化表达。每一次 Evolution 都可能重塑它。

### 9.2 可复制性

当产业世界模型成熟后，World Engine 的五个齿轮逻辑可以复制到任何行业：

- 教育宇宙：学校 → 课程 → 技能 → 认证 → 就业机会
- 医疗宇宙：医院 → 医生 → 技术 → 临床试验 → 治疗方案
- 制造宇宙：工厂 → 工艺 → 供应链 → 质量标准 → 产能

复制的不是数据，而是**世界运行机制**。


**`08_GEO_Universe_Industry_World_Model.md`（待创建）：** 将在以下条件满足后独立成文：Observation 管道真实运行、至少数十个真实节点出现、现有节点类型分类已无法容纳新的产业形态。届时，它将不是一个静态分类文档，而是 Industry World Model 的 Living Specification。

这定义了 GEO Universe 的长期愿景：不是做一个 GEO 工具，而是成为 AI 时代产业认知基础设施的参考实现。

---

## 附录：关键术语表

| 术语 | 定义 | 首次出现章节 |
|------|------|-------------|
| World Engine | Universe 的运行机制层，包含五齿轮循环 | 第一章 |
| Candidate Change | Observation 层的输出，描述值得反应的潜在变化 | 第三章 |
| 五齿轮 | Observation / Event / Graph / Memory / Reputation | 第一章 |
| 确定性等级 | Level A（确定）/ B（推断）/ C（规则） | 第四章 |
| Position | 节点在 Universe 中的多维坐标 | 第五章 |
| Trajectory | 节点的阶段变化因果链 | 第五章 |
| Possibility | 基于位置和历史轨迹的可能性空间（非预测） | 第五章 |
| Industry World Model | 持续维护的产业世界动态模型 | 第九章 |
| Living Sandbox | Sprint 5.3-B 产物：人工设计的固定生态 | 第八章 |

---

> *本文档与 00_GEO_Universe_第一性原理.md 同级，属于产品宪章层。*
> *所有后续 Agent 设计、数据管道、定时任务、API 开发必须可追溯至本文档中的运行原理。*
> *修订需经 CTO 审核。*
