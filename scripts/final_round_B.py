import os

# === 02：+GEOIndustryTrend +TalentDemand +BusinessOpportunity ===
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_domain = """

### 2.30 GEOIndustryTrend（产业趋势）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| trend_name | String | 趋势名称 |
| trend_category | Enum | technology/market/business_model/policy |
| industry_id | UUID | FK -> Industry |
| time_horizon | String | 时间范围 |
| impact_level | Int | 影响程度(1-5) |
| description | Text | 趋势描述 |
| evidence | JSON | 支撑证据 |
| confidence | Decimal | 置信度 |

### 2.31 TalentDemand（人才需求）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| role_id | UUID | FK -> GEOJob |
| industry_id | UUID | FK -> Industry |
| demand_count | Int | 需求量 |
| demand_growth | Decimal | 需求增长率 |
| avg_salary | Decimal | 平均薪资 |
| skill_gap | JSON | 技能缺口 |

### 2.32 BusinessOpportunity（商业机会）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| industry_id | UUID | FK -> Industry |
| opportunity_type | Enum | service_gap/talent_shortage/market_entry/technology_adoption |
| description | Text | 机会描述 |
| potential_value | Decimal | 预估价值 |
| entry_barrier | Enum | low/medium/high |"""

old_end = "### 2.29 GEOCareerPath（职业路径）"
c = c.replace(old_end, old_end + new_domain)
open(p02, "w", encoding="utf-8").write(c)
print("02 updated")

# === 03：+geo_industry_trends +geo_talent_demand +geo_business_opportunities ===
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_tables = """

### GEO产业趋势表

geo_industry_trends
- id (UUID, PK)
- trend_name (String)
- trend_category (Enum: technology / market / business_model / policy)
- industry_id (UUID, FK -> industries.id, nullable)
- time_horizon (String)
- impact_level (Int, 1-5)
- description (Text)
- evidence (JSON)
- confidence (Decimal)
- data_period (Date)

### GEO人才需求表

geo_talent_demand
- id (UUID, PK)
- role_id (UUID, FK -> geo_jobs.id)
- industry_id (UUID, FK -> industries.id)
- demand_count (Int)
- demand_growth (Decimal)
- avg_salary (Decimal)
- skill_gap (JSON)
- data_period (Date)

### GEO商业机会表

geo_business_opportunities
- id (UUID, PK)
- industry_id (UUID, FK -> industries.id)
- opportunity_type (Enum: service_gap / talent_shortage / market_entry / technology_adoption)
- description (Text)
- potential_value (Decimal)
- entry_barrier (Enum: low / medium / high)
- confidence (Decimal)
- detected_at (DateTime)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
c = c.replace(old_end, old_end + new_tables)
open(p03, "w", encoding="utf-8").write(c)
print("03 updated")

# === 06：+产业趋势视图, 职业地图, 技能图谱 ===
p06 = os.path.join("D:\\GEO-IE", "docs", "06_前端设计.md")
c = open(p06, "r", encoding="utf-8").read()

old_06 = "- 产业链地图：上中下游结构展示"
new_06 = "- 产业链地图：上中下游结构展示\n  - 产业趋势视图：GEO产业生命周期、技术趋势时间线、市场规模TAM/SAM/SOM\n  - 职业地图：7个岗位的可视化分布、需求量热力图、薪资区间对比\n  - 技能图谱：L1-L4技能树、技能关联网络、学习路径推荐"
c = c.replace(old_06, new_06)
open(p06, "w", encoding="utf-8").write(c)
print("06 updated")