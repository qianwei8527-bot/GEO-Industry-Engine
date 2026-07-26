import os
p02 = os.path.join("D:\\GEO-IE\\docs\\02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_objects = """

### 2.13 AiModel（AI模型）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String | 模型名称（ChatGPT/Gemini/Claude等）|
| provider | String | 提供商（OpenAI/Google/Anthropic等）|
| country | Enum | 所属国家/地区 |
| type | Enum | general_search/vertical_search/recommendation |
| release_date | Date | 发布日期 |
| api_available | Bool | 是否有公开API |
| search_enabled | Bool | 是否支持联网搜索 |
| last_updated | DateTime | 模型信息最后更新时间 |
| status | Enum | active/deprecated/beta |

**关系**：AiModel -> Industry (N:M 通过热度矩阵)，AiModel -> Company (N:M 通过查询结果)

---

### 2.14 ModelMetrics（模型指标）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| estimated_users | BigInt | 估算月活用户 |
| market_share | Decimal | 市场份额估算 |
| enterprise_adoption | Decimal | 企业采用率(0-1) |
| citation_rate | Decimal | 引用来源频率(0-1) |
| avg_response_length | Int | 平均回答长度 |
| knowledge_cutoff | Date | 知识截止日期 |
| data_period | Date | 数据所属时期 |

---

### 2.15 ModelIndustryScore（模型-行业热度）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| industry_id | UUID | FK -> Industry |
| recommendation_rate | Decimal | 该行业在该模型中被推荐的频率 |
| avg_sentiment | Decimal | 情感倾向 |
| top_sources | JSON | 该行业中模型主要引用的来源 |
| confidence | Decimal | 置信度(0-1) |
| data_period | Date | 数据所属时期 |

---

### 2.16 ModelBehaviorPattern（模型行为模式）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| answer_style | Enum | factual/analytical/conversational/summary |
| source_preference | JSON | 来源权重分布（官网/X/新闻/论文/百科）|
| language_bias | JSON | 语言偏向权重 |
| update_sensitivity | Decimal | 对最新信息的敏感度 |
| citation_behavior | JSON | 引用方式偏好 |
| content_format_preference | JSON | 偏好内容格式（长文/列表/表格/代码）|

---

### 2.17 ModelQueryResult（查询结果样本）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| query_text | Text | 查询的Prompt |
| query_category | Enum | 行业/企业/产品/趋势 |
| industry_id | UUID | FK -> Industry |
| response_text | Text | 模型回答全文 |
| mentioned_entities | JSON | 回答中提及的企业/产品 |
| citations | JSON | 引用的来源URL |
| response_time_ms | Int | 响应时间 |
| queried_at | DateTime | 查询时间 |

---

### 2.18 ModelSourcePreference（模型来源偏好）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| source_type | Enum | official_site/news/wikipedia/reddit/academic/forums/social |
| weight | Decimal | 该来源的引用权重(0-1) |
| confidence | Decimal | 权重估算的置信度 |
| data_period | Date | 数据所属时期 |
"""

# Insert after the Agent section
old_marker = "### 2.12 Agent（智能体）"
new_marker = old_marker + "\n" + new_objects
c = c.replace(old_marker, new_marker)

# Update the relationship matrix to include new objects
old_matrix = "           Ind  Sec  Com  Pro  Cap  Vis  Sco  Opp  Reg  Cer  Usr  Agt"
new_matrix = "           Ind  Sec  Com  Pro  Cap  Vis  Sco  Opp  Reg  Cer  Usr  Agt  Mod  MMt  MIs  MBe  MQr  MSr"
c = c.replace(old_matrix, new_matrix)

old_matrix2 = "Agent      -    -    -    -    -    -    -    -    -    -    N:M  ─"
new_matrix2 = "Agent      -    -    -    -    -    -    -    -    -    -    N:M  ─\nAiModel    N:M  -    N:M  -    N:M  -    -    -    -    -    -    N:M  ─   1:1  1:N  1:N  1:N  1:N\nModelMetrics-   -    -    -    -    -    -    -    -    -    -    -   N:1  ─    -    -    -    -\nModelIndScoreN:1  -    -    -    -    -    -    -    -    -    -    -   N:1  -    ─    -    -    -\nModelBehav   -    -    -    -    -    -    -    -    -    -    -    -   N:1  -    -    ─    -    -\nModelQuery   N:1  -    N:M  N:M  -    N:M  N:M  -    -    -    -    -   N:1  -    -    -    ─    -\nModelSource  -    -    -    -    -    -    -    -    -    -    -    -   N:1  -    -    N:1  -    ─"
c = c.replace(old_matrix2, new_matrix2)

open(p02, "w", encoding="utf-8").write(c)
print("02 done")