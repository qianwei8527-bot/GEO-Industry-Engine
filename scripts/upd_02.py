import os
p02 = os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_objects = """

### 2.23 UserIntent（用户意图）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String | 意图名称 |
| category | Enum | industry_discovery / comparison / vendor_selection / solution_exploration / brand_verification |
| purchase_stage | Enum | awareness / evaluation / decision / need / validation |
| industry_id | UUID | FK -> Industry（可空）|
| commercial_value | Int | 商业价值评分 0-100 |
| description | Text | 意图描述 |
| example_prompt | Text | 典型问题示例 |
| geo_goal | Text | GEO优化目标 |
| created_at | DateTime |

**用途**：定义用户为什么问AI。每个Prompt背后的意图分类。

### 2.24 IntentModelScore（意图-模型得分）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| intent_id | UUID | FK -> UserIntent |
| model_id | UUID | FK -> AiModel |
| recommendation_weight | Decimal | 该模型对此意图的推荐权重(0-1) |
| top_factors | JSON | 主要推荐因子及占比 |
| confidence | Decimal | 置信度 |
| data_period | Date | 数据所属时期 |

**用途**：不同模型对不同意图的推荐倾向不同。存储每个模型在每个意图下的推荐因子权重。"""

old_end = "### 2.22 UserSearchSession（用户搜索会话）"
if old_end in c:
    c = c.replace(old_end, old_end + new_objects)
else:
    c += new_objects

open(p02, "w", encoding="utf-8").write(c)
print("02 done")