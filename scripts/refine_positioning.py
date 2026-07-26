import os

# === 00_项目宪章.md: Add infrastructure positioning + 5-layer product structure ===
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()

old_core = "GEO-Engine = AI时代的供应商上榜系统。构建企业在AI世界中的定位、认知、信任、推荐和交易基础设施。"
new_core = "GEO产业基础设施平台。每个人都能在这里找到自己的位置——企业发现AI推荐中的定位，个人发现产业中的成长路径，机构发现生态中的连接机会。"

old_systems = "### 评分算法"
new_systems = """### 产品层级结构

| 层级 | 产品 | 定位 | 用户 |
|------|------|------|------|
| 入口层 | GEO企业AI可见度诊断（免费） | 第一入口，零门槛获客 | 所有企业 |
| 增长层 | AI可见度SaaS（订阅） | 持续监测与优化 | 付费企业 |
| 生态层 | 产业地图 + 认证 + 交易 | 连接与信任 | 企业/个人/服务商 |
| 资产层 | GEO数据资产中心 | 数据沉淀与智能 | 平台自身 |
| 智能层 | Agent OS（远期） | 自动化 | 平台自身 |

### 评分算法"""

c = c.replace(old_core, new_core)
c = c.replace(old_systems, new_systems)
open(p00, "w", encoding="utf-8").write(c)
print("00 done")

# === README.md: Update positioning ===
pr = os.path.join("D:\\GEO-IE", "README.md")
c = open(pr, "r", encoding="utf-8").read()

old_title = "**AI时代企业智能可见度基础设施与GEO产业生态平台**"
new_title = "**GEO产业基础设施平台 — 让企业成为AI搜索推荐首选，让每个人找到自己的位置**"

old_sub = "> 构建企业在AI世界中的定位、认知、信任、推荐和交易基础设施。"
new_sub = "> 一个开放的GEO产业基础设施：企业在这里了解AI推荐中的自己，个人在这里发现产业中的成长路径，机构在这里连接生态中的机会。"

old_pos = "以智能认知为底座，以产业地图为入口，以交易市场完成商业闭环。"
new_pos = "以AI诊断免费入口获客，以增长SaaS持续服务，以产业地图+认证+交易构建生态，以数据资产和Agent构建长期壁垒。"

old_arch = "### 1. AI可见度增长系统"
new_arch = """### 入口层：GEO企业AI可见度诊断（免费）

输入企业信息，10秒生成AI推荐报告：AI怎么看你、和竞争对手比怎么样、哪里需要优化。

### 增长层：AI可见度SaaS（订阅）

持续监测AI推荐变化，追踪优化效果，接收竞争预警。

### 生态层：产业地图 + 认证 + 交易

在产业地图中找到自己的位置，通过认证建立信任，在交易市场中连接服务和需求。

### 资产层：GEO数据资产中心

行业数据、企业数据、AI推荐数据、用户意图数据，构成GEO产业知识图谱。

### 智能层：Agent OS（远期）

AI Agent自动监测、分析、优化和执行。

---

### 1. AI可见度增长系统"""

c = c.replace(old_title, new_title)
c = c.replace(old_sub, new_sub)
c = c.replace(old_pos, new_pos)
c = c.replace(old_arch, new_arch)
open(pr, "w", encoding="utf-8").write(c)
print("README done")

# === 01_产品架构PRD.md: Add 5-layer product structure ===
p01 = os.path.join("D:\\GEO-IE", "docs", "01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()

old_start = "## 一、AI可见度增长系统"
new_start = """## 产品层级总览

| 层级 | 产品 | 阶段 |
|------|------|------|
| 入口层 | GEO企业AI可见度诊断（免费） | MVP |
| 增长层 | AI可见度SaaS（订阅） | MVP |
| 生态层 | 产业地图 + 认证 + 交易 | v2-v3 |
| 资产层 | GEO数据资产中心 | 持续 |
| 智能层 | Agent OS | 远期(P5)|

---

## 一、AI可见度增长系统"""

c = c.replace(old_start, new_start)
open(p01, "w", encoding="utf-8").write(c)
print("01 done")

print("All done")