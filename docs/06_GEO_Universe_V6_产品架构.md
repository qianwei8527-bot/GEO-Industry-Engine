---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-30
parent: 05_GEO_Universe_V6_能力地图.md
role: architecture document (bridges philosophy to implementation)
---

# GEO Universe V6 产品架构

> 不是功能列表。不是页面清单。是 Universe 三层能力在代码、数据、API 和前端中的实现方式。
> 本文档桥接 00-05 号顶层文档与当前代码库：它定义 Universe 如何实现，而不只是 Universe 有什么能力。

---

## 第零章：文档定位

### 前序文档链

```
00_GEO_Universe_第一性原理.md      → 为什么 Universe 存在
01_GEO_Universe_产品哲学.md        → Universe 相信什么
02_Universe_世界规则.md           → 世界如何运行
03_Universe_Dynamic_Evolution.md  → 时间维度如何演化
04_Universe_UI_Design.md          → 用户如何感知
05_GEO_Universe_V6_能力地图.md    → Universe 有什么能力
06_GEO_Universe_V6_产品架构.md    → ← 本文档：如何实现
```

### 本文档的职责

定义：
- V6 三层能力体系在代码中的实现方式
- 数据模型如何映射到能力层
- API 端点如何服务能力
- 前端页面如何承载能力
- 从旧模块到 V6 的迁移路径
- 下一阶段 Sprint 的开发顺序

不定义：哲学原则（见 00/01）、世界规则（见 02）、视觉规范（见 04）。

---

## 第一章：系统分层架构

### 1.1 完整分层

```
                       用户入口层
                    (Identity Center)
                           |
            ┌──────────────┼──────────────┐
            |              |              |
        Universe Views   Position      Connection
        (5 View切换)     Engine        Network
            |           (检测+定位)     (市场+匹配)
            |              |              |
    ┌───────┴───────┐      |              |
    |               |      |              |
 生态视图 商业视图  成长视图 分布视图 未来视图
    |               |      |              |
    └───────┬───────┘      |              |
            |              |              |
        Intelligence Panel (7-tab 智能面板)
            |              |              |
    ┌───────┴───────┬──────┴──────┬───────┘
    |               |             |
Universe Memory  Growth Engine  Reputation
  (数据资产)      (成长路径)     Layer(信誉)
    |               |             |
    └───────┬───────┴──────┬──────┘
            |              |
        AI Decision Engine (Agent OS)
            |              |
    ┌───────┴───────┬──────┴──────┐
    |       |       |      |       |
 Context  Decision Evidence Match Provider Industry
 Engine   Engine   Tool    Tool  Tool     Tool
    |       |       |      |       |
    └───────┴───────┴──────┴───────┘
            |
    ┌───────┴───────┐
    |               |
Dynamic Graph   Node Evolution
  (动态图谱)     (节点生命周期)
    |               |
    └───────┬───────┘
            |
    Universe Rule Engine (Layer 0)
    ┌──────────────────────────┐
    | R01 Capability-Evidence  |
    | R02 AI Recommendation    |
    | R03 Map Auto-Evolution   |
    | R04 Growth Path          |
    | R05 Five Views = One     |
    | R06 Node as Center       |
    | R07 Marketplace Found.   |
    | R08 Reputation Immutable |
    | R09 Evidence Weight      |
    | R10 AI Accelerated       |
    └──────────────────────────┘
            |
    ┌───────┴───────┐
    |               |
  数据层 (PostgreSQL)  文件存储层
    |               |
  Entity/Company   Evidence Files
  Provider/Industry Certification Docs
  Capability/Evidence ...
```

### 1.2 三层对应关系

| 架构层 | 对应能力层 | 对应第一性原理 | 对应规则编号 |
|--------|-----------|---------------|-------------|
| Universe Views + Position Engine | 世界认知层 (Perception) | Position | R05, R06 |
| Universe Memory + Growth Engine + AI Decision + Reputation | 智能增长层 (Growth) | Growth | R01, R02, R04, R08, R09 |
| Connection Network + Ecosystem | 价值连接层 (Connection) | Connection | R07 |
| Dynamic Graph + Node Evolution | 时间维度 | (Position 的第四维) | R03 |
| Universe Rule Engine | 基础层 | (所有原则的机器化) | R01-R10 |

### 1.3 数据流向

```
用户行为 / 外部数据
        |
        v
  GeoEvent (事件采集)
        |
        v
  Rule Engine 触发检查
        |
   ┌────┴────┐
   |         |
Dynamic    Node
Graph     Evolution
   |         |
   └────┬────┘
        |
  Map Update Trigger
        |
   ┌────┴────┐
   |         |
Universe   Intelligence
Memory     Panel Refresh
   |         |
   └────┬────┘
        |
  用户可见变化
```

---

## 第二章：数据架构

### 2.1 V6 数据模型全景

当前已有的 28 个模型按 V6 能力层重新分组：

#### 世界认知层模型 (Perception Layer)

| 模型 | 表名 | V6 能力 | 状态 | 说明 |
|------|------|--------|------|------|
| Entity | entities | 节点基类（Identity Center 核心） | ✅ 已有 | 所有节点的抽象父表 |
| Company | companies | Position Engine 的企业定位 | ✅ 已有 | 继承 Entity 的企业节点 |
| Provider | providers | Position Engine 的服务商定位 | ✅ 已有 | 继承 Entity 的服务商节点 |
| Industry | industries | Universe Views 的产业维度 | ✅ 已有 | 行业分类与层次 |
| Capability | capabilities | Position Engine 的能力坐标 | ✅ 已有 | 企业和 Provider 的能力标签 |
| Competitor | competitors | Position Engine 的竞争坐标 | ✅ 已有 | 企业间竞争关系 |
| GrowthStage | growth_stages | Position Engine 的时间坐标 | ✅ 已有 | 企业/Provider 的成长阶段 |

#### 智能增长层模型 (Growth Layer)

| 模型 | 表名 | V6 能力 | 状态 | 说明 |
|------|------|--------|------|------|
| Evidence | evidences | Universe Memory 的证据存储 | ✅ 已有 | 可追溯的数据资产证据 |
| Relationship | relationships | Growth Engine 的关系数据 | ✅ 已有 | 节点间关系（competitor/partner/supplier等） |
| GeoEvent | geo_events | Dynamic Graph 的事件驱动 | ✅ 已有 | 触发图变化的产业事件 |
| Reputation | reputations | Reputation Layer 的信誉记录 | ✅ 已有 | 不可篡改的信誉评分历史 |
| Trust | trusts | Reputation Layer 的信任计算 | ✅ 已有 | 信任度评分模型 |
| Certification | certifications | Reputation Layer 的认证记录 | ✅ 已有 | 第三方认证 |
| AgentCallLog | agent_call_logs | AI Decision 的调用记录 | ✅ 已有 | Agent 调用审计日志 |
| AgentMemory | agent_memories | AI Decision 的长期记忆 | ✅ 已有 | Agent 跨任务记忆 |
| AnalyticsEvent | analytics_events | AI Decision 的分析事件 | ✅ 已有 | 用户行为分析事件 |

#### 价值连接层模型 (Connection Layer)

| 模型 | 表名 | V6 能力 | 状态 | 说明 |
|------|------|--------|------|------|
| ProviderCapability | provider_capabilities | Connection Network 的能力匹配 | ✅ 已有 | Provider 能力多对多 |
| MatchResult | match_results | Connection Network 的匹配结果 | ✅ 已有 | 需求-能力匹配输出 |
| MarketDemand | market_demands | Connection Network 的需求发布 | ✅ 已有 | 企业发布的需求 |
| Order | orders | Connection Network 的交易记录 | ✅ 已有 | 交易/服务订单 |
| PaymentTransaction | payment_transactions | Connection Network 的支付记录 | ✅ 已有 | 支付流水 |
| TransactionReview | transaction_reviews | Connection Network 的评价记录 | ✅ 已有 | 交易后评价 |
| ValueChain | value_chains | Ecosystem 的价值链数据 | ✅ 已有 | 产业价值链位置 |

#### V6 待新增模型

| 模型 | 表名 | V6 能力 | 优先级 | 说明 |
|------|------|--------|--------|------|
| NodeSnapshot | node_snapshots | Node Evolution | P0 | 节点历史快照，支持生命周期回放 |
| GeoObservation | geo_observations | AI Observation | P1 | AI 持续观察产业的发现日志 |
| IdentityProfile | identity_profiles | Identity Center | P1 | 用户身份配置（企业/个人/服务商/投资者） |
| ConnectionRequest | connection_requests | Connection Network | P2 | 企业间连接请求（替代简单 order） |

### 2.2 模型与 Universe Rules 的绑定

每个模型的核心字段必须可追溯至 Universe Rule：

| 模型关键字段 | 对应规则 | 计算/更新方式 |
|-------------|---------|-------------|
| Company.geo_score | R02 | evidence 数量 × 质量 + capability 覆盖率 + relationship 密度 |
| Evidence.weight | R09 | 来源权威度 × 时间衰减 × 验证状态 |
| Reputation.score | R08 | 不可篡改：只追加不修改，每次变化生成 audit log |
| ProviderCapability.match_score | R02 | 能力匹配度 + 证据完整性 + 信誉分数 + 关系 + 近期动态 |
| GrowthStage.current_stage | R04 | 根据 evidence_count, geo_score, certification_count, relationship_count 自动判定 |
| GeoEvent → Map update | R03 | 事件触发 map_update_trigger → Dynamic Graph 重算 |

### 2.3 数据库 Migration 策略

当前 Alembic migration 状态：
- 基线：schema_freeze_baseline（核心 Domain 冻结）
- 新增：provider_capability, match_results
- V6 新增模型走独立 migration 版本

Migation 原则：
- 只追加，不修改已有字段（破坏性变更走独立 migration + 数据迁移脚本）
- 每个 V6 新模型对应一个 alembic version
- 生产环境 migration 需人工审批，开发环境自动执行

---

## 第三章：API 架构

### 3.1 V6 API 全景

当前 20+ 端点按 V6 能力层重新分组：

#### Perception Layer APIs (世界认知层 /api/v1/)

| 端点 | 方法 | 当前路由 | V6 能力 | 状态 |
|------|------|---------|--------|------|
| 企业列表/详情 | GET | /companies, /companies/{id} | Position Engine | ✅ 验证通过 |
| 服务商列表/详情 | GET | /providers, /providers/{id} | Position Engine | ✅ 验证通过 |
| 行业列表/详情 | GET | /industries, /industries/{id} | Universe Views | ✅ 验证通过 |
| 企业检测 | POST | /detection/* | Position Engine | ✅ 验证通过 |
| 竞争对比 | GET | /intelligence/competitors | Position Engine | ✅ 增强版已上线 |
| 图谱查询 | GET | /graph/* | Universe Views | ✅ 验证通过 |
| Universe Rules | GET | /universe/rules | Layer 0 | ✅ 验证通过 |
| Intelligence Panel | GET | /universe/panel/{type}/{id} | Universe Views | ✅ 验证通过 |
| 实体通用查询 | GET | /entities | Identity Center | ✅ 验证通过 |
| GeoEvent 列表 | GET | /geo-events | Dynamic Graph | 🟡 待增强 |

#### Growth Layer APIs (智能增长层 /api/v1/)

| 端点 | 方法 | 当前路由 | V6 能力 | 状态 |
|------|------|---------|--------|------|
| Evidence CRUD | GET/POST | /evidence | Universe Memory | ✅ 验证通过 |
| Context 生成 | POST | /context/* | AI Decision | ✅ 验证通过 |
| Decision 执行 | POST | /decision/* | AI Decision | ✅ 验证通过 |
| Agent 调用 | POST | /agent/* | AI Decision | ✅ 验证通过 |
| 认证管理 | GET/POST | /certification/* | Reputation Layer | ✅ 验证通过 |
| 分析事件 | GET | /analytics | Growth Engine | ✅ 验证通过 |
| 数据资产 | GET | /assets | Universe Memory | ✅ 验证通过 |

#### Connection Layer APIs (价值连接层 /api/v1/)

| 端点 | 方法 | 当前路由 | V6 能力 | 状态 |
|------|------|---------|--------|------|
| 服务商匹配 | POST | /marketplace/match | Connection Network | ✅ 验证通过 |
| 需求发布 | GET/POST | /marketplace/demands | Connection Network | ✅ 验证通过 |
| 关系管理 | GET/POST | /relationships | Ecosystem | ✅ 验证通过 |
| 支付/订阅 | * | /payments/*, /subscriptions/* | Connection Network | 🟡 基础可用 |

### 3.2 V6 需要新增/调整的 API

| 端点 | 方法 | 优先级 | 说明 |
|------|------|--------|------|
| /api/v1/universe/node/{id}/snapshots | GET | P0 | 节点历史快照（Node Evolution） |
| /api/v1/universe/observations | GET | P1 | AI 观察发现列表 |
| /api/v1/universe/identity/profile | GET/PUT | P1 | 用户身份配置 |
| /api/v1/universe/connection/request | POST | P2 | 连接请求（替代简单 order） |
| /api/v1/universe/node/{id}/evolution | GET | P0 | 节点生命周期完整轨迹 |

### 3.3 API 设计约束（来自产品哲学）

1. **所有 Agent 输出必须包含 Rule Citation**：每个 response 中的 citations 数组引用 Universe Rule ID
2. **平台不替用户决策**：匹配结果返回 candidates[] 而非 recommended
3. **Evidence 先行**：任何评分/推荐必须附带可追溯的证据链
4. **Universe Rules 是 API 的验证层**：决策端点必须通过 Rule Engine 的 validate 检查
5. **不新增独立于三层之外的 API**：每个新端点必须归属于 Perception/Growth/Connection 其中之一

---

## 第四章：前端架构

### 4.1 V6 页面全景

当前 20+ 页面按 V6 能力层重新分组：

#### 世界认知层页面

| 页面 | 路由 | V6 能力 | 组件 | 状态 |
|------|------|--------|------|------|
| 首页(Identity入口) | / | Position 入口 | 三层认知入口 | ✅ 已更新为 GEO Universe 品牌 |
| Universe Views | /navigation | Universe Views | 5 View 联动切换 | ✅ 已修复中文 + 对接 Universe API |
| Position Engine(检测) | /detection | Position Engine | 实体输入 → 定位 | ✅ 验证通过 |
| 检测结果 | /detection/result | Position Engine | 5 维坐标 + AI 诊断 | ✅ 已增加 AI 诊断 tab |
| 竞争对比 | /detection/compare | Position Engine | 双企业对比分析 | ✅ 增强版（含 Evidence Gap） |
| 企业详情 | /company/[id] | Node Identity | 7-tab IntelligencePanel | ✅ 已对接 /universe/panel API |
| 企业竞争分析 | /intelligence/competitors | Position Engine | 竞争矩阵 | ✅ 验证通过 |

#### 智能增长层页面

| 页面 | 路由 | V6 能力 | 组件 | 状态 |
|------|------|--------|------|------|
| 数据资产 | /assets | Universe Memory | 资产列表 | ✅ 验证通过 |
| Intelligence 面板 | /intelligence | AI Decision | Agent 调用入口 | ✅ 布局+路由就绪 |
| 情报详情 | /intelligence/[id] | AI Decision | Agent 结果展示 | ✅ 验证通过 |
| 认证中心 | /certification | Reputation Layer | 认证流程 | ✅ 验证通过 |
| Admin 治理 | /admin | 所有层 | 配置管理后台 | ✅ 验证通过 |

#### 价值连接层页面

| 页面 | 路由 | V6 能力 | 组件 | 状态 |
|------|------|--------|------|------|
| Marketplace | /marketplace | Connection Network | 候选服务商浏览 | ✅ 验证通过 |
| Provider 详情 | /marketplace/provider/[id] | Connection Network | 能力详情卡片 | 🟡 待增强 |
| Demand 发布 | /marketplace/demand | Connection Network | 需求发布表单 | ✅ 验证通过 |
| 商业机会 | /intelligence/opportunities | Connection Network | 机会推荐 | ✅ 验证通过 |

### 4.2 V6 需要新增/重构的页面

| 页面 | 优先级 | 路由建议 | 说明 |
|------|--------|---------|------|
| Identity Center（重构首页） | P0 | / | 身份选择 → 个性化 Universe 入口（当前已是三层认知入口，需增加身份选择器） |
| Node Evolution Timeline | P0 | 集成在 IntelligencePanel | 节点生命周期可视化（新 tab） |
| Dynamic Graph 播放器 | P1 | /universe/dynamic | 关系网络的时间回放 |
| AI Observation Feed | P1 | /universe/observations | AI 持续观察发现的时间线 |
| Connection Request 流程 | P2 | /connection/request | 企业间连接请求的端到端流程 |
| Growth Engine 独立入口 | P1 | /growth | 成长路径规划与追踪 |

### 4.3 前端组件架构

```
components/
├── AgentInsight.tsx        # Agent UI Runtime（已有，对接 Agent API）
├── IntelligencePanel.tsx   # 7-tab 智能面板（已对接 Universe API）
├── Header.tsx              # GEO Universe 品牌导航
├── Footer.tsx
├── PageHeader.tsx
├── LoadingSpinner.tsx
└── (V6 新增)
    ├── IdentitySelector.tsx     # P0: 身份选择组件
    ├── UniverseViewCanvas.tsx   # P0: 5 View 联动画布
    ├── NodeEvolutionChart.tsx   # P0: 节点生命周期图
    ├── DynamicGraphTimeline.tsx # P1: 动态图谱时间轴
    ├── RuleCitationBadge.tsx    # P1: Rule 引用徽章
    └── ConnectionCard.tsx       # P2: 连接请求卡片
```

### 4.4 前端设计约束

1. **Header 统一命名**：GEO Universe（非 GEO-Industry-Engine）
2. **导航命名统一**：产业宇宙/认证/市场/资产/情报
3. **IntelligencePanel 7 tab**：身份/评分/能力/报告/关系/证据/事件（每个类型权重不同）
4. **5 View 联动**：节点在任一 View 选中，所有 View 联动高亮
5. **所有 Agent 输出必须使用 AgentInsight 组件包裹**（确保 Citation、Memory、Log 统一）

---

## 第五章：Agent 架构

### 5.1 Agent OS 当前状态

```
                  Agent Runtime (6 Agent + 6 Tool)
                       |
        ┌──────────────┼──────────────┐
        │              │              │
   Context Tool   Decision Tool   Industry Tool
        │              │              │
   Evidence Tool  Provider Tool   Match Tool
        │              │              │
        └──────────────┴──────────────┘
                       |
              Role Agent (6 个全部注册)
       ┌───────────┬───┴───┬───────────┐
       |           |       |           |
IndustryAnalyst  Company  GEOGrowth  DataAnalyst
              Intelligence
       |                       |
EnterpriseDiagnostician   ProviderMatcher
```

### 5.2 Agent 列表与 V6 能力映射

| Agent | V6 能力 | 输入 | 输出 | 引用规则 |
|-------|--------|------|------|---------|
| IndustryAnalyst | Universe Views | 行业 ID | 产业趋势分析 | R03, R05 |
| CompanyIntelligence | Position Engine | 企业 ID | 企业定位报告 | R02, R06 |
| GEOGrowth | Growth Engine | 企业 ID | 成长路径建议 | R01, R04 |
| DataAnalyst | Universe Memory | 查询条件 | 数据分析报告 | R09 |
| EnterpriseDiagnostician | Position + Growth | 企业 ID | 诊断报告 + 候选服务商 | R01, R02, R04 |
| ProviderMatcher | Connection Network | 需求描述 | 候选服务商集合 | R02, R07 |

### 5.3 Agent 设计约束

1. **每个 Agent 必须引用 Universe Rules**：不是自由生成，是解释规则在当前情境中的适用
2. **Agent 不创造事实**：Context Engine 负责数据，Agent 负责解释
3. **Agent 不替用户决策**：ProviderMatcher 返回 candidates[]，不是 recommended
4. **所有 Agent 输出必须可追溯**：Citation Layer 保证每个结论都能追溯到 Evidence
5. **AgentCallLog 记录每次调用**：为未来 Agent 质量分析和优化提供数据

### 5.4 V6 Agent 扩展计划

| 优先级 | 新 Agent | V6 能力 | 说明 |
|--------|---------|--------|------|
| P1 | ObservationAgent | AI Observation | 每日扫描产业变化，发现新赛道/新节点/新关系 |
| P1 | EvolutionAgent | Node Evolution | 分析节点生命周期，预测成长/衰退趋势 |
| P2 | EcosystemAgent | Ecosystem Engine | 分析网络效应，发现生态关键节点 |
| P2 | ReputationAuditor | Reputation Layer | 持续验证信誉数据的真实性和时效性 |

---

## 第六章：Universe Rules 集成

### 6.1 Rules 在系统中的位置

Universe Rules 不是文档，是代码中的执行层：

```
config/universe/rules.yaml         ← 规则定义（YAML）
        |
        v
backend/app/universe/rules.py     ← Rule Engine（Python 加载器）
        |
        v
    ┌───┴───┐
    |       |
API 层     Agent 层
    |       |
/universe  Agent 调用时引用规则
/rules     RuleEngine.cite(rule_id)
/validate  RuleEngine.validate()
    |       |
    └───┬───┘
        |
前端 RuleCitationBadge 组件
（Agent 输出中的规则引用可视化）
```

### 6.2 Rule 引用协议

Agent 输出中的每条结论必须附带：

```json
{
  "conclusion": "Trust 不足的主要原因是行业认证缺失",
  "citations": [
    { "rule_id": "R01", "explanation": "缺少认证导致信誉飞轮无法启动" },
    { "rule_id": "R08", "explanation": "信誉不可篡改：认证是唯一的信誉注入方式" }
  ],
  "evidence": [
    { "evidence_id": "uuid", "summary": "0 active certifications" }
  ]
}
```

### 6.3 规则验证层

后端关键决策点（评分计算、匹配算法、成长阶段判定）必须经过 Rule Engine 验证：

```python
engine = get_rule_engine()
result = engine.validate(decision_type="geo_score_calculation", factors={...})
if not result["valid"]:
    # 拒绝或标记为不受信计算
```

---

## 第七章：从旧模块到 V6 的迁移路径

### 7.1 迁移原则

1. **不废弃**：旧模块不是错的，是层级不对。重新定位而非删除。
2. **不新建独立模块**：新功能必须归入三层能力体系。
3. **语义迁移优先于代码重写**：先改名、改文档、改引用，再考虑代码重构。
4. **路由保持兼容**：旧路由 30 天重定向到新路由。

### 7.2 迁移映射表

| 旧模块 | 旧路由 | V6 能力 | V6 路由(建议) | 迁移动作 |
|--------|--------|--------|-------------|---------|
| 产业导航 | /navigation | Universe Views | /universe/views | 改名 + 增加 5 View 联动 |
| 检测中心 | /detection | Position Engine | /position | 改名 + 增加 Identity 入口 |
| 企业中心 | /company/[id] | Node Identity | /universe/node/company/[id] | 路由重构 + 7-tab Panel |
| 数据资产中心 | /assets | Universe Memory | /universe/memory | 改名 + 增加时间深度 |
| 学习成长 | (无独立页) | Growth Engine | /growth | 新建独立能力入口 |
| 认证中心 | /certification | Reputation Layer | /reputation | 改名 + 增加信誉时间轴 |
| 交易市场 | /marketplace | Connection Network | /connection | 改名 + 候选替代推荐 |
| 产业情报 | /intelligence | AI Decision | /intelligence | 保留当前路由，内容增强 |
| Admin | /admin | 治理层 | /admin | 保留，增加 Rule 管理 |

### 7.3 迁移分阶段执行

**Phase 1: 语义对齐（当前已完成）**
- ✅ 文档中的旧名 → 新名映射完成
- ✅ 前端页面标题和导航文案已更新
- 🟡 API 文档标注旧名对应的 V6 能力（待补齐）

**Phase 2: 路由重构（Sprint 5）**
- 前端路由从旧名迁移到 V6 命名
- 保持旧路由 30 天重定向
- API 增加 /api/v1/universe/* 前缀的聚合端点

**Phase 3: 数据模型演进（Sprint 5-6）**
- 新增 NodeSnapshot, GeoObservation 等模型
- Alembic migration 分步执行
- 旧模型字段不做破坏性变更

**Phase 4: 旧文档归档（Sprint 6 后期）**
- 47 个旧文档中保留约 20 个进行语义迁移
- 其余移入 docs/archive/v4/
- 索引更新

---

## 第八章：开发路线图

### 8.1 当前状态

```
GEO-Industry-Engine v0.2-alpha
████████░░ 85%

已完成: 00-06 号顶层文档, Domain Models (28个), API v1 骨架 (20+端点),
       Agent OS (6 Agent + 6 Tool), Universe Rules Engine (10 Rules),
       前端 20+ 页面, Docker Compose, Alembic Migration,
       E2E Flywheel Test (Golden Test)
```

### 8.2 Sprint 5: Universe Views 重构 + Identity Center + Node Evolution

**目标**：让用户第一次进入 Universe 就照见自己。

| 任务 | 优先级 | 说明 |
|------|--------|------|
| Identity Center 首页重构 | P0 | 身份选择 → 个性化 Universe（当前首页已是三层认知入口，在此基础上增加身份选择器） |
| 5 View 联动机制 | P0 | 同一节点在五个 View 中联动高亮（不是 Tab 切换，是 Camera 联动） |
| Node Evolution Timeline | P0 | Intelligence Panel 中增加生命周期视图（第 8 tab） |
| NodeSnapshot 模型 + Migration + API | P0 | 节点历史快照查询 |
| Universe Views 路由重构 | P0 | /navigation → /universe/views |
| 旧模块语义迁移（Phase 2） | P0 | 页面标题、API 端点注释、导航文案全线统一 |

### 8.3 Sprint 6: Growth Engine + AI Observation + 数据增强

**目标**：让 Universe 活起来。

| 任务 | 优先级 | 说明 |
|------|--------|------|
| Dynamic Graph 时间轴 | P1 | 关系网络的创建/变更/失效时间线，支持历史回放 |
| AI Observation Agent | P1 | 每日扫描产业变化，自动发现新赛道/新节点/新关系 |
| GeoObservation 模型 + Migration + API | P1 | AI 观察发现日志存储与查询 |
| Growth Engine 页面 | P1 | 独立的成长路径入口：起点→目标→路径→追踪 |
| Reputation 时间衰减 | P1 | 信誉分数随时间自动衰减，长期无活动/无证据的节点自动降分 |
| RuleCitationBadge 组件 | P1 | Agent 输出中可视化规则引用（显示 R01/R02 等徽章） |
| 真实种子数据增强 | P1 | 1-2 个行业 10-20 家企业的真实 Evidence 数据 |

### 8.4 Sprint 7: Connection Network + Ecosystem + 旧文档清理

**目标**：让企业产生真实商业价值。

| 任务 | 优先级 | 说明 |
|------|--------|------|
| Connection Request 端到端流程 | P2 | 企业间连接请求：发起→审核→确认→交易→评价完整闭环 |
| IdentityProfile 模型 + Migration + API | P2 | 多身份配置支持 |
| EcosystemAgent | P2 | 网络效应分析：识别生态关键节点、中心度排名 |
| ReputationAuditor Agent | P2 | 信誉数据持续验证，标记数据过期或异常 |
| 旧文档归档 | P2 | 47 个 → 保留约 20 个，其余 → archive/v4/ |

### 8.5 新功能 Gate（架构准入规则）

当前不冻结任何架构层。但新功能必须通过 V6 Gate：

1. 归入三层（Perception / Growth / Connection）中的哪一层？
2. 增强 Position / Growth / Connection 中的哪一个命题？
3. 是否引用 Universe Rules？具体哪些 Rule ID？
4. 是否需要新数据模型？是否可复用现有模型？
5. 是否需要新 Agent？是否可组合现有 Agent 实现？

---

## 第九章：旧文档处理策略

### 9.1 当前 70+ 文档状态

| 类别 | 数量 | 处理方式 | 时机 |
|------|------|---------|------|
| V6 顶层文档 (00-06) | 7 | 当前开发依据 | 持续维护 |
| 已被 V6 替代的旧设计 | ~15 | 归档到 archive/v4/ | Sprint 6 后期 |
| 技术参考仍有价值 | ~15 | 语义迁移后保留 | Sprint 6 后期 |
| Sprint 报告（历史记录） | ~12 | 保留，标注 DEPRECATED | Sprint 6 后期 |
| 架构治理/冻结（已废弃） | ~5 | 归档 + 标注 DEPRECATED | 已标注 |
| 混合角色待评估 | ~16 | 逐一评估 | Sprint 6 后期 |

### 9.2 保留并迁移的核心文档

- 02_领域模型设计.md → 更新为 V6 能力数据模型
- 03_数据架构.md → 更新为 Universe Memory 架构
- 04_Agent_OS设计.md → 更新为 AI Decision Engine 架构
- 05_技术架构.md → 更新为 V6 技术架构
- 06_前端信息架构设计.md → 更新为 Universe UI 架构
- 08_API接口规范.md → 更新为 V6 API 规范

### 9.3 归档时机

不立即处理。在 Sprint 6 后期（数据模型稳定后）统一执行。
当前所有旧文档保留原位置，以 DEPRECATED 标记区分。

---

## 第十章：工程约束与执行纪律

### 10.1 继承自 CTO 长期开发协议（v3.2）

- 命名统一：GEO Universe（非 GEO-Industry-Engine）
- 路由前缀：前端 /universe/*，后端 /api/v1/universe/*
- 禁止新增独立于三层之外的系统
- 禁止 Agent 输出不引用 Universe Rule
- 禁止平台替用户做决策（recommended → candidates）

### 10.2 继承自 Universe 世界规则（02）

- 每个节点都是世界中心（R06）
- 五个视角 = 一个 Universe（R05）
- 所有评分/推荐必须有证据链（R09）
- 信誉不可篡改（R08）

### 10.3 继承自产品哲学（01）

- Universe First, AI Accelerated
- Position + Growth + Connection 三维价值
- 生态不与业务协同发展就是找死
- 让用户照见自己，不是让 AI 回答用户

### 10.4 当前不冻结的架构层

以下层级在 V6 期间完全开放修改：

- ✅ 前端路由结构（可重构）
- ✅ 页面组件拆分（可重组）
- ✅ API 端点组织（可重命名）
- ✅ 数据模型字段（可新增，不可删除已有字段）
- ✅ Agent 配置和 Prompt（可迭代）
- ✅ Universe Rules YAML（可追加新规则）
- ✅ 文档体系和命名（可重构）

---

> 本文档是 V6 产品架构的唯一定义。它是 00-05 号顶层文档的工程实现层。
> 架构决策冲突时，优先级：第一性原理(00) > 产品哲学(01) > 世界规则(02) > 能力地图(05) > 产品架构(06)。
> 后续文档：Sprint 5 执行计划（基于本文档第八章的详细任务分解）。
