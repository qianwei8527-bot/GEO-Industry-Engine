import os
p03 = os.path.join("D:\\GEO-IE\\docs\\03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_domain = """

## 十一、AI模型智能库（新增）

### 模型基础表

ai_models
- id (UUID, PK)
- name (String, unique)
- provider (String)
- country (String)
- type (Enum: general_search / vertical_search / recommendation)
- release_date (Date)
- api_available (Boolean)
- search_enabled (Boolean)
- status (Enum: active / deprecated / beta)
- last_updated (DateTime)
- created_at (DateTime)

### 模型指标表

ai_model_metrics
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- estimated_users (BigInt)
- market_share (Decimal)
- enterprise_adoption (Decimal)
- citation_rate (Decimal)
- avg_response_length (Int)
- knowledge_cutoff (Date)
- data_period (Date)

### 模型-行业热度表

ai_model_industry_scores
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- industry_id (UUID, FK -> industries.id)
- recommendation_rate (Decimal)
- avg_sentiment (Decimal)
- top_sources (JSON)
- confidence (Decimal)
- data_period (Date)

### 模型行为模式表

ai_model_behavior_patterns
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id, unique)
- answer_style (Enum: factual / analytical / conversational / summary)
- source_preference (JSON) — 来源权重分布
- language_bias (JSON) — 语言偏向
- update_sensitivity (Decimal)
- citation_behavior (JSON)
- content_format_preference (JSON)

### 模型查询结果表

ai_query_results
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- query_text (Text)
- query_category (Enum: industry / company / product / trend)
- industry_id (UUID, FK -> industries.id)
- response_text (Text)
- mentioned_entities (JSON)
- citations (JSON)
- response_time_ms (Int)
- queried_at (DateTime)

### 模型来源偏好表

ai_model_sources
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- source_type (Enum: official_site / news / wikipedia / reddit / academic / forums / social)
- weight (Decimal, 0-1)
- confidence (Decimal)
- data_period (Date)
"""

old_end = "# GEO产业引擎 — 数据库ER设计"
c = c.replace(old_end, old_end + new_domain)

open(p03, "w", encoding="utf-8").write(c)
print("03 done")