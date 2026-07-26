import os
p05 = os.path.join("D:\\GEO-IE\\docs\\05_技术架构.md")
c = open(p05, "r", encoding="utf-8").read()

new_section = """

## 模型追踪管道（新增）

### 数据流转

```
公开数据采集（模型官网/新闻/行业报告）
    |
    v
模型注册表引擎（定时扫描新模型出现）
    |
    v
AI API 查询引擎（向各模型发送行业查询Prompt）
    |
    v
查询结果解析（提取回答、引用来源、提及实体）
    |
    v
模型行为分析（来源偏好、行业倾向、回答模式）
    |
    v
GEO评分校准（模型权重纳入评分算法）
```

### 数据源

| 数据 | 采集方式 | 频率 |
|------|---------|------|
| 模型基础信息 | 官网+新闻+社区 | 每周 |
| 用户量估算 | Similarweb方法论+抽样 | 每月 |
| 模型-行业热度 | AI API 批量查询 | 每天 |
| 来源偏好 | 查询结果统计分析 | 每天 |
| 查询结果样本 | 向各模型发送标准Prompt | 每天 |

### AI Model Intelligence Pipeline 架构

| 组件 | 技术选型 | 功能 |
|------|---------|------|
| 模型注册表 | PostgreSQL | 存储模型基础信息 |
| 查询引擎 | Python + httpx | 向各AI API发送查询 |
| 结果解析 | LLM + 正则 | 提取回答中的结构化信息 |
| 行为分析 | 统计分析 + ML | 识别模型偏好和趋势 |
| 评分校准 | Python | 将模型因素纳入GEO评分 |
"""

old_end = "# GEO产业引擎 — 技术架构"
c = c.replace(old_end, old_end + new_section)

open(p05, "w", encoding="utf-8").write(c)
print("05 done")