import os

# === 03：+intent_prompts +ai_recommendation_factors +ai_opportunities ===
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_03 = """

### 意图-问题关联表

intent_prompts
- id (UUID, PK)
- intent_id (UUID, FK -> user_intents.id)
- prompt_text (Text) — 典型问题
- prompt_category (Enum: industry / company / product / trend)
- commercial_value (Int, 0-100) — 该问题的商业价值
- frequency_estimate (Int) — 预估月查询频率
- sample_count (Int) — 已采集的样本数

### AI推荐因子表

ai_recommendation_factors
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- factor_name (String) — 因子名称
- factor_weight (Decimal, 0-1) — 权重
- factor_category (Enum: content_authority / industry_relevance / source_credibility / entity_completeness / user_sentiment / timeliness)
- description (Text)
- data_period (Date)

### AI商机表

ai_opportunities
- id (UUID, PK)
- intent_id (UUID, FK -> user_intents.id)
- industry_id (UUID, FK -> industries.id)
- model_id (UUID, FK -> ai_models.id)
- query_frequency (Int) — 月查询频率
- current_occupants (Int) — 当前占位企业数
- competition_level (Enum: low / medium / high)
- potential_value (Decimal) — 预估商业价值
- confidence (Decimal)
- detected_at (DateTime)
- data_period (Date)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
if old_end in c:
    c = c.replace(old_end, old_end + new_03)
open(p03, "w", encoding="utf-8").write(c)
print("03 refined")