import os

# 03_数据架构.md: fix ai_model_metrics fields
p03 = os.path.join("D:\\GEO-IE\\docs\\03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

old_metrics = """ai_model_metrics
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- estimated_users (BigInt)
- market_share (Decimal)
- enterprise_adoption (Decimal)
- citation_rate (Decimal)
- avg_response_length (Int)
- knowledge_cutoff (Date)
- data_period (Date)"""

new_metrics = """ai_model_metrics
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- estimated_monthly_users (BigInt) — 估算月活
- data_source (String) — 来源（公开报告/内部估算/第三方）
- confidence_level (Enum: high / medium / low) — 置信度
- market_share (Decimal)
- enterprise_adoption (Decimal)
- citation_rate (Decimal)
- avg_response_length (Int)
- knowledge_cutoff (Date)
- last_updated (DateTime)
- data_period (Date)"""

c = c.replace(old_metrics, new_metrics)

# 03_数据架构.md: add access_type to ai_models
old_models = """ai_models
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
- created_at (DateTime)"""

new_models = """ai_models
- id (UUID, PK)
- name (String, unique)
- provider (String)
- country (String)
- type (Enum: general_search / vertical_search / recommendation)
- access_type (Enum: official_api / web_only / third_party_api / unknown) — GEO检测接入方式
- release_date (Date)
- api_available (Boolean)
- search_enabled (Boolean)
- status (Enum: active / deprecated / beta)
- last_updated (DateTime)
- created_at (DateTime)"""

c = c.replace(old_models, new_models)

open(p03, "w", encoding="utf-8").write(c)
print("03 done")

# 02_领域模型设计.md: update ModelMetrics
p02 = os.path.join("D:\\GEO-IE\\docs\\02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

old_metrics_domain = """| estimated_users | BigInt | 估算月活用户 |"""
new_metrics_domain = """| estimated_monthly_users | BigInt | 估算月活用户 |
| data_source | String | 数据来源（公开报告/内部估算/第三方）|
| confidence_level | Enum | high/medium/low 置信度 |
| last_updated | DateTime | 最近更新时间 |"""

c = c.replace(old_metrics_domain, new_metrics_domain)

# Add access_type to AiModel
old_access = "| type | Enum | general_search/vertical_search/recommendation |"
new_access = old_access + "\n| access_type | Enum | GEO检测接入方式: official_api/web_only/third_party_api/unknown |"
c = c.replace(old_access, new_access)

open(p02, "w", encoding="utf-8").write(c)
print("02 done")

# 04_Agent_OS设计.md: add 03 reference
p04 = os.path.join("D:\\GEO-IE\\docs\\04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

old_ref = "| [07_后端设计.md](07_后端设计.md) | Agent服务的后端实现 |"
new_ref = old_ref + "\n| [03_数据架构.md](03_数据架构.md) | AI模型智能库数据表定义、AI回答数据结构、模型行为数据结构 |"

c = c.replace(old_ref, new_ref)

open(p04, "w", encoding="utf-8").write(c)
print("04 done")