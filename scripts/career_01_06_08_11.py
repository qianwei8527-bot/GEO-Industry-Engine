import os

# === 01：产业导航系统加职业生态描述 ===
p01 = os.path.join("D:\\GEO-IE", "docs", "01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()

# Add career ecosystem to the navigation system description (after 教育成长层)
old_career = "每一层都支持：**展示**（可视化呈现）、**连接**（点击跳转关联信息）、**评论**（用户参与讨论）、**自动更新**（数据层实时同步变化）。"
if old_career in c:
    added = old_career + "\n\n**GEO职业生态** — 产业导航系统新增职业子模块：\n- 产业链地图（上中下游结构）\n- GEO岗位体系（7个核心岗位定义）\n- 技能等级体系（L1-L4能力模型）\n- 人才成长路径（4条发展路径）\n- 企业能力需求（按GEO成熟度对应人才需求）\n- 市场趋势预测（GEO产业生命周期、商业模式演进）"
    c = c.replace(old_career, added)
    open(p01, "w", encoding="utf-8").write(c)
    print("01 done")
else:
    print("01 marker not found")

# === 06：产业导航加人才地图/职业生态视图 ===
p06 = os.path.join("D:\\GEO-IE", "docs", "06_前端设计.md")
c = open(p06, "r", encoding="utf-8").read()

old_nav = "### 6.3 产业导航"
new_nav = """### 6.3 产业导航

- 5张交互地图（生态/商业/运营/地域/发展）
- 每层支持：监控面板 + 建议按钮 + 新增节点 + 评论
- GEO职业生态子页面（新增）：
  - 产业链地图：上中下游结构展示
  - 岗位墙：7个GEO岗位卡片展示（职责/技能/薪资/需求量）
  - 技能体系：L1-L4技能等级可视化
  - 成长路径：4条路径的交互式职业树
  - 趋势看板：市场TAM/SAM/SOM数据展示
  - 企业需求：按成熟度对应的人才匹配"""

c = c.replace(old_nav, new_nav)
open(p06, "w", encoding="utf-8").write(c)
print("06 done")

# === 08：+/career/ endpoints ===
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_career = """

#### GEO职业生态接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /career/jobs | 岗位列表（按category/level筛选）|
| GET | /career/jobs/{id} | 岗位详情（含技能要求、薪资、发展路径）|
| GET | /career/skills | 技能列表（按category筛选）|
| GET | /career/paths | 职业路径图（完整发展网络）|
| GET | /career/industry-demand | 企业能力需求（按成熟度匹配人才）|
| GET | /career/market-trends | 市场趋势数据（TAM/SAM/SOM）|"""

old_end = "### 4.11 AI模型智能库（/api/v1/ai-models）"
c = c.replace(old_end, old_end + new_career)
open(p08, "w", encoding="utf-8").write(c)
print("08 done")

# === 11：+P0-10 career ecology ===
p11 = os.path.join("D:\\GEO-IE", "docs", "11_MVP范围.md")
c = open(p11, "r", encoding="utf-8").read()

new_mvp = """

### P0-10 GEO职业生态（新增）
- [ ] GEO职业体系设计（7个岗位定义+薪资+需求量）
- [ ] GEO技能体系（L1-L4能力模型）
- [ ] 人才成长路径（4条发展路径）
- [ ] 企业能力需求匹配（按GEO成熟度）"""

c += new_mvp
open(p11, "w", encoding="utf-8").write(c)
print("11 done")