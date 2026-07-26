import os
p08 = os.path.join("D:\\GEO-IE\\docs\\08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_section = """

### 4.11 AI模型智能库（/api/v1/ai-models）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/ | 模型列表（支持筛选：type/country/status）|
| GET | /ai-models/{id} | 模型详情（含画像、指标、行为模式）|
| GET | /ai-models/{id}/industry-scores | 模型-行业热度矩阵 |
| GET | /ai-models/{id}/behavior | 模型行为模式详情 |
| GET | /ai-models/{id}/sources | 模型来源偏好分布 |
| POST | /ai-models/query | 向指定模型发送查询并返回结果 |
| GET | /ai-models/comparison | 多模型对比（行业/来源/行为）|
| GET | /ai-models/ranking | 模型排名（按行业/地域/类型）|
| GET | /ai-models/query-results | 查询结果样本列表 |
"""

old_end = "### 4.10 Agent（/api/v1/agents）"
c = c.replace(old_end, old_end + new_section)

open(p08, "w", encoding="utf-8").write(c)
print("08 done")