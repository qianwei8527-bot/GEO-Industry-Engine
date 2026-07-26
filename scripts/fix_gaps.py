import os

# ===== Fix 03_数据架构.md: add 3 missing tables =====
p03 = os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md")
c = open(p03, "r", encoding="utf-8").read()

new_tables = """

### 模型用户画像表（Layer 2）

model_user_personas
- id (UUID, PK)
- model_id (UUID, FK -> ai_models.id)
- user_group (String) — 用户群体（企业管理者/开发者/学生等）
- industry_focus (JSON) — 关注的行业列表
- decision_influence (Enum: high / medium / low) — 购买决策影响力
- estimated_share (Decimal) — 占模型用户比例
- data_source (String) — 数据来源
- confidence_level (Enum: high / medium / low)
- data_period (Date)
- updated_at (DateTime)

### Prompt知识库表（Layer 4）

prompt_knowledge_base
- id (UUID, PK)
- query_text (Text) — 问题原文
- query_category (Enum: industry / company / product / trend)
- industry_id (UUID, FK -> industries.id)
- model_id (UUID, FK -> ai_models.id)
- response_summary (Text) — 模型回答摘要
- mentioned_companies (JSON) — 提及的企业列表
- citations (JSON) — 引用来源URL列表
- mention_frequency (Decimal) — 企业出现频率(0-1)
- confidence (Decimal)
- queried_at (DateTime)
- data_period (Date)

### AI品牌排名表（Layer 5）

ai_brand_rankings
- id (UUID, PK)
- company_id (UUID, FK -> companies.id)
- ranking_date (Date) — 排行日期
- overall_score (Decimal) — 综合GEO评分(0-100)
- scores_by_model (JSON) — 各模型评分: {chatgpt:92, gemini:88, ...}
- trend_direction (Enum: up / down / stable)
- rank_position (Int) — 当前排名
- rank_change (Int) — 排名变化
- data_period (Date)"""

old_end = "# GEO产业引擎 — 数据库ER设计"
if old_end in c:
    c = c.replace(old_end, old_end + new_tables)

open(p03, "w", encoding="utf-8").write(c)
print("03 fixed: +3 tables")


# ===== Fix 08_API接口规范.md: add 3 missing API sections =====
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_apis = """

#### 用户画像接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/{id}/personas | 指定模型的用户画像列表 |
| PUT | /ai-models/{id}/personas | 更新用户画像数据 |
| GET | /ai-models/personas/comparison | 多模型用户画像对比 |

#### Prompt知识库接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /prompt-knowledge-base/ | 查询样本列表（支持按模型/行业/时间筛选）|
| GET | /prompt-knowledge-base/{id} | 查询样本详情（含完整回答+引用+提及企业）|
| POST | /prompt-knowledge-base/ | 手动新增查询样本 |
| GET | /prompt-knowledge-base/trends | 趋势分析（谁在上升/谁在下降）|
| POST | /prompt-knowledge-base/trigger-query | 手动触发向指定模型的查询并存入知识库 |

#### 品牌排名接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /brand-ranking/ | 品牌排名总榜（支持按行业/地域筛选）|
| GET | /brand-ranking/{company_id} | 指定企业的品牌排名详情（含各模型评分）|
| GET | /brand-ranking/industry/{industry_id} | 行业内的企业排名 |
| GET | /brand-ranking/trends | 排名变化趋势（上升最快/下降最快）|
| POST | /brand-ranking/refresh | 手动触发排名刷新计算"""

old_end = "### 4.11 AI模型智能库（/api/v1/ai-models）"
if old_end in c:
    c = c.replace(old_end, old_end + new_apis)

open(p08, "w", encoding="utf-8").write(c)
print("08 fixed: +3 API sections")