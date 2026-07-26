import os

# === 02：+AIRecommendationFactor +AIOpportunityScore ===
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_02 = """

### 2.25 AIRecommendationFactor（AI推荐因子）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| factor_name | String | 因子名称（如"知识权威性"）|
| factor_weight | Decimal | 在该模型中的权重(0-1) |
| factor_category | Enum | content_authority / industry_relevance / source_credibility / entity_completeness / user_sentiment / timeliness |
| description | Text | 因子说明 |
| data_period | Date | |

**用途**：存储每个AI模型的推荐因子权重。不同模型对不同因素的重视程度不同，这是GEO策略的核心依据。

### 2.26 AIOpportunityScore（AI商机评分）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| intent_id | UUID | FK -> UserIntent |
| industry_id | UUID | FK -> Industry |
| model_id | UUID | FK -> AiModel |
| query_frequency | Int | 月查询频率 |
| current_occupants | Int | 当前占位企业数 |
| competition_level | Enum | low/medium/high |
| potential_value | Decimal | 预估商业价值 |
| confidence | Decimal | 置信度 |
| data_period | Date | |

**用途**：核心商业产品。识别高频率搜索但低竞品占位的商机。"""

old_end = "### 2.24 IntentModelScore（意图-模型得分）"
c = c.replace(old_end, old_end + new_02)
open(p02, "w", encoding="utf-8").write(c)
print("02 refined")