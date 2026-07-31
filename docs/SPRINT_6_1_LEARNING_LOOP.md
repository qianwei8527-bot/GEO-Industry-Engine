---
status: stable
authority: engineering_record
version: v1.0
date: 2026-07-31
sprint: Sprint 6.1 — Universe Learning Loop
parent: 07_GEO_Universe_World_Engine.md
verified_by: Observation Pipeline Integration Test
---

# Sprint 6.1 Engineering Record: Universe Learning Loop 验证完成

> 这是 GEO Universe 第一次通过 Observation → Evidence → Knowledge 链路，
> 在没有预先定义的前提下，发现了一个此前不存在的概念。

---

## 一、验证目标

**核心假设：** Universe 是否能够在没有预定义概念的情况下，通过 Observation 管道发现新概念，并积累 Evidence 使其成为可识别的 Emerging Pattern？

**不是验证：** API 是否正常工作、数据库是否写入成功。这些是工程基础项。

**是在验证：** `07_World_Engine` 定义的世界运行机制前三个齿轮（Observation → Event → Knowledge）是否在代码层面闭合。

---

## 二、原始假设

从 `07_GEO_Universe_World_Engine.md` 中提取：

```
Reality → Observation → Evidence → Knowledge → Law → Universe
```

Sprint 6.1 验证的是前四步：

```
Reality（外部信号）
    ↓
Observation（摄入）
    ↓
Evidence（CandidateChange 积累）
    ↓
Knowledge（Emerging Pattern 识别）
```

`Law` 和 `Universe` 层不在本次验证范围内。

---

## 三、实现链路

### 3.1 新增组件

| 组件 | 文件 | 职责 |
|------|------|------|
| CandidateChange 模型 | `app/models/candidate_change.py` | Evidence 层的持久化载体 |
| Observation API | `app/api/v1/observation.py` | 信号摄入 + 积累 + 推广端点 |
| GeoEvent 桥接 | 内嵌于 promote 端点 | 将 acknowledged 信号转化为 World Engine 事件 |

### 3.2 数据流（实测）

```
POST /api/v1/observation/ingest  ×5
    signal_label="AI Employee"
    change_type="new_node"
    suggested_node_type="role"
    certainty_level="B"
        ↓
CandidateChange(id=d300f899..., occurrence_count=5, signal_strength=0.5, status=pending)
        ↓
POST /api/v1/observation/signals/{id}/promote
    status="acknowledged"
        ↓
CandidateChange(status=acknowledged)
        ↓
GeoEvent 自动生成：
    event_type="candidate_change_promoted"
    title="New signal acknowledged: AI Employee"
    impact_level="medium"
    impact_score=0.5
        ↓
GET /api/v1/observation/stats
    emerging_patterns=[
        {signal_label: "AI Employee", suggested_node_type: "role",
         occurrence_count: 5, signal_strength: 0.5}
    ]
```

### 3.3 关键设计决策

- **信号积累而非覆盖**：相同 signal_label + change_type 的信号不会创建重复记录，而是递增 occurrence_count 和 signal_strength
- **B 级确定性**：外部 Agent 的信号默认为 Level B（推断变化），需要 accumulate 或 promote 才能进入 World Engine
- **GeoEvent 自动桥接**：promote 到 acknowledged 时自动创建 GeoEvent，不需要手动写 Event 层

---

## 四、当前能力边界

### 已具备

- [x] Observation 端点接受任意来源的信号（agent / user / api / crawler / system）
- [x] 相同信号自动积累（occurrence_count 递增，signal_strength 随积累增长）
- [x] Level A/B/C 确定性分类
- [x] 手动 promote（pending → acknowledged）
- [x] 自动桥接 GeoEvent（acknowledged → World Engine 事件）
- [x] emerging_patterns 统计端点

### 尚未具备

- [ ] 自动积累阈值触发 promote（occurrence_count ≥ N 自动 acknowledged）
- [ ] Knowledge Recognition：区分"observed" / "emerging" / "recognized" / "adopted" 状态
- [ ] Emergence Score：基于 occurrence + persistence + source diversity + impact 的复合评分
- [ ] Law 层：为 recognized 概念自动生成规则提案
- [ ] 前端展示：IntelligencePanel 中 "Universe 正在学习" 视图
- [ ] 虚假趋势过滤：短期热点 vs 真实产业变化的区分

---

## 五、未解决问题

### 5.1 什么信号值得 accumulate？

当前实现：相同 signal_label + change_type 即视为同一信号。但真实场景中，"AI Employee"和"AI 员工"应该是同一个概念。需要概念归并（Concept Resolution）。

**建议（Sprint 6.2）：** 利用 LLM 做信号语义聚类，而非字符串匹配。

### 5.2 积累速度如何控制？

当前实现：每次 POST 递增 1。信号 strength = min(1.0, count / 10)。但一条微博热搜和一篇学术论文不应该有相同的信号权重。

**建议（Sprint 6.2）：** 引入 source_weight（crawler=0.5, academic=0.9, social_media=0.3），signal_strength 基于加权累加而非简单计数。

### 5.3 如何防止 Universe 学会错误的概念？

当前实现：依赖人工 promote。但长期来看，需要自动化的"假趋势检测"。

**建议（Sprint 6.3）：** 引入 persistence_requirement（信号必须持续存在超过 N 天才进入 emerging 状态），以及 source_diversity 检查（至少来自 M 个不同来源）。

---

## 六、对后续文档的影响

### 已确认的设计

- `07_GEO_Universe_World_Engine.md` Chapter 1-3 的五齿轮模型在工程上可行
- Chapter 4 的三级确定性分类（Level A/B/C）在 API 中已实现
- Chapter 9 的"World Model 不是输入而是输出"理念在 emerging_patterns 端点中首次体现

### 需要更新的认知

- `07` Chapter 1.2 的五齿轮定义中，"Knowledge" 齿轮的描述需要从概念层细化：Knowledge 不是单一的"数据库写入"，而是 accumulation → assessment → recognition 的三阶段过程。本次验证覆盖了第一阶段。

---

## 七、Sprint 6.2 设计原则

基于本次验证得出的边界，Sprint 6.2（Knowledge Recognition Layer）应遵循以下原则：

1. **不跳过 Knowledge 直接做 Law。** 需要在 Observation 和 Law 之间建立 Knowledge Assessment 层，包含 observed → emerging → recognized → adopted 的状态机。

2. **Emergence Score 替代简单计数。** 基于 occurrence × persistence × source_diversity × impact 的复合评分决定一个信号是否值得进入 Knowledge 层。

3. **概念归并。** 在 accumulation 阶段引入语义聚类，将不同来源对同一概念的不同表述合并。

4. **保留人工确认入口。** 即使引入自动阈值，Level B 信号的 promote 仍需要可审计的确认路径。

5. **前端不展示"答案"，展示"Universe 正在学习"。** IntelligencePanel 的 emerging 视图应体现"观察中 → 形成中 → 已识别"的过程感，而非直接显示结论。

---

> *本记录是 Sprint 6.1 的工程验证文档。*
> *Sprint 6.2 将从 Knowledge Recognition Layer 开始，在本次验证的边界基础上扩展。*
> *相关架构文档：`07_GEO_Universe_World_Engine.md`，`06_GEO_Universe_V6_产品架构.md`*
---

## 附录：Genesis Observation Record

> GEO Universe 第一条 Learning Loop 样本。不是 API 测试数据，是 Universe 第一次证明自己可以在没有预定义概念的前提下，发现、积累并暴露一个未知信号。

### 概念标识

| 字段 | 值 |
|------|-----|
| 概念名 | AI Employee |
| 信号标签 | `signal_label="AI Employee"` |
| 变化类型 | `change_type="new_node"` |
| 建议节点类型 | `suggested_node_type="role"` |
| 数据来源 | `source_type=experiment` |
| 实验标识 | `experiment_name=sprint_6_1_learning_loop` |
| 确定性 | `certainty_level=B`（推断变化） |

### 时间线

| 事件 | 时间 | 状态 |
|------|------|------|
| 首次观察 | 2026-07-31 | 1 signal, strength=0.1 |
| 积累至 5 | 2026-07-31 | 5 signals, strength=0.5 |
| Promote | 2026-07-31 | status=acknowledged |
| GeoEvent 生成 | 2026-07-31 | event_type=candidate_change_promoted |

### 当前 Universe 状态

| 维度 | 状态 |
|------|------|
| Observation 层 | 5 条信号已摄入，Evidence 已积累 |
| Knowledge 层 | Emerging Pattern 已识别，但未 Recognition |
| World Model | 尚未创建 "AI Employee" 节点类型 |
| Law 层 | 尚未定义能力边界 |
| Universe 状态 | Observing（正在观察） |

### 保护规则

- 此记录标记为 `source_type=experiment`，不会被误认为生产数据
- 在 Knowledge Recognition 完成之前，不创建 AI Employee 节点、不分配 IdentityProfile、不计算 Reputation
- 未来 World Engine 回归测试以此记录为第一条 fixture
