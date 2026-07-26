import os
p02 = os.path.join("D:\\GEO-IE\\docs\\02_领域模型设计.md")
c = open(p02, "r", encoding="utf-8").read()

new_objects = """

### 2.19 PromptKnowledgeBase（Prompt知识库）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| query_text | Text | 问题原文 |
| query_category | Enum | industry/company/product/trend |
| industry_id | UUID | FK -> Industry |
| model_id | UUID | FK -> AiModel |
| response_summary | Text | 模型回答摘要 |
| mentioned_companies | JSON[] | 提及的企业列表 |
| citations | JSON[] | 引用来源URL列表 |
| mention_frequency | Decimal | 企业出现频率(0-1) |
| confidence | Decimal | 置信度 |
| queried_at | DateTime | 查询时间 |

**用途**：GEO Prompt Database 核心资产，每天监控谁上升谁下降。

---

### 2.20 UserPersona（模型用户画像）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| user_group | String | 用户群体 |
| industry_focus | JSON[] | 关注的行业 |
| decision_influence | Enum | high/medium/low 购买决策影响力 |
| estimated_share | Decimal | 占模型用户比例 |
| data_source | String | 来源 |
| confidence_level | Enum | high/medium/low |

---

### 2.21 AIBrandRanking（AI品牌排名）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| ranking_date | Date | 排行日期 |
| overall_score | Decimal | 综合GEO评分(0-100) |
| scores_by_model | JSON | 各模型评分 |
| trend_direction | Enum | up/down/stable |
| rank_position | Int | 当前排名 |
| rank_change | Int | 排名变化 |
| data_period | Date | 数据所属时期 |

**用途**：AI品牌排名系统核心输出，类似AI时代的Alexa/SimilarWeb。
"""

# Find the last domain object and append
marker = "**用途**：AI品牌排名系统核心输出，类似AI时代的Alexa/SimilarWeb。"
if marker in c:
    c += new_objects
else:
    # Insert after ModelSourcePreference section
    old_end = "### 2.18 ModelSourcePreference（模型来源偏好）"
    c = c.replace(old_end, old_end + new_objects)

open(p02, "w", encoding="utf-8").write(c)
print("02 done")