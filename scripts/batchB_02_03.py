import os

# === 02 + 03: add all domain objects and tables for 14+15 ===
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c2 = open(p02, "r", encoding="utf-8").read()

new_domain = """

### 2.37 EntityProfile（企业实体画像）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| identity_completeness | Decimal | 身份完整度 |
| capability_completeness | Decimal | 能力完整度 |
| market_completeness | Decimal | 市场完整度 |
| relationship_completeness | Decimal | 关系完整度 |
| trust_completeness | Decimal | 信任完整度 |
| overall_score | Int | 综合实体完整度(0-100) |

### 2.38 InformationSource（信息来源）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| source_name | String | 来源名称 |
| source_type | Enum | official/encyclopedia/news/academic/review/social |
| authority_level | Int | 权威等级(1-5) |
| ai_citation_probability | Decimal | AI引用概率 |
| model_preferences | JSON | 偏好模型 |

### 2.39 CompetitionSnapshot（竞争快照）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| industry_id | UUID | FK -> Industry |
| query_text | Text | 查询问题 |
| snapshot_date | Date | 快照日期 |
| rankings | JSON | 多企业在各模型排名 |

### 2.40 GEOExperiment（GEO实验）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| experiment_type | Enum | content/source/schema/multi |
| hypothesis | Text | 实验假设 |
| status | Enum | active/completed/failed |
| started_at | DateTime | 开始时间 |"""

old_end = "### 2.36 GEOAttribution（GEO效果归因）"
c2 = c2.replace(old_end, old_end + new_domain)
open(p02, "w", encoding="utf-8").write(c2)
print("02 updated")

p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c3 = open(p03, "r", encoding="utf-8").read()
new_tables = """

### 实体画像表

entity_profiles
- id (UUID, PK), company_id (UUID, FK), identity_score (Decimal), capability_score (Decimal), market_score (Decimal), relationship_score (Decimal), trust_score (Decimal), overall_score (Int)

### 信息来源表

information_sources
- id (UUID, PK), source_name (String), source_type (Enum), authority_level (Int), ai_citation_probability (Decimal), model_preferences (JSON)

### 竞争快照表

competition_snapshots
- id (UUID, PK), industry_id (UUID, FK), query_text (Text), snapshot_date (Date), rankings (JSON)

### GEO实验表

geo_experiments
- id (UUID, PK), company_id (UUID, FK), experiment_type (Enum), hypothesis (Text), status (Enum), started_at (DateTime), completed_at (DateTime), results (JSON)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
c3 = c3.replace(old_end, old_end + new_tables)
open(p03, "w", encoding="utf-8").write(c3)
print("03 updated")