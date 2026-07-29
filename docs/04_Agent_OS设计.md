---
status: stable
authority: primary
version: v2.0
last_review: 2026-07-28
related_docs: [CTO长期开发协议, 04-1, 40]
---
﻿# GEO产业引擎 — Agent OS设计

## Agent Tool Layer（决策模型调用层）

Agent 分阶段建设，当前优先级按以下顺序：

| Agent | 调用模型 | 用途 | 优先级 |
|-------|---------|------|-------|
| Context Agent | Context Engine（7个上下文维度） | 所有Agent的基础设施，统一上下文供给 | P0 |
| Industry Analyst Agent | 产业认知库、IndustryIntelligence、Evolution Engine | 输入企业，输出产业结构、关系、趋势、机会 | P0 |
| Scanner Agent | AI模型智能库、用户意图模型AIOpportunityScore、CompetitionMatrix | 生成模型感知的扫描策略 | P1 |
| Content Agent | AITrustScore、AIContentReadiness | 生成AI可理解、易引用的内容 | P2 |
| Industry Agent | 产业认知库、职业生态、IndustryIntelligence | 产业趋势分析和机会发现 | P2 |
| Market Agent | 竞争矩阵、商业机会模型 | 需求匹配和商机推荐 | P3 |

### 九模型调用矩阵

| 决策模型 | 调用Agent | 输入 | 输出 |
|----------|----------|------|------|
| EntityClarity | Scanner Agent | 企业ID | 实体完整度评分 |
| AITrustScore | Content Agent | 企业ID+模型ID | 信任评分 |
| AIContentReadiness | Content Agent | 内容URL | 就绪度分数+优化建议 |
| GEOSpaceScore | Scanner Agent | 行业ID+查询 | 席位竞争分析 |
| CompetitionScore | Market Agent | 企业ID+行业ID | 竞争差距报告 |
| IndustryRelevance | Industry Agent | 企业ID+行业ID | 相关度评分 |
| ModelPreference | Scanner Agent | 企业ID+模型ID | 推荐倾向评分 |
| Timeliness | Data Agent | 企业ID | 信息新鲜度评分 |
| Sentiment | Industry Agent | 企业ID+模型ID | 情感倾向评分 |


---

## Industry Memory（产业级记忆系统）

GEO Agent OS 的Agent在已有决策模型调用能力之上，新增**共享产业记忆（Industry Memory）**作为系统资源。

| 记忆类型 | 内容 | 调用Agent | 用途 |
|----------|------|----------|------|
| 企业演化路径 | 企业的转型、扩张、衰退、并购记录 | Industry Agent | 理解企业当前状态 |
| 产业事件流 | 融资、并购、政策发布、产品发布 | Scanner Agent | 实时感知产业变化 |
| 关系变化记录 | 合作/竞争关系的新建与中断 | Market Agent | 判断产业动态 |
| AI推荐变化 | AI对企业的推荐频率、位置、语境变化 | Scanner Agent | 跟踪可见度趋势 |
| 人才流动 | 关键人才在不同企业/行业间的迁移 | Industry Agent | 判断行业热度 |

Agent通过统一的 context.memory API 调用：

```
# Agent伪代码示例
industry_memory = geo_context.memory.get(
    entity="GEO-COMPANY-000001",
    time_range="2024-2026",
    memory_types=["evolution", "events", "recommendation"]
)
```

详见 [31_GEO产业上下文层.md](31_GEO产业上下文层.md) 第五章。

> *本文件为中文完整版。英文概览版内容已合并至此。*

## 概述

GEO Agent OS 是一个基于多Agent协作的智能操作系统，模拟AI公司组织架构，每个Agent承担特定职责，协同完成GEO产业增长闭环。

## Agent组织架构

```
                     CEO Agent
                         │
            ┌────────────┼────────────┐
            │            │            │
         CTO Agent    Product Ag    Industry Ag
            │            │            │
    ┌───────┼───────┐   │            │
    │       │       │   │            │
Scanner  Content  Data  │            │
  Ag       Ag      Ag   │            │
                        │            │
                   Market Ag ─── Sales Ag
                        │
                     QA Agent
```

## Agent详细定义

### 1. CEO Agent

| 属性 | 定义 |
|------|------|
| **职责** | 全局协调、任务分配、决策仲裁、进度监控 |
| **输入** | 用户意图、系统状态、各Agent报告 |
| **输出** | 任务指令、协调指令、决策结论 |
| **权限** | 所有Agent调度、资源配置、优先级决策 |
| **调用工具** | 所有Agent、日程管理、通知系统 |

### 2. CTO Agent

| 属性 | 定义 |
|------|------|
| **职责** | 技术架构决策、系统设计、技术风险管控 |
| **输入** | 产品需求、技术问题、架构变更请求 |
| **输出** | 技术方案、架构文档、技术评审结论 |
| **权限** | 代码仓库、基础设施配置、技术栈决策 |
| **调用工具** | 代码分析、架构评审、文档生成 |

### 3. Product Agent

| 属性 | 定义 |
|------|------|
| **职责** | 产品规划、需求分析、功能设计、用户研究 |
| **输入** | 市场反馈、用户数据、行业趋势 |
| **输出** | PRD、功能规格、产品路线图 |
| **权限** | 功能开关、版本规划、需求池管理 |
| **调用工具** | 数据分析、产业情报、用户访谈 |

### 4. Industry Agent

| 属性 | 定义 |
|------|------|
| **职责** | 行业研究、产业地图维护、行业趋势分析 |
| **输入** | 行业数据、研究报告、政策信息 |
| **输出** | 产业地图更新、行业报告、趋势分析 |
| **权限** | 产业知识图谱读写、行业数据库 |
| **调用工具** | Neo4j查询、数据爬取、报告生成 |

**产业趋势分析扩展**：
- 调用 GEO产业认知库 的趋势数据
- 分析GEO产业生命周期阶段和商业模式演进
- 识别产业链各环节的商业机会
- 预测岗位需求和技能缺口
- 输出产业趋势报告给 CEO Agent 决策参考

**意图分析扩展**：
- 分析本行业用户搜索意图分布（5类意图）
- 识别行业内的高商业价值问题
- 输出行业AI需求地图给Scanner Agent参考

### 5. GEO Scanner Agent

| 属性 | 定义 |
|------|------|
| **职责** | AI搜索扫描、企业GEO监测、产业情报 |
| **输入** | 企业信息、关键词、监测周期 |
| **输出** | GEO评分、监测报告、变更告警 |
| **权限** | AI搜索API调用、评分模型触发 |
| **调用工具** | AI搜索API、评分引擎、告警系统 |

**格式感知生成**：
- 根据查询意图选择最优回答格式（factual→段落, comparative→表格, exploratory→列表, transactional→结构化）
- 不同行业默认格式不同（电商→表格, 医疗→段落, 法律→列表）
- 用户满意度信号反馈校准格式选择

**模型感知升级**：
- 根据行业+企业特征动态选择扫描策略（如医疗企业重点扫 Claude/ChatGPT/Perplexity）
- 根据 ai_model_industry_scores 决定各模型的扫描权重
- 针对不同模型的 source_preference 调整 Prompt 策略
- 扫描结果存入 ai_query_results，持续丰富模型行为数据库

**意图感知扫描**：
- 根据 Industry Agent 输出的行业AI需求地图选择扫描优先级
- 高商业价值意图对应的Prompt优先扫描
- 高频率低占位问题触发商机预警

**用户行为研究能力**：
- 扫描并分类用户查询意图（factual/comparative/exploratory/transactional）
- 跟踪用户在多模型间的切换模式（session级行为）
- 分析用户满意度信号（点击引用/继续追问/离开）
- 洞察任务类型与模型选择的关联规律

**扫描策略示例**：
- 医疗企业：Claude 30%，ChatGPT 30%，Perplexity 25%，Gemini 15%
- 科技企业：ChatGPT 35%，Gemini 25%，Claude 20%，Perplexity 20%

### 6. Content Agent

| 属性 | 定义 |
|------|------|
| **职责** | GEO内容创作、内容优化、多模态内容生产 |
| **输入** | 内容策略、关键词、品牌调性 |
| **输出** | 优化文章、多模态内容、内容方案 |
| **权限** | 内容模板库、知识库、媒体资源 |
| **调用工具** | LLM生成、知识库查询、媒体制作 |

**格式感知生成**：
- 根据查询意图选择最优回答格式（factual→段落, comparative→表格, exploratory→列表, transactional→结构化）
- 不同行业默认格式不同（电商→表格, 医疗→段落, 法律→列表）
- 用户满意度信号反馈校准格式选择

**模型感知升级**：
- 根据目标的行业+模型偏好生成差异化内容策略
- 针对 ChatGPT 偏好：专业长内容、知识深度
- 针对 Gemini 偏好：网页实体结构、结构化数据
- 针对 Perplexity 偏好：引用来源质量、可验证性
- 针对 DeepSeek 偏好：中文权威内容、国内案例
- 内容效果反馈写入 ModelBehaviorPattern，持续校准

### 7. Data Agent

| 属性 | 定义 |
|------|------|
| **职责** | 数据采集、数据处理、数据质量管理、知识图谱构建 |
| **输入** | 数据源配置、采集任务、清洗规则 |
| **输出** | 清洗数据、知识图谱更新、数据报告 |
| **权限** | 所有数据库读写、数据管道控制 |
| **调用工具** | ETL工具、数据库查询、数据验证 |

### 8. Marketplace Agent

| 属性 | 定义 |
|------|------|
| **职责** | 需求匹配、服务商推荐、交易撮合、佣金管理 |
| **输入** | 企业需求、服务商能力、交易规则 |
| **输出** | 匹配结果、推荐排序、交易建议 |
| **权限** | 交易数据库、服务商信息、评价系统 |
| **调用工具** | AI匹配算法、信用评分、交易引擎 |

### 9. Sales Agent

| 属性 | 定义 |
|------|------|
| **职责** | 商机识别、客户跟进、续约管理、升级推荐 |
| **输入** | 客户数据、使用行为、服务到期信息 |
| **输出** | 销售线索、跟进建议、续约方案 |
| **权限** | 客户CRM、定价系统、促销配置 |
| **调用工具** | CRM系统、邮件系统、数据分析 |

### 10. QA Agent


| 属性 | 定义 |
|------|------|
| **职责** | 质量检测、效果验证、合规审查 |
| **输入** | 测试任务、审查请求、合规要求 |
| **输出** | 测试报告、质量评分、合规结论 |
| **权限** | 测试环境、审查工具、质量标准库 |
| **调用工具** | 测试框架、内容审查、合规检查 |

---

## 开发优先级
Agent OS is planned for Phase 5 (P5) of the MVP roadmap. All earlier modules must be designed with Agent-callable interfaces.


---

## 设计指南
1. Each agent uses Function Calling specification
2. Agents communicate via standardized message protocol
3. All agent actions are logged for audit and improvement
4. Agent capabilities are configurable and extensible

Refer to: docs/Agent_OS\u8bbe\u8ba1.md (Chinese detail)

---

## 关联文档

| 文档 | 关系 |
|------|------|
| [02_领域模型设计.md](02_领域模型设计.md) | Agent操作的业务对象定义 |
| [07_后端设计.md](07_后端设计.md) | Agent服务的后端实现 |
| [03_数据架构.md](03_数据架构.md) | AI模型智能库数据表定义、AI回答数据结构、模型行为数据结构 |
| [08_API接口规范.md](08_API接口规范.md) | Agent的Function Calling API定义 |

> 修改本文件时需同步检查以上文件。

## GEO Agent市在

不是交易市场，而是外部Agent生态。未来每个行业都有专业Agent（如医疗市场分析Agent、工厂智能化Agent），基于你的产业知识图谱运行。外部Agent通过GEO Protocol调用平台数据，平台提供实体查询、能力匹配、机会发现等服务。

---

## Implementation Reference

> Content from 04-1_Agent工作流详细设计.md, integrated for developer reference.

# Agent OS Implementation

## Architecture

```
User Query
    |
    v
Agent Router (IntentRouter) -----> Agent Registry
    |                                    |
    v                                    v
Task Planner                     +------------------+
    |                            | IndustryAgent    |
    v                            | CompanyAgent     |
Agent OS Framework               | GEOGrowthAgent   |
    |                            | AnalystAgent     |
    +-- Context Engine (Sprint2) +------------------+
    +-- Decision Engine (Sprint3)       |
    +-- Tools (search/analyze)         v
    +-- Memory (future)           MCP Server
                                        |
                                        v
                                External AI Agents
```

## Components

### Core Framework (agents/core/)
- **BaseAgent**: Abstract class with context and decision engine integration
- **AgentRegistry**: Central registry for all agents
- **AgentContext**: Execution context with history tracking

### Router (agents/router/)
- **IntentRouter**: Keyword-based routing to appropriate agent
- Supports Chinese and English keywords

### Planner (agents/planner/)
- **TaskPlanner**: Multi-step task planning for complex queries

### Agents (agents/agents/)
| Agent | Name | Capabilities |
|-------|------|-------------|
| Industry Agent | industry_agent | Industry structure, trends, opportunities |
| Company Agent | company_agent | Company profile, strengths, competitive position |
| GEO Growth Agent | geo_growth_agent | GEO roadmap, content strategy, AI search growth |
| Analyst Agent | analyst_agent | Data gap analysis, missing data detection |

## Tools (agents/tools/)
- **ContextTool**: Wraps ContextEngine for agent use
- **DecisionTool**: Wraps DecisionEngine for agent use
- **SearchTool**: Entity search across the knowledge graph

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/agent/analyze | Analyze query with routed agent |
| GET | /api/v1/agent/list | List available agents |

## Industry Benchmark

Added to Decision Engine: compares company scores against industry averages
- Company GEO Score vs Industry Average
- Percentile ranking
- Strength/weakness identification

## Integration Rules
1. Agents NEVER access database directly
2. Agents ALWAYS go through Context Engine -> Knowledge Layer
3. Agents ALWAYS go through Decision Engine -> Scores
4. All agent outputs are explainable (scores + reasons + actions)

