import os

# === 12 文档：完善结构，加 GEO决策智能 + AIOpportunityScore ===
p12 = os.path.join("D:\\GEO-IE", "docs", "12_GEO用户行为与AI决策路径模型.md")
c = open(p12, "r", encoding="utf-8").read()

# Add GEO Decision Intelligence concept after 1.2
old_after = "这三层决定GEO的商业价值。"
new_after = old_after + " 所以我们称之为 **GEO决策智能（GEO Decision Intelligence）**——预测哪些AI问题会产生商业价值，并指导企业占位。"

c = c.replace(old_after, new_after)

# Add AIOpportunityScore section after 4.2
old_opp = "### 4.2 IntentModelScore（意图-模型得分）"
new_opp = old_opp + """

### 4.3 AIOpportunityScore（AI商机评分）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| intent_id | UUID | FK -> UserIntent |
| industry_id | UUID | FK -> Industry |
| model_id | UUID | FK -> AiModel |
| query_frequency | Int | 该问题在AI搜索中的月出现频率 |
| current_occupants | Int | 当前已占位的企业数量 |
| competition_level | Enum | low/medium/high |
| potential_commercial_value | Decimal | 预估商业价值（元/月）|
| confidence | Decimal | 置信度 |
| data_period | Date | 数据所属时期 |

**用途**：核心商业产品。识别"高频率搜索、低竞品占位"的商机。例如：某行业每月10000次搜索"推荐XX供应商"，但只有2家企业被AI提及 → 这是高价值商机。"""

c = c.replace(old_opp, new_opp)

# Add for 5.1: GEO Decision Intelligence impact description
old_51 = "### 5.1 对AI可见度增长系统的影响"

new_51_intro = """

### 5.0 GEO决策智能在五大系统中的位置

GEO决策智能（GEO Decision Intelligence）不是一个独立系统，而是贯穿所有系统的核心逻辑：

| 系统 | 决策智能的应用 |
|------|-------------|
| AI可见度增长系统 | 不只看"是否被提到"，更看"在高价值意图中是否被提到" |
| 产业导航系统 | 增加"行业AI需求地图"层，显示该行业的高频问题 |
| 交易市场 | 增加"AI商机池"，推送未被占位的商业问题 |
| 认证体系 | 认证数据成为AI推荐因子 |
| 数据资产中心 | 增加用户意图数据库和商机数据库 |

"""

c = c.replace(old_51, new_51_intro + old_51)

open(p12, "w", encoding="utf-8").write(c)
print("12 refined")