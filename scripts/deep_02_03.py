import os

# === 02：+4 domain objects ===
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()
new_domain = """

### 2.33 GEOSpaceScore（推荐空间评分）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| query_text | Text | 查询问题 |
| industry_id | UUID | FK -> Industry |
| total_slots | Int | AI推荐席位上限 |
| occupied_slots | Int | 当前占位企业数 |
| churn_rate | Decimal | 列表变动频率 |
| entry_barrier | Enum | low/medium/high |
| opportunity_score | Int | 综合机会评分(0-100) |

### 2.34 AITrustScore（AI信任评分）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| model_id | UUID | FK -> AiModel |
| authority_score | Decimal | 权威性信号(0-100) |
| consistency_score | Decimal | 一致性信号(0-100) |
| timeliness_score | Decimal | 时效性信号(0-100) |
| verifiability_score | Decimal | 验证性信号(0-100) |
| overall_trust_score | Int | 综合信任评分(0-100) |

### 2.35 AIContentReadiness（AI内容就绪度）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| content_id | UUID | FK -> Content |
| url | String | 内容URL |
| structure_score | Decimal | 结构化程度(0-100) |
| citability_score | Decimal | 可引用性(0-100) |
| authority_score | Decimal | 权威信号(0-100) |
| timeliness_score | Decimal | 时效性(0-100) |
| verification_score | Decimal | 多源验证(0-100) |
| overall_readiness | Int | 综合就绪度(0-100) |
| suggested_improvements | JSON | 优化建议 |

### 2.36 GEOAttribution（GEO效果归因）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| campaign_id | UUID | FK -> Campaign |
| attribution_model | Enum | last_touch/linear/time_decay/position_based |
| ai_impressions | Int | AI曝光次数 |
| website_visits | Int | 归因网站访问 |
| conversions | Int | 转化数 |
| revenue_attributed | Decimal | 归因收入 |
| roi | Decimal | ROI |"""

old_end = "### 2.32 BusinessOpportunity（商业机会）"
c = c.replace(old_end, old_end + new_domain)
open(p02, "w", encoding="utf-8").write(c)
print("02 updated")

# === 03：+4 tables ===
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()
new_tables = """

### GEO推荐空间评分表

geo_space_scores
- id (UUID, PK)
- query_text (Text)
- industry_id (UUID, FK -> industries.id)
- total_slots (Int)
- occupied_slots (Int)
- churn_rate (Decimal)
- entry_barrier (Enum: low / medium / high)
- opportunity_score (Int, 0-100)

### AI信任评分表

ai_trust_scores
- id (UUID, PK)
- company_id (UUID, FK -> companies.id)
- model_id (UUID, FK -> ai_models.id)
- authority_score (Decimal)
- consistency_score (Decimal)
- timeliness_score (Decimal)
- verifiability_score (Decimal)
- overall_trust_score (Int, 0-100)

### AI内容就绪度表

ai_content_readiness
- id (UUID, PK)
- content_id (UUID)
- url (String)
- structure_score (Decimal)
- citability_score (Decimal)
- authority_score (Decimal)
- timeliness_score (Decimal)
- verification_score (Decimal)
- overall_readiness (Int, 0-100)
- suggested_improvements (JSON)

### GEO效果归因表

geo_attributions
- id (UUID, PK)
- company_id (UUID, FK -> companies.id)
- campaign_id (UUID)
- attribution_model (Enum: last_touch / linear / time_decay / position_based)
- ai_impressions (Int)
- website_visits (Int)
- conversions (Int)
- revenue_attributed (Decimal)
- roi (Decimal)
- period_start (Date)
- period_end (Date)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
c = c.replace(old_end, old_end + new_tables)
open(p03, "w", encoding="utf-8").write(c)
print("03 updated")