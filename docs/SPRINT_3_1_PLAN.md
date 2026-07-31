# Sprint 3.1 商业连接层产品与技术规划

**日期**: 2026-07-29 | **状态**: 规划
**关联**: CTO长期开发协议 §5.5交易市场 / §3.3飞轮 / §4.1 五层架构
**飞轮位置**: 信任 → **连接** → 交易 → 数据

---

## 一、定位与边界

### 1.1 商业连接层是什么

商业连接层是飞轮中「信任→连接」和「连接→交易」之间的桥梁。不替代交易市场，不等同于交易市场。它的核心作用是：

> 让已经认证过的企业和服务商，基于产业知识图谱的能力匹配，自动发现商业机会，形成可信连接，再进入交易市场完成闭环。

### 1.2 边界约束

| 属于 Sprint 3.1 | 不属于（延后/另规划） |
|---|---|
| 服务商实体模型 + 能力标签 | 支付集成 |
| 企业需求发布与匹配 | 完整订单系统 |
| 能力匹配评分引擎 | 合同/发票 |
| 交易评价体系 | 会员定价/套餐 |
| 与 Decision Engine 联动 | 第三方支付网关 |

### 1.3 关联现有资产

| 已有资产 | 在 Sprint 3.1 中的角色 |
|---|---|
| MarketDemand 模型 | 企业需求数据源 |
| Capability 模型 | 服务商能力数据源 |
| Certification 模型 | 服务商可信度输入 |
| Decision Engine | 匹配评分计算 |
| Context Engine | 服务商/企业上下文理解 |
| Evidence / Trust | 匹配结果可信度支撑 |

---

## 二、服务商生态模型

### 2.1 核心问题

目前系统中「企业」通过 Company + Entity 表达，但「服务商」没有独立的领域模型。服务商不是企业的子类型，而是一种独立的生态角色——一个企业可以同时是需求方（作为企业）和供给方（作为服务商）。

### 2.2 设计方案：Provider 模型

```
Provider（服务商）
├── entity_id → Entity（关联实体，复用 GEO 数字身份）
├── provider_type: company | individual | team
├── service_categories: JSONB（可服务的品类，对应 MarketDemand.category 枚举）
├── capability_ids: JSONB（关联 Capability 表的具体能力项）
├── certification_id → Certification（关联认证记录）
├── trust_score: Float（从 Trust 模型聚合）
├── geo_score: Float（从 Decision Engine 聚合）
├── completed_orders: Int（历史完成交易数）
├── avg_rating: Float（来自 TransactionReview 聚合）
├── is_verified: Bool（认证状态快捷标记）
├── is_active: Bool（是否接单中）
├── pricing_model: JSONB（定价方式: 固定/按时/按项目，可选价格区间）
└── metadata: JSONB（扩展字段）
```

### 2.3 服务商生命周期

```
注册 → 基础信息
 ↓
认证 → L1 身份认证（可信度提升）
 ↓
能力登记 → 关联 Capability（可被匹配发现）
 ↓
服务定价 → 设置价格/模式（进入交易市场）
 ↓
接单交易 → 完成订单 + 积累评价
 ↓
等级提升 → L2/L3 认证（更多曝光权重）
 ↓
持续运营 → 数据累积反哺 Trust Score
```

---

## 三、企业需求模型

### 3.1 现有资产评估

`MarketDemand` 模型已具备不错的骨架：
- `category`: service/tool/data/knowledge/talent（五类需求）
- `budget_min/max`: 预算范围
- `timeline_days`: 交付周期
- `requirements`: JSONB 灵活需求描述
- `status`: open → in_progress → closed/expired（状态机）
- `matched_providers`: JSONB（已预留给匹配结果）

### 3.2 需要补强的点

| 补强项 | 当前 | 目标 |
|---|---|---|
| 需求-能力映射 | 手动填写 requirements | 从 Capability 分类自动建议匹配标签 |
| GEO 上下文关联 | 无 | 自动关联企业当前 GEO Score、行业位置 |
| 需求可见度 | 无排序 | 按企业认证等级 + 预算范围加权排序 |
| 匹配推荐 | matched_providers 字段空 | Decision Engine 填充匹配服务商 |

### 3.3 需求发布与匹配流程

```
企业发布需求
     │
     ├── 1. 关联企业 GEO 身份
     ├── 2. 选择需求品类 (service/tool/data/knowledge/talent)
     ├── 3. Context Engine 理解企业上下文
     ├── 4. Decision Engine 计算需求优先级权重
     └── 5. 自动建议关联 Capability 标签

能力匹配
     │
     ├── 1. 检索品类匹配的服务商 (Provider 表)
     ├── 2. 匹配 Capability 交集
     ├── 3. 计算 Match Score（权重见 §4）
     ├── 4. 按 Trust Score + Geo Score + 评价 + 预算匹配度排序
     └── 5. 写入 MarketDemand.matched_providers

连接建立
     │
     ├── 服务商收到匹配通知
     ├── 双方可见对方 GEO 身份卡
     └── 进入交易市场 → 订单
```

---

## 四、能力匹配机制

### 4.1 Match Score 公式

```yaml
# config/matching/match_weights.yaml (新建)
match_score:
  weights:
    capability_overlap: 0.30    # 能力标签交集度
    trust_score:      0.25    # 服务商可信度
    geo_score:        0.15    # 服务商 GEO 综合评分
    rating:           0.15    # 历史评价均分
    budget_fit:       0.10    # 预算匹配度 (1 - |实际-预算|/预算)
    certification:    0.05    # 认证等级加成
  thresholds:
    strong_match: 0.75    # 强匹配 → 推送通知
    moderate_match: 0.50  # 中等匹配 → 列表展示
    weak_match: 0.25      # 弱匹配 → 备选池
```

匹配逻辑路径：
```
MarketDemand → Decision Engine.match_providers(demand_id)
     │
     ├── Step 1: 品类筛选
     │   筛选 category 相符的 Provider
     │
     ├── Step 2: 能力交集
     │   计算 demand.requirements ∩ provider.capability_ids
     │
     ├── Step 3: 加权打分
     │   读取 match_weights.yaml → 逐项计算 → 合成总分
     │
     ├── Step 4: 排序输出
     │   按 match_score DESC，top N 写入 matched_providers
     │
     └── Step 5: 匹配理由
     │   每个匹配结果附带理由 (可解释性)
```

### 4.2 配置化原则

- 匹配权重全部来自 YAML，不硬编码
- 不同行业可配置不同权重模板
- 加载方式与现有 Decision Engine YAML 一致（ConfigLoader → Decision Engine → API）

---

## 五、与交易市场的数据关系

### 5.1 数据模型关系图

```
Entity (GEO 数字身份)
  │
  ├── Company (企业 → 需求方)
  │     │
  │     ├── Capability (能力标签)
  │     ├── MarketDemand (发布需求)
  │     └── Certification (认证记录)
  │
  └── Provider (服务商 → 供给方)
        │
        ├── Capability (能力标签)
        ├── Certification (认证记录)
        └── MarketDemand.matched_providers (被匹配)

交易市场
  │
  ├── Order (订单 → 连接成立后创建)
  ├── PaymentTransaction (支付 → 暂不开发)
  ├── TransactionReview (评价 → 反哺 Provider.avg_rating)
  └── Subscription (订阅 → 暂不开发)
```

### 5.2 数据流

```
企业发布需求 → MarketDemand
       ↓
Decision Engine 匹配 → 填充 matched_providers
       ↓
服务商浏览 → 查看匹配的需求
       ↓
双方建立连接 → 创建 Order（Sprint 3.2）
       ↓
交易完成 → 创建 TransactionReview
       ↓
评价反哺 → Provider.avg_rating + Trust Score 更新
       ↓
数据沉淀 → Evidence 自动生成 + 飞轮继续
```

### 5.3 与决策引擎的关系

商业连接层本质上是 Decision Engine 的一个新维度——不是新 Engine，而是已有能力的新应用场景：

| Decision Engine 能力 | 在商业连接层中的使用 |
|---|---|
| scoring | Provider GEO Score 作为匹配权重输入 |
| opportunity | 识别企业需求中的商业机会 |
| risk | 评估服务商交付风险 |
| recommendation | 生成匹配推荐理由 |

---

## 六、执行计划

### Phase A: 数据层 (Provider 模型 + Migration)

| 任务 | 输入 | 输出 |
|---|---|---|
| A1: 创建 Provider ORM 模型 | 现有 Entity/Capability/Certification 模型 | models/provider.py |
| A2: 创建 Alembic Migration | Provider 模型 | migration 文件 |
| A3: 创建 Provider Schema | Provider 模型 | schemas/provider.py |
| A4: 创建 Provider API | Schema | api/v1/providers.py (CRUD + list by category) |

### Phase B: 匹配层 (Decision Engine 扩展)

| 任务 | 输入 | 输出 |
|---|---|---|
| B1: 新建 match_weights.yaml | §4.1 公式 | config/matching/match_weights.yaml |
| B2: 创建 MatchingEngine | ConfigLoader + Decision Engine + Provider API | app/decision/matching.py |
| B3: MarketDemand API 扩展 | MatchingEngine | POST /demands/{id}/match（触发匹配） |
| B4: 匹配结果测试 | 测试数据 | test_matching.py |

### Phase C: 前端层 (交易市场真实化)

| 任务 | 输入 | 输出 |
|---|---|---|
| C1: 交易市场首页真实数据 | Provider API + MarketDemand API | marketplace/page.tsx 改写 |
| C2: 需求发布页 | MarketDemand API | marketplace/demand/create |
| C3: 服务商列表页 | Provider API | marketplace/providers/page.tsx |
| C4: 匹配结果展示 | MatchingEngine API | 需求详情页 + 匹配服务商列表 |

### Phase D: 评价闭环

| 任务 | 输入 | 输出 |
|---|---|---|
| D1: TransactionReview API 扩展 | 现有 review 模型 | GET /reviews/by-provider/{id} |
| D2: Provider avg_rating 自动聚合 | 新 review 写入时触发 | SQL 或 Python 计算 |
| D3: 评价反哺 Trust Score | avg_rating + Evidence | Trust 模型增量更新 |

---

## 七、关联设计检查

| 关联项 | 检查方式 | 状态 |
|---|---|---|
| Provider ↔ Entity | entity_id FK，复用 GEO 数字身份 | 设计 |
| Provider ↔ Capability | capability_ids JSONB 关联 | 设计 |
| Provider ↔ Certification | certification_id FK，L3 可进入交易市场 | 设计 |
| MarketDemand ↔ Decision Engine | matched_providers 由 MatchingEngine 填充 | 设计 |
| TransactionReview ↔ Trust | 好评提升 Trust Score | 设计 |
| MarketDemand ↔ Context Engine | 需求发布时自动获取企业上下文 | 设计 |
| 前端 ↔ API | 所有页面走 api lib /api/v1 | 已有规范 |

---

## 八、风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| 服务商冷启动问题（无数据→无匹配→无交易） | 高 | 种子数据预置 5-8 个示范服务商 |
| 匹配质量差导致用户不信任 | 中 | 匹配理由可解释 + YAML 权重可调 |
| Provider/Company 边界模糊导致数据冗余 | 中 | 领域原则：同一 Entity 可同时有 Company 和 Provider 角色 |
| 过早开发支付导致重心偏移 | 低 | 明确 Order 属于 Sprint 3.2，Payment 属于 Sprint 4.0 |

---

## 九、CTO 协议符合性检查

| CTO协议要求 | 如何符合 |
|---|---|
| 服务哪个角色？ | 企业（需求方）、服务商（供给方） |
| 增强五大系统哪个环节？ | 交易市场（连接→交易段） |
| 增强知识图谱/Context/Decision？ | Decision Engine 新增 matching 维度 |
| 禁止硬编码 | 匹配权重全部 YAML 化 |
| 禁止重复建设 | 复用已有 Entity/Capability/Decision，不新建 Engine |
| 不替代交易市场 | 商业连接层是桥梁，Order/Payment 延后 |

---

## 十、术语表

| 术语 | 定义 |
|---|---|
| 商业连接层 | 飞轮「信任→连接→交易」中负责能力匹配和商业机会发现的层 |
| Provider | 服务商实体，复用 GEO 数字身份，在生态中提供 GEO 相关服务 |
| MarketDemand | 企业发布的需求，五类品类，含预算/周期/要求 |
| Match Score | 由 Decision Engine 驱动的多维加权匹配评分 |
| TransactionReview | 交易完成后双方互评，反哺 Trust Score |
