---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine Agent 工作流详细设计

> 状态：架构设计 | 版本：v2.0 | 日期：2026-07-28
> 关联：04_Agent_OS设计.md、CTO长期开发协议.md §Agent OS
> 代码: agents/ (21个文件)、backend/app/agents/、backend/app/mcp/

---

## 一、Agent OS 定位

Agent OS 是整个系统的执行层，不是决策层。Agent 不能创造事实，只能解释知识。

核心约束: Agent 不能绕过 Context Engine + Decision Engine 直接生成业务结论。所有 Agent 输出必须引用 Entity/Evidence/Event/Decision Rule。

---

## 二、Agent 执行架构

`
用户输入 (自然语言/API/MCP)
         ↓
┌─ Intent Router ──────────────────────────────┐
│  agents/workflow/intent_router.py             │
│  分类: assessment | certification | analysis │
│       | navigation | marketplace | inquiry   │
└──────────────────┬───────────────────────────┘
                   ↓
┌─ Task Planner ───────────────────────────────┐
│  agents/workflow/task_planner.py              │
│  分解为: [Step1, Step2, ..., StepN]           │
│  每步: {agent, tool, params, depends_on}     │
└──────────────────┬───────────────────────────┘
                   ↓
┌─ Task Executor (多步骤编排) ──────────────────┐
│  按DAG执行: 无依赖并行, 有依赖串行            │
│  每步执行后验证输出, 失败回退                 │
└──────────────────┬───────────────────────────┘
                   ↓
         ┌────────┼────────┐
         ↓        ↓        ↓
    [Agent1]  [Agent2]  [Agent3]
         ↓        ↓        ↓
    [Context Tool] [Decision Tool] [Search Tool]
         ↓        ↓        ↓
┌─ Memory Layer ───────────────────────────────┐
│  短期: 会话内上下文缓存                       │
│  长期: 分析结果/洞察持久化                    │
└──────────────────┬───────────────────────────┘
                   ↓
              最终输出
     (带引用: 来源Entity/Evidence/Event/Decision Rule)
`

---

## 三、Agent 分类体系

### 3.1 基础Agent (4个已注册)

| Agent | 文件 | 核心能力 | 状态 |
|-------|------|---------|------|
| IndustryAnalyst | agents/agents/industry_agent.py | 行业规模评估、趋势分析、比较 | 骨架就绪 |
| CompanyIntelligence | agents/agents/company_agent.py | 企业深度分析、竞争位置、风险 | 骨架就绪 |
| GEOGrowth | agents/agents/geo_growth_agent.py | GEO优化建议、策略生成、效果追踪 | 骨架就绪 |
| DataAnalyst | agents/agents/analyst_agent.py | 指标统计、数据总结、洞察提炼 | 骨架就绪 |

### 3.2 角色Agent（架构设计，未代码化）

角色Agent 是对基础Agent的编排封装，面向特定用户角色提供一站式能力：

| 角色Agent | 面向角色 | 编排的基础Agent | 触发场景 |
|-----------|---------|----------------|---------|
| EnterpriseDiagnostician | 企业 | CompanyIntelligence + GEOGrowth + DataAnalyst | 企业用户进入检测中心 |
| CareerNavigator | 个人 | IndustryAnalyst + GEOGrowth | 个人用户查询职业机会 |
| ProviderMatcher | 服务商 | IndustryAnalyst + CompanyIntelligence | 服务商寻找客户 |
| RegionalIntelligence | 政府 | IndustryAnalyst + DataAnalyst | 政府分析区域产业 |
| InvestmentScout | 投资机构 | IndustryAnalyst + CompanyIntelligence | 投资者发现标的 |
| EcosystemMonitor | 平台 | 全部四个基础Agent | 平台自动监控 |

### 3.3 Agent 工具集

| 工具 | 文件 | 能力 | 状态 |
|------|------|------|------|
| ContextTool | agents/tools/search_tool.py | 查询 Context Engine 获取实体上下文 | 骨架就绪 |
| DecisionTool | backend/app/agents/tools/decision_tool.py | 调用 Decision Engine 获取评分/预测/推荐 | 骨架就绪 |
| SearchTool | backend/app/agents/tools/context_tool.py | 通用搜索(企业/行业/能力) | 骨架就绪 |
| MCP Context | backend/app/mcp/tools/context_tool.py | MCP协议暴露的Context查询 | 骨架就绪 |
| MCP Decision | backend/app/mcp/tools/decision_tool.py | MCP协议暴露的Decision查询 | 骨架就绪 |

---

## 四、意图路由设计

### 4.1 意图分类

| 意图 | 关键词/模式 | 路由目标 | 优先级 |
|------|-----------|---------|:--:|
| assessment | "评估"、"检测"、"评分"、"排名"、"位置" | CompanyIntelligence + GEOGrowth | 1 |
| certification | "认证"、"审核"、"申请"、"等级" | DataAnalyst → Certification API | 2 |
| analysis | "分析"、"趋势"、"增长"、"行业"、"竞争" | IndustryAnalyst | 3 |
| navigation | "地图"、"导航"、"在哪里"、"找企业" | IndustryAnalyst → Context | 4 |
| marketplace | "找服务商"、"发布需求"、"交易" | CompanyIntelligence → Marketplace API | 5 |
| inquiry | 无法匹配以上 → fallback | DataAnalyst → 通用查询 | 6 |

### 4.2 路由实现

gents/workflow/intent_router.py:
`python
class IntentRouter:
    def route(self, query: str) -> Intent:
        # 规则匹配 + 置信度排序
        for intent in INTENT_PATTERNS:
            if matches(query, intent.patterns):
                return intent
        return Intent.INQUIRY  # fallback
`

### 4.3 多意图处理

当用户输入包含多意图时（如"分析腾讯云的GEO表现并推荐认证等级"）:
1. 识别主意图 + 次意图
2. Task Planner 串行编排: 先完成主意图，结果作为次意图输入上下文
3. 最终输出合并

---

## 五、多步骤任务编排

### 5.1 任务分解示例

用户问: "分析某企业在AI营销行业的竞争位置并给出提升建议"

Task Planner 分解:
`json
{
  "steps": [
    {
      "id": "step_1",
      "agent": "IndustryAnalyst",
      "tool": "ContextTool",
      "params": {"industry": "AI营销", "query_type": "overview"},
      "depends_on": []
    },
    {
      "id": "step_2",
      "agent": "CompanyIntelligence",
      "tool": "ContextTool",
      "params": {"entity_id": "geo-company-042", "query_type": "full_context"},
      "depends_on": []
    },
    {
      "id": "step_3",
      "agent": "CompanyIntelligence",
      "tool": "DecisionTool",
      "params": {"entity_id": "geo-company-042", "decision_type": "competitive_position"},
      "depends_on": ["step_1", "step_2"]
    },
    {
      "id": "step_4",
      "agent": "GEOGrowth",
      "tool": "DecisionTool",
      "params": {"entity_id": "geo-company-042", "decision_type": "improvement_roadmap"},
      "depends_on": ["step_3"]
    }
  ]
}
`

执行: step_1 和 step_2 并行 → step_3 串行 → step_4 串行

### 5.2 执行约束

- 无依赖步骤并行执行（最大并发: 4）
- 每步超时: 30秒
- 失败策略: 重试1次 → 跳过(非关键步)或终止(关键步)
- 每步输出验证: 非空 + 结构正确 + 置信度 > 0.5

### 5.3 当前状态

| 能力 | 状态 | 说明 |
|------|------|------|
| 意图路由 | ✅ 已实现 | intent_router.py 工作正常 |
| 任务分解 | ⚠️ 骨架 | 	ask_planner.py 基础分解可用，复杂多意图未实现 |
| 多步执行 | 🔴 未实现 | C.3-2 编码阶段任务 |
| Agent调用Tool | ✅ 单Tool可调用 | 每个Agent可调单个Tool |
| 多Tool编排 | 🔴 未实现 | 同Agent内多Tool调用链未实现 |
| Memory持久化 | 🔴 未实现 | 会话内临时缓存，未持久化 |

---

## 六、Agent输出约束

### 6.1 强制引用格式

Agent 所有结论性输出必须附带引用:

`json
{
  "conclusion": "腾讯云的AI可见度在过去90天提升了15%，主要驱动因素是技术文档增加。",
  "confidence": 0.85,
  "citations": [
    {"source": "Entity", "id": "geo-company-042", "field": "geo_visibility"},
    {"source": "Evidence", "id": "EV-128", "field": "content_count"},
    {"source": "Event", "id": "EVT-342", "field": "document_published"},
    {"source": "DecisionRule", "config": "assessment.yaml#identity_position"}
  ]
}
`

### 6.2 不可输出的内容

Agent 禁止:
- 编造数据库中不存在的实体
- 声称没有证据支持的能力
- 给出没有Decision Engine支撑的评分
- 推荐未经Context验证的关系

---

## 七、Agent进化路径

| 阶段 | 能力 | 依赖 |
|------|------|------|
| 当前 | 单Tool调用、简单意图路由 | ✅ 已实现 |
| P0编码 | 多步骤链、Memory持久化、Tool组合 | C.3-2 |
| P1 | 角色Agent封装、自定义Workflow | C.3-2完成 |
| P2 | 自主学习(从反馈中调整)、Agent协作 | Decision反馈闭环 |
| P3 | Agent Marketplace、第三方Agent接入 | 开放生态 |

---

## 八、MCP协议集成

### 8.1 已注册MCP工具

| MCP工具 | 对应后端 | 用途 |
|---------|---------|------|
| geo_context_query | Context Engine | 外部系统查询GEO实体上下文 |
| geo_decision_calculate | Decision Engine | 外部系统调用GEO评分能力 |
| geo_agent_caller | Agent OS | 外部系统触发Agent分析 |

### 8.2 MCP调用示例

`json
// 外部系统调用
{
  "tool": "geo_decision_calculate",
  "params": {
    "entity_id": "geo-company-042",
    "decision_type": "geo_score",
    "include_breakdown": true
  }
}
`

---

## 九、实现状态与编码任务

### 当前状态

| 组件 | 代码路径 | 状态 |
|------|---------|------|
| 4个基础Agent | agents/agents/*.py | ✅ 骨架就绪 |
| BaseAgent | agents/core/base.py | ✅ 2KB |
| AgentRegistry | backend/app/agents/core/agent_registry.py | ✅ 1.2KB |
| IntentRouter | agents/workflow/intent_router.py | ✅ 0.7KB |
| TaskPlanner | agents/workflow/task_planner.py | ⚠️ 1.1KB (简单分解) |
| ContextTool | agents/tools/ (2文件) | ✅ 单Tool可用 |
| DecisionTool | backend/app/agents/tools/decision_tool.py | ✅ 2KB |
| MCP Server | backend/app/mcp/server.py | ✅ 0.7KB |
| MCP Tools | backend/app/mcp/tools/ (2文件) | ✅ 骨架就绪 |
| Agent API | backend/app/api/v1/agent.py | ✅ 1.8KB |
| Memory | agents/memory/ | 🔴 空 |
| 多步执行 | — | 🔴 未实现 |

### 编码阶段P0任务 (C.3-2)

1. Memory模块实现: 短期(会话缓存) + 长期(SQLite/PostgreSQL持久化)
2. 多步骤链: TaskPlanner → 按DAG并行/串行执行 → 结果合并
3. Tool组合: 同Agent内多Tool调用链
4. 端到端测试: 复杂查询 → Agent → 多Tool → 最终结果+引用

---

## 十、质量门禁

- [ ] Agent 输出强制包含引用（Entity/Evidence/Event/DecisionRule）
- [ ] 意图路由覆盖率 ≥ 90%（已知意图模式）
- [ ] 多步骤链注入测试通过（≥5步骤的复杂查询）
- [ ] Agent 不产生幻觉（所有结论有知识图谱支撑）
- [ ] API 集成测试：POST /agent/analyze → 完整链路
