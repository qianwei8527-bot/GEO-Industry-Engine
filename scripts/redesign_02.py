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
| mentioned_companies | JSON[] | 回答中提及的企业列表 |
| citations | JSON[] | 引用的来源URL列表 |
| citation_types | JSON | 来源类型分布（官网/X/新闻/论文等）|
| mention_frequency | Decimal | 该企业的出现频率(0-1) |
| confidence | Decimal | 置信度 |
| queried_at | DateTime | 查询时间 |
| data_period | Date | 数据所属时期 |

**用途**：GEO Prompt Database 的核心资产。每天监控谁在上升、谁在下降。

---

### 2.20 UserPersona（模型用户画像）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| model_id | UUID | FK -> AiModel |
| user_group | String | 用户群体（企业管理者/开发者/学生等）|
| industry_focus | JSON[] | 该群体关注的行业 |
| decision_influence | Enum | high/medium/low 购买决策影响力 |
| estimated_share | Decimal | 该群体占模型用户的比例 |
| data_source | String | 数据来源 |
| confidence_level | Enum | high/medium/low |

---

### 2.21 AIBrandRanking（AI品牌排名）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| ranking_date | Date | 排行日期 |
| overall_score | Decimal | 综合GEO评分(0-100) |
| scores_by_model | JSON | 各模型评分：{chatgpt:92, gemini:88, ...} |
| scores_by_metric | JSON | 各维度评分：{visibility:90, sentiment:85, ...} |
| trend_direction | Enum | up/down/stable |
| trend_change | Decimal | 变化幅度 |
| rank_position | Int | 当前排名 |
| rank_change | Int | 排名变化 |
| data_period | Date | 数据所属时期 |

**用途**：AI品牌排名系统的核心输出。类似AI时代的Alexa/SimilarWeb排名。
"""

# Insert after PromptKnowledgeBase
old_end = "### 2.18 ModelSourcePreference（模型来源偏好）"
new_end = old_end + "\n" + new_objects
c = c.replace(new_end, c  # placeholder, actually this won't work right

open(p02, "w", encoding="utf-8").write(c)
print("02 done")