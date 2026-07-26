import os
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_tables = """

### 用户意图表

user_intents
- id (UUID, PK)
- name (String)
- category (Enum: industry_discovery / comparison / vendor_selection / solution_exploration / brand_verification)
- purchase_stage (Enum: awareness / evaluation / decision / need / validation)
- industry_id (UUID, FK -> industries.id, nullable)
- commercial_value (Int, 0-100) — 商业价值评分
- description (Text)
- example_prompt (Text)
- geo_goal (Text)
- created_at (DateTime)

### 意图-模型得分表

intent_model_scores
- id (UUID, PK)
- intent_id (UUID, FK -> user_intents.id)
- model_id (UUID, FK -> ai_models.id)
- recommendation_weight (Decimal) — 该模型对此意图的推荐权重
- top_factors (JSON) — 主要推荐因子及占比
- confidence (Decimal)
- data_period (Date)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
if old_end in c:
    c = c.replace(old_end, old_end + new_tables)

open(p03, "w", encoding="utf-8").write(c)
print("03 done")