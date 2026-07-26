import os
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_behavior_api = """

#### 用户搜索行为分析接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /search-behavior/query-intents | 查询意图分布统计（按模型/行业/时间）|
| GET | /search-behavior/sessions | 搜索会话分析（会话深度、模型切换模式）|
| GET | /search-behavior/satisfaction | 用户满意度信号统计 |
| GET | /search-behavior/task-model-matrix | 任务类型X模型选择矩阵 |
| GET | /search-behavior/format-preference | 不同行业/任务的内容格式偏好统计 |"""

old_end = "### 4.11 AI模型智能库（/api/v1/ai-models）"
c = c.replace(old_end, old_end + new_behavior_api)

open(p08, "w", encoding="utf-8").write(c)
print("08 done")