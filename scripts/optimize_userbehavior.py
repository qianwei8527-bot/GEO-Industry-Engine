import os

# ===== 02_领域模型设计.md: Enhance PromptKnowledgeBase + Add UserSearchSession =====
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

# 1. Enhance PromptKnowledgeBase: add 4 new behavioral fields
old_prompt_table = """| id | UUID | 主键 |
| query_text | Text | 问题原文 |
| query_category | Enum | industry/company/product/trend |
| industry_id | UUID | FK -> Industry |
| model_id | UUID | FK -> AiModel |
| response_summary | Text | 模型回答摘要 |
| mentioned_companies | JSON[] | 提及的企业列表 |
| citations | JSON[] | 引用来源URL列表 |
| mention_frequency | Decimal | 企业出现频率(0-1) |
| confidence | Decimal | 置信度 |
| queried_at | DateTime | 查询时间 |"""

new_prompt_table = """| id | UUID | 主键 |
| query_text | Text | 问题原文 |
| query_intent | Enum | 查询意图: factual/comparative/exploratory/transactional |
| query_category | Enum | industry/company/product/trend |
| session_id | UUID | FK -> UserSearchSession（同一对话会话归组）|
| industry_id | UUID | FK -> Industry |
| model_id | UUID | FK -> AiModel |
| response_summary | Text | 模型回答摘要 |
| response_format | Enum | 回答格式: list/paragraph/table/code |
| mentioned_companies | JSON[] | 提及的企业列表 |
| citations | JSON[] | 引用来源URL列表 |
| citation_types | JSON | 引用类型分布 |
| mention_frequency | Decimal | 企业出现频率(0-1) |
| user_satisfaction_signals | JSON | 用户满意度信号（点击引用/继续追问/离开等）|
| confidence | Decimal | 置信度 |
| queried_at | DateTime | 查询时间 |"""

c = c.replace(old_prompt_table, new_prompt_table)

# 2. Add UserSearchSession after AIBrandRanking
new_session_obj = """

### 2.22 UserSearchSession（用户搜索会话）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_type | Enum | enterprise_decision_maker/researcher/developer/student |
| industry_id | UUID | FK -> Industry（用户关注的行业）|
| start_time | DateTime | 会话开始时间 |
| end_time | DateTime | 会话结束时间 |
| query_count | Int | 此次会话的查询次数 |
| models_used | JSON[] | 会话中用到的模型列表 |
| task_type | Enum | research/comparison/decision_verification/exploration |
| final_action | Enum | purchased/contacted/documented/no_action |
| user_satisfaction | Enum | high/medium/low/drop_off |
| session_metadata | JSON | 会话元数据（查询序列、模型切换模式等）|

**用途**：追踪用户在多模型间的实际搜索行为——用户不是只用一个模型查一次，而是反复查、对比、追问。"""

old_end = "**用途**：AI品牌排名系统核心输出，类似AI时代的Alexa/SimilarWeb。"
c = c.replace(old_end, old_end + new_session_obj)

open(p02, "w", encoding="utf-8").write(c)
print("02 done")


# ===== 03_数据架构.md: Enhance prompt_knowledge_base + add user_search_sessions =====
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

old_prompt_tbl = """prompt_knowledge_base
- id (UUID, PK)
- query_text (Text) — 问题原文
- query_category (Enum: industry / company / product / trend)
- industry_id (UUID, FK -> industries.id)
- model_id (UUID, FK -> ai_models.id)
- response_summary (Text) — 模型回答摘要
- mentioned_companies (JSON) — 提及的企业列表
- citations (JSON) — 引用来源URL列表
- mention_frequency (Decimal) — 企业出现频率(0-1)
- confidence (Decimal)
- queried_at (DateTime)
- data_period (Date)"""

new_prompt_tbl = """prompt_knowledge_base
- id (UUID, PK)
- query_text (Text) — 问题原文
- query_intent (Enum: factual / comparative / exploratory / transactional) — 查询意图
- query_category (Enum: industry / company / product / trend)
- session_id (UUID, FK -> user_search_sessions.id, nullable) — 所属会话
- industry_id (UUID, FK -> industries.id)
- model_id (UUID, FK -> ai_models.id)
- response_summary (Text) — 模型回答摘要
- response_format (Enum: list / paragraph / table / code) — 回答格式
- mentioned_companies (JSON) — 提及的企业列表
- citations (JSON) — 引用来源URL列表
- citation_types (JSON) — 引用类型分布
- mention_frequency (Decimal) — 企业出现频率(0-1)
- user_satisfaction_signals (JSON) — 用户满意度信号
- confidence (Decimal)
- queried_at (DateTime)
- data_period (Date)"""

c = c.replace(old_prompt_tbl, new_prompt_tbl)

# Add user_search_sessions table
new_session_tbl = """

### 用户搜索会话表

user_search_sessions
- id (UUID, PK)
- user_type (Enum: enterprise_decision_maker / researcher / developer / student)
- industry_id (UUID, FK -> industries.id, nullable)
- start_time (DateTime)
- end_time (DateTime, nullable)
- query_count (Int)
- models_used (JSON)
- task_type (Enum: research / comparison / decision_verification / exploration)
- final_action (Enum: purchased / contacted / documented / no_action, nullable)
- user_satisfaction (Enum: high / medium / low / drop_off, nullable)
- session_metadata (JSON)"""

old_end_tbl = "# GEO产业引擎 — 数据库ER设计"
if "# GEO产业引擎 — 数据库ER设计" in c:
    c = c.replace(old_end_tbl, "# GEO产业引擎 — 数据库ER设计" + new_session_tbl)

open(p03, "w", encoding="utf-8").write(c)
print("03 done")