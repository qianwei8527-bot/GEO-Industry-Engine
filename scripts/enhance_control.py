import os

# 1. 08_API接口规范.md: enhance ai-models endpoints with full CRUD
p08 = os.path.join("D:\\GEO-IE\\docs\\08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

old = """### 4.11 AI模型智能库（/api/v1/ai-models）

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
| GET | /ai-models/query-results | 查询结果样本列表 |"""

new = """### 4.11 AI模型智能库（/api/v1/ai-models）

#### 查询接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/ | 模型列表（支持筛选：type/country/status/access_type）|
| GET | /ai-models/{id} | 模型详情（含画像、指标、行为模式、行业热度）|
| GET | /ai-models/{id}/metrics | 模型指标数据 |
| GET | /ai-models/{id}/industry-scores | 模型-行业热度矩阵 |
| GET | /ai-models/{id}/behavior | 模型行为模式详情 |
| GET | /ai-models/{id}/sources | 模型来源偏好分布 |
| GET | /ai-models/{id}/query-results | 该模型的查询结果列表 |
| GET | /ai-models/comparison | 多模型对比（行业/来源/行为）|
| GET | /ai-models/ranking | 模型排名（按行业/地域/类型）|
| GET | /ai-models/query-results | 全部查询结果样本列表 |

#### 管理接口（手动操作）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /ai-models/ | 手动新增模型 |
| PUT | /ai-models/{id} | 编辑模型信息 |
| DELETE | /ai-models/{id} | 删除模型 |
| PUT | /ai-models/{id}/metrics | 手动录入/修正指标数据 |
| PUT | /ai-models/{id}/industry-scores | 调整特定行业的推荐热度 |
| PUT | /ai-models/{id}/behavior | 修正行为模式 |
| PUT | /ai-models/{id}/sources | 设置来源偏好权重 |
| POST | /ai-models/query | 手动触发向指定模型的查询 |

#### 管道管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/pipeline/status | 数据管道运行状态 |
| POST | /ai-models/pipeline/trigger | 手动触发管道执行 |
| GET | /ai-models/pipeline/logs | 管道执行日志 |"""

c = c.replace(old, new)

open(p08, "w", encoding="utf-8").write(c)
print("08 done")


# 2. 06_前端设计.md: add AI模型智能库 sub-page
p06 = os.path.join("D:\\GEO-IE\\docs\\06_前端设计.md")
c = open(p06, "r", encoding="utf-8").read()

old_page = "- 行业/企业/个人数据库 + AI回答库 + 知识图谱 + 研究资料库 + 跨行业对比面板 + API数据服务管理"
new_page = "- 行业/企业/个人数据库 + AI回答库 + 知识图谱 + 研究资料库 + 跨行业对比面板 + API数据服务管理\n- **AI模型智能库**：模型注册表、行为分析、来源偏好、行业热度矩阵、查询结果样本、管道状态看板"

c = c.replace(old_page, new_page)

# Add detail description for AI模型智能库 page
old_info = "### 6.5 数据中心"
new_info = """### 6.5 数据中心

- 行业/企业/个人数据库 + AI回答库 + 知识图谱 + 研究资料库 + 跨行业对比面板 + API数据服务管理 + **AI模型智能库**

#### AI模型智能库子页面

| 视图 | 功能 | 操作权限 |
|------|------|---------|
| 模型总览 | 全部模型列表（搜索/筛选/排序），模型总数统计 | 浏览 |
| 模型详情 | 基本信息 + 画像Tab + 指标Tab + 行为Tab + 来源Tab + 行业热度Tab | 浏览 |
| 模型对比 | 多模型横向对比（并排显示指标/行为/来源差异） | 浏览 |
| 查询结果 | 历史查询样本浏览（按模型/行业/时间筛选） | 浏览 |
| 数据管理 | 新增模型、编辑模型信息、删除模型、录入指标 | 管理员 |
| 管道状态 | 自动采集管道运行状态、最近执行时间、执行日志、手动触发 | 管理员 |
| 数据导出 | 模型数据库导出CSV/JSON | 认证用户 |

**可延展性**：
- 新模型出现时可手动新增或自动发现后确认入库
- 所有指标和评分可手动修正后覆盖自动计算结果
- 模型行为模式可手动调整和标注
- 来源偏好权重可手动校准"""

c = c.replace(old_info, new_info)

open(p06, "w", encoding="utf-8").write(c)
print("06 done")