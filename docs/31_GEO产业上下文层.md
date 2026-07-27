---
status: stable
authority: primary
version: v2.0
last_review: 2026-07-27
related_docs: [02, 16, 04]
---
﻿# GEO产业上下文层（Industry Context Layer）

> AI理解产业世界的上下文基础设施 — GEO-Industry-Engine的终极架构层。

---

## 一、定位：AI时代的产业上下文基础设施

未来AI的最大缺口不是智力，而是**产业实时上下文**。

通用大模型知道"什么是AI营销"，但不知道：
- 哪些公司**真正做过**AI营销项目
- 哪些公司**效果好、可信**
- 哪些公司**正在增长**，适合特定行业需求
- 这个行业**昨天和今天**发生了什么变化

GEO-Industry-Engine的终极定位是成为**连接AI与真实产业世界的上下文层（Context Layer）**——AI Agent通过调用GEO获取产业决策所需的实体、能力、信任、历史、意图等关键上下文。

`
      AI Agent / MCP Client
            │
            ▼
  ┌─────────────────────┐
  │  GEO Context Layer   │  ← 本文件
  ├─────────────────────┤
  │  GEO Industry Kernel │  ← 26_GEO产业内核与开放协议.md
  ├─────────────────────┤
  │  产业数据层           │
  └─────────────────────┘
`

这**不是**替代AI，而是给AI一个"产业世界的接口"。模型提供推理能力，GEO提供推理所需的产业事实。

---

## 二、Context Engine（上下文引擎）

Context Engine**不是**产业内核的第7个引擎。它是产业内核之上的**封装与编排层**，负责：

1. 接收AI Agent的上下文请求（自然语言或结构化）
2. 解析请求，确定需要哪些维度
3. 从产业内核的6个引擎中抽取对应数据
4. 组装为结构化的上下文响应（JSON格式，优化AI消费）

### 7个上下文维度

| 维度 | 回答的问题 | 依赖的内核引擎 |
|------|-----------|--------------|
| Entity Context | 这是谁？在产业中处于什么位置？ | Entity Engine |
| Capability Context | 能做什么？哪些能力经过验证？ | Capability Engine |
| Industry Context | 处于产业链的哪个环节？上下游是谁？ | Relationship Engine + Evolution Engine |
| Trust Context | 可信吗？证据是什么？ | Value Engine + 证据图谱 |
| Historical Context | 过去经历了什么？如何演化至此？ | Evolution Engine + 产业记忆 |
| Intent Context | 用户真正需要什么？ | Recommendation Engine |
| Decision Context | 如何选择？为什么推荐A不推荐B？ | Value Engine + Recommendation Engine |

### 请求处理流程

`
请求（自然语言 / 结构化）
  │
  ▼
Context Engine
  ├── 意图识别 → 确定需要哪些上下文维度
  ├── 内核编排 → 调用对应引擎获取原始数据
  ├── 证据组装 → 为每个结论附上证据来源与可信等级
  └── 响应生成 → 结构化上下文（AI消费优化格式）
  │
  ▼
结构化上下文响应
`

### 与内核引擎的协作示例

`
AI Agent: "推荐一家适合中型制造企业做AI升级的公司"

Context Engine 处理：
  1. Intent Context 识别 → 行业=制造, 需求=AI转型, 预算=中型
  2. Entity Engine → 检索匹配行业的公司池
  3. Capability Engine → 筛选具备"制造AI改造能力"的公司
  4. Value Engine → 评估商业价值匹配度
  5. Trust Context → 获取信任评分与证据
  6. ══ 组装 → 候选列表+推荐理由+证据链
`

---

## 三、Context API（面向AI Agent的上下文接口）

所有 Context API 专为AI Agent消费设计，返回结构化JSON，附证据链和置信度。

### 企业上下文

`
GET /api/v1/context/company/{geo_id}

Response:
{
  "entity": {
    "geo_id": "GEO-COMPANY-000001",
    "name": "某AI科技公司",
    "industry_position": "医疗AI - 智能诊断 - 中高端",
    "verified_capabilities": [
      {"name": "AI辅助诊断系统", "level": "L3", "evidence": "完成3家三甲医院部署"}
    ]
  },
  "trust": {
    "score": 88,
    "evidence_count": 15,
    "certifications": ["GEO企业认证L2"],
    "data_confidence": "Level 3 - 第三方验证"
  },
  "market_position": {
    "rank_in_industry": "top 15%",
    "growing_capabilities": ["多模态分析"],
    "risk_factors": ["区域市场集中度过高"]
  },
  "historical": {
    "evolution_path": ["2024: 传统AI公司", "2025: 转型医疗AI", "2026: 医疗AI头部"],
    "key_events": ["2025-06: 完成B轮融资", "2026-03: 获GEO认证L2"]
  }
}
`

### 行业上下文

`
GET /api/v1/context/industry/{industry_id}

Response:
{
  "industry": {
    "name": "医疗AI",
    "total_companies": 320,
    "growth_rate": "35% YoY",
    "hot_sub_sectors": ["AI诊断", "智能病历", "药物发现"]
  },
  "opportunities": [
    {"sector": "基层医疗AI化", "gap": "缺少适合中小医院的轻量方案", "urgency": "high"}
  ],
  "talent_demand": {
    "hottest_role": "医疗AI产品经理",
    "supply_gap": "30%"
  }
}
`

### 决策上下文

`
POST /api/v1/context/decision

Request:
{
  "goal": "enter_market",
  "industry": "robotics",
  "company_profile": {"capabilities": ["计算机视觉", "机器人控制"]}
}

Response:
{
  "recommended_path": "工业视觉检测 → 仓储机器人 → 人机协作",
  "entry_barrier": "中（需要制造业客户基础）",
  "key_partners": [
    {"name": "某制造企业", "match_reason": "已有产线AI升级需求"}
  ],
  "risks": [
    {"factor": "头部企业已建立品牌优势", "mitigation": "专注于细分场景"}
  ]
}
`

### 能力匹配上下文

`
POST /api/v1/context/match

Request:
{
  "requirement": "需要医疗行业AI客服解决方案",
  "conditions": {"region": "华东", "budget": "中型"}
}

Response:
{
  "candidates": [
    {
      "company": "某AI公司",
      "match_score": 92,
      "trust_score": 85,
      "evidence": ["完成3家三甲医院部署", "GEO认证L2"]
    }
  ],
  "market_context": {
    "similar_projects": 45,
    "avg_success_rate": "78%",
    "price_range": "30-80万"
  }
}
`

---

## 四、GEO作为MCP Industry Server

未来AI Agent之间的通信标准正在向MCP（Model Context Protocol）收敛。GEO应成为：

### GEO Industry MCP Server

AI Agent获取产业信息的**标准入口**。

`
AI Agent
  │  MCP
  ▼
GEO Industry MCP Server    ← 开放协议层的新成员
  │  查询：行业信息、企业信息、能力匹配、信任评价
  ▼
GEO Context Engine
  │  Industry Kernel调用
  ▼
产业知识图谱 + 产业记忆
`

### 注册的MCP工具

| MCP Tool | 用途 | 输入 | 输出 |
|----------|------|------|------|
| geo__search_company | 搜索企业 | name, industry, region | 企业上下文 |
| geo__search_industry | 搜索行业 | industry_name, scope | 行业上下文 |
| geo__match_capability | 能力匹配 | requirement, conditions | 候选列表+匹配评分 |
| geo__evaluate_trust | 可信评估 | company_id | 信任评分+证据链 |
| geo__get_industry_trend | 行业趋势 | industry, time_range | 趋势分析+预测 |
| geo__get_decision_support | 决策支持 | goal, context | 决策建议+风险提示 |
| geo__get_company_evolution | 企业演化 | company_id | 企业演化路径+关键事件 |

MCP Server 作为开放协议家族的新成员，与 GEO Entity Protocol、GEO Data Protocol 等并列。

---

## 五、Industry Memory（产业记忆）

每个AI Agent需要长期记忆，但单个Agent的记忆是私有的、碎片化的。

GEO提供的是**共享的、权威的产业记忆**——记录产业世界随时间发生的变化。

### 产业记忆的类型

| 记忆类型 | 内容 | 用途 |
|----------|------|------|
| 企业演化路径 | 企业的转型、扩张、衰退、并购记录 | Agent理解企业当前状态 |
| 产业事件流 | 融资、并购、政策发布、产品发布、合作签约 | Agent实时感知产业变化 |
| 关系变化记录 | 合作关系的新建与中断、供应链变化 | Agent判断产业动态 |
| AI推荐变化 | AI对企业的推荐频率、位置、语境变化 | Agent跟踪可见度趋势 |
| 人才流动 | 关键人才在不同企业/行业间的迁移 | Agent判断行业热度 |

### Agent如何调用产业记忆

`python
# Agent伪代码示例
industry_memory = geo_context.memory.get(
    entity="GEO-COMPANY-000001",
    time_range="2024-2026",
    memory_types=["evolution", "events", "recommendation"]
)
# 返回：这家企业过去两年的演化路径、关键事件、AI推荐变化曲线
`

### Industry Memory vs 传统Agent Memory

| 维度 | 传统Agent Memory | GEO Industry Memory |
|------|-----------------|-------------------|
| 所有者 | 单个Agent | 全平台共享 |
| 内容来源 | Agent自身对话 | 产业级数据采集+社区贡献 |
| 权威性 | 无验证 | 数据来源分级+交叉验证 |
| 时间跨度 | 会话级别 | 年/十年级别 |
| 访问权限 | 私有 | 平台级可查询 |

---

## 六、减少AI幻觉（Context Layer的信任锚点）

GEO不替代AI生成，而是为AI生成**提供事实锚点**。

| AI面对的问题 | GEO提供的解决方案 |
|-------------|-----------------|
| 不知道某企业是否存在 | GEO Entity ID + 可信企业库 |
| 不确定企业能力是否真实 | Capability Engine + 证据图谱（数据来源Level 0-4） |
| 不了解行业最新动态 | Industry Memory + 实时事件流 |
| 无法判断推荐是否可信 | Trust Context + 信任评分+证据链 |
| 无法解释推荐理由 | Decision Context + 推荐因子透明化 |

**效果**：AI回答从"语言概率"变成"产业事实推理"。每个结论都附有：
1. 数据来源等级（Level 0-4）
2. 证据链（谁能证明）
3. 置信度（统计可信区间）

这与 22_GEO测量方法论.md 中定义的"可观测与不可观测边界"一致——Context Layer只描述可观测范围内的统计规律，不推测AI的"真实想法"。

---

## 七、系统架构位置（完整图景）

`
                    AI Agent / MCP Client
                            │
                    ┌───────┴───────┐
                    │  GEO Context  │  ← 33_本文件
                    │     Layer     │
                    ├───────────────┤
                    │  Context API  │
                    │  MCP Server   │
                    │  Context Eng. │
                    │  Ind. Memory  │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │  Industry     │  ← 26_GEO产业内核与开放协议.md
                    │  Kernel       │
                    │  (6 Engines)  │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │  Data Layer   │
                    │  (Graph + DB) │
                    └───────────────┘
`

Context Layer 是 GEO 行业协议家族的"AI入口层"，向上对接 AI Agent / MCP Client，向下封装 Industry Kernel 的全部能力。它与现有各层的关系：

| 现有层 | 与Context Layer的关系 |
|--------|---------------------|
| Industry Kernel (26) | Context Layer对内核6引擎的编排封装 |
| Protocol Family (26) | MCP Server作为协议族新成员 |
| Agent OS (04) | Context Engine为Agent提供产业级记忆 |
| API规范 (08) | Context API作为独立API分类 |
| 测量方法论 (22) | Context Layer遵循可观测边界原则 |
| 标准体系 (32) | Context Layer使用的评分/分类遵循GEO标准 |

---

## 八、与现有文档的映射关系

| 本文件内容 | 联动文档 |
|----------|---------|
| Context Engine的7个维度 | 26_GEO产业内核与开放协议.md（6个引擎） |
| MCP Server协议 | 26_GEO产业内核与开放协议.md（开放协议家族） |
| Industry Memory | 04_Agent_OS设计.md（Agent系统资源） |
| Context API | 08_API接口规范.md（API分类） |
| 减少AI幻觉 | 22_GEO测量方法论.md（可观测边界） |
| 上下文评分溯源 | 30_GEO标准体系与行业指数.md（评分标准） |

---

## Implementation Reference

> Content from 02_CONTEXT_ENGINE_IMPLEMENTATION.md, integrated for developer reference.

﻿# Context Engine Implementation

## Architecture

Context Engine sits between the Knowledge Layer (Entity/Relationship/Event/Evidence) and the Application/Agent Layer. It is the orchestration layer that assembles raw data into structured, queryable, rankable context.

`
Knowledge Layer (Sprint 1)
    |
    v
  Retrieval Layer
  EntityRetriever / RelationshipRetriever / EvidenceRetriever
    |
    v
  Builders
  CompanyContextBuilder / IndustryContextBuilder / CapabilityContextBuilder
    |
    v
  Ranking
  RelevanceScorer / TrustScorer / GEOScorer
    |
    v
  Context Engine (orchestrator)
    |
    v
  Context API / MCP Server
`

## Module Structure

backend/app/context/
  engine.py              # ContextEngine orchestrator
  builders/
    company_context.py   # Company context assembly
    industry_context.py  # Industry context assembly
    capability_context.py # Capability context assembly
  retrieval/
    entity_retriever.py  # Company/Industry/Capability queries
    relationship_retriever.py  # Graph edge queries
    evidence_retriever.py  # Evidence queries by target
  ranking/
    relevance.py         # Keyword relevance scoring
    trust_score.py       # Evidence-based trust scoring
    geo_score.py         # GEO Score calculation
  schemas/
    context_schema.py    # Pydantic models for all context types

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/context/company/{id} | Full company profile + capabilities + relationships + events + evidence + scoring |
| GET | /api/v1/context/industry/{id} | Industry structure + companies + capabilities + trends + events |
| GET | /api/v1/context/capability/{id} | Capability detail + providers + relationships + evidence |
| POST | /api/v1/context/query | Natural language search across entities |

## Context Data Flow

### Company Context
1. EntityRetriever.get_company()
2. EntityRetriever.get_capabilities_by_company()
3. RelationshipRetriever.get_relationships() + resolve entity names
4. Event query (SQLAlchemy direct)
5. EvidenceRetriever.get_evidence()
6. TrustScorer.compute() + GEOScorer.compute()
7. Assembly into CompanyContext response

### Industry Context
1. EntityRetriever.get_industry()
2. EntityRetriever.get_companies_by_industry()
3. Capability query across all companies
4. Event query across all companies
5. Assembly into IndustryContext response

### Capability Context
1. EntityRetriever.get_capability()
2. EntityRetriever.get_company() for provider
3. RelationshipRetriever.get_relationships() for provider
4. EvidenceRetriever.get_evidence()
5. Assembly into CapabilityContext response

### Natural Language Query
1. EntityRetriever.search_companies() - PostgreSQL ILIKE search
2. RelevanceScorer.score_companies() - keyword relevance
3. Top N results returned

## Ranking Framework

| Factor | Source | Weight (configurable) |
|--------|--------|----------------------|
| Relevance | Keyword match score | 0.3 (in YAML) |
| Trust | Evidence confidence levels | 0.3 (in YAML) |
| GEO Score | Company.geo_score | 0.2 (in YAML) |
| Capability | Capability level match | 0.2 (in YAML) |

## Agent Interface Preparation

Context Engine is designed as the single entry point for Agent data access:

`
Agent -> Tool -> Context API -> ContextEngine -> Knowledge Layer
`

No Agent should directly access the database. The Context API provides a complete, ranked, explainable context response.

## Future Extensions

1. Vector DB integration: Replace ILIKE search with embedding similarity
2. Graph DB integration: Replace ORM relationship queries with Neo4j traversal
3. Cache layer: Redis cache for frequently accessed contexts
4. Streaming: Long-running context assembly with progress reporting
5. Event-driven: Real-time context updates when entities change

