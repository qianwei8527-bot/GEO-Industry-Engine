import os

# === 02：+GEOJob +GEOJobSkill +GEOCareerPath ===
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_domain = """

### 2.27 GEOJob（GEO岗位）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String | 岗位名称 |
| category | Enum | strategy/operation/content/data/engineering/brand/agent |
| level | Enum | L1/L2/L3/L4 |
| description | Text | 岗位描述 |
| typical_tasks | JSON | 典型工作内容 |
| salary_range | JSON | 薪资范围 |
| demand_level | Int | 需求量评分(1-5) |

### 2.28 GEOJobSkill（岗位技能）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| job_id | UUID | FK -> GEOJob |
| skill_name | String | 技能名称 |
| skill_category | Enum | cognitive/data/content/engineering/strategy/tools |
| required_level | Int | 需要的熟练度(1-5) |
| learning_path | JSON | 学习资源推荐 |

### 2.29 GEOCareerPath（职业路径）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| from_job_id | UUID | FK -> GEOJob |
| to_job_id | UUID | FK -> GEOJob |
| path_type | Enum | promotion/transition/specialization |
| typical_duration | String | 典型周期 |
| required_experience | String | 所需经验 |"""

marker = "### 2.26 AIOpportunityScore（AI商机评分）"
c = c.replace(marker, marker + new_domain)
open(p02, "w", encoding="utf-8").write(c)
print("02 done")

# === 03：+geo_jobs +geo_job_skills +geo_career_paths ===
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_tables = """

### GEO岗位表

geo_jobs
- id (UUID, PK)
- name (String)
- category (Enum: strategy / operation / content / data / engineering / brand / agent)
- level (Enum: L1 / L2 / L3 / L4)
- description (Text)
- typical_tasks (JSON)
- salary_range (JSON)
- demand_level (Int, 1-5)

### GEO岗位技能表

geo_job_skills
- id (UUID, PK)
- job_id (UUID, FK -> geo_jobs.id)
- skill_name (String)
- skill_category (Enum: cognitive / data / content / engineering / strategy / tools)
- required_level (Int, 1-5)
- learning_path (JSON)

### GEO职业路径表

geo_career_paths
- id (UUID, PK)
- from_job_id (UUID, FK -> geo_jobs.id)
- to_job_id (UUID, FK -> geo_jobs.id)
- path_type (Enum: promotion / transition / specialization)
- typical_duration (String)
- required_experience (String)"""

marker03 = "# GEO产业引擎 — 数据库ER设计"
c = c.replace(marker03, marker03 + new_tables)
open(p03, "w", encoding="utf-8").write(c)
print("03 done")