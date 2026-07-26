import os
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_apis = """

#### 用户意图接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /intents/ | 意图列表（支持按category/industry筛选）|
| GET | /intents/{id} | 意图详情（含商业价值评分、典型问题）|
| POST | /intents/ | 手动新增意图 |
| PUT | /intents/{id} | 编辑意图 |
| GET | /intents/industry/{industry_id} | 某行业的高价值意图排行 |
| GET | /intents/commercial-value-ranking | 商业价值排序 |

#### 决策路径接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /decision-paths/model-factors/{model_id} | 指定模型的推荐因子权重 |
| GET | /decision-paths/intent-analysis/{intent_id} | 指定意图的跨模型推荐对比 |
| GET | /decision-paths/brand-path/{company_id} | 指定企业的AI推荐路径分析 |
| POST | /decision-paths/analyze-prompt | 分析单条Prompt的意图和商业价值 |"""

old_end = "### 4.11 AI模型智能库（/api/v1/ai-models）"
c = c.replace(old_end, old_end + new_apis)

open(p08, "w", encoding="utf-8").write(c)
print("08 done")