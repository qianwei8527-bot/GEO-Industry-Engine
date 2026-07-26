import os

# === 13：添加GEO产业认知库概念 + 3个新领域对象 ===
p13 = os.path.join("D:\\GEO-IE", "docs", "13_GEO产业发展趋势与职业生态模型.md")
c = open(p13, "r", encoding="utf-8").read()

# Add GEO产业认知库 concept after the first line
old_head = "> 第三个认知层：这个产业怎么发展？谁参与？谁赚钱？产生哪些岗位？"
new_head = old_head + "\n\n> **内部定位：GEO产业认知库** — 不只是存数据的数据库，而是包含趋势推理、职业图谱、商业机会分析的认知资产库。"

c = c.replace(old_head, new_head)

# Add 3 new domain objects after GEOCareerPath
old_domain_end = "- required_experience (String)"
new_domain = old_domain_end + """

### GEOIndustryTrend（产业趋势）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| trend_name | String | 趋势名称 |
| trend_category | Enum | technology/market/business_model/policy |
| industry_id | UUID | FK -> Industry |
| time_horizon | String | 时间范围（2025/2027/2030）|
| impact_level | Int | 影响程度(1-5) |
| description | Text | 趋势描述 |
| evidence | JSON | 支撑证据 |
| confidence | Decimal | 置信度 |
| data_period | Date | |

### TalentDemand（人才需求）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| role_id | UUID | FK -> GEOJob |
| industry_id | UUID | FK -> Industry |
| demand_count | Int | 需求量 |
| demand_growth | Decimal | 需求增长率 |
| avg_salary | Decimal | 平均薪资 |
| skill_gap | JSON | 技能缺口分析 |
| data_period | Date | |

### BusinessOpportunity（商业机会）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| industry_id | UUID | FK -> Industry |
| opportunity_type | Enum | service_gap/talent_shortage/market_entry/technology_adoption |
| description | Text | 机会描述 |
| potential_value | Decimal | 预估价值 |
| entry_barrier | Enum | low/medium/high |
| time_window | String | 时间窗口 |
| confidence | Decimal | 置信度 |"""

c = c.replace(old_domain_end, new_domain)
open(p13, "w", encoding="utf-8").write(c)
print("13 updated")

# === 01：数据资产中心加GEO产业认知库 ===
p01 = os.path.join("D:\\GEO-IE", "docs", "01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()

old_01 = "AI模型智能库影响说明"
new_01 = "GEO产业认知库 — GEO产业发展趋势、职业生态、商业机会分析。见 13_GEO产业发展趋势与职业生态模型.md\n\n### " + old_01
c = c.replace(old_01, new_01)
open(p01, "w", encoding="utf-8").write(c)
print("01 updated")

# === 04：Industry Agent 加趋势分析 ===
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

old_04 = "| **调用工具** | Neo4j查询、数据爬取、报告生成 |"
new_04 = old_04 + "\n\n**产业趋势分析扩展**：\n- 调用 GEO产业认知库 的趋势数据\n- 分析GEO产业生命周期阶段和商业模式演进\n- 识别产业链各环节的商业机会\n- 预测岗位需求和技能缺口\n- 输出产业趋势报告给 CEO Agent 决策参考"
c = c.replace(old_04, new_04)
open(p04, "w", encoding="utf-8").write(c)
print("04 updated")

# === 05：加趋势数据采集管道 ===
p05 = os.path.join("D:\\GEO-IE", "docs", "05_技术架构.md")
c = open(p05, "r", encoding="utf-8").read()

new_pipeline = """

## 趋势与职业数据采集管道（新增）

### 数据源

| 数据 | 采集方式 | 频率 |
|------|---------|------|
| 行业报告（Gartner/IDC等） | 爬虫+API | 每周 |
| 招聘数据（招聘网站） | API | 每天 |
| 技术趋势（GitHub/论文） | API | 每天 |
| 商业新闻（行业媒体） | RSS+爬虫 | 每天 |
| 政策信息（政府网站） | RSS | 每天 |

### 处理流程

```
数据采集 -> NLP解析 -> 趋势识别 -> 置信度评估 -> 入库
```

### 与产业导航的集成

趋势和职业数据直接影响产业导航的发展方向地图和职业生态子模块。"""

old_end = "# GEO产业引擎 — 技术架构"
c = c.replace(old_end, old_end + new_pipeline)
open(p05, "w", encoding="utf-8").write(c)
print("05 updated")