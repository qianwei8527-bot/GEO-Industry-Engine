import os

# === 00_项目宪章.md: 加决策智能飞轮 + 模型分层 ===
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()

# Add GEO决策智能飞轮
flywheel = """

### GEO决策智能飞轮

整个项目的数据驱动闭环：

```
企业数据 -> 实体智能 -> AI理解 -> 用户需求 -> 推荐结果 -> 商业反馈 -> 模型优化 -> 企业增长
```

飞轮每转一圈，企业对AI推荐的理解和控制力就提升一层。
"""

old_end = "所有业务系统（可见度增长/产业导航/交易市场/认证/Agent）都基于这层认知数据运转。"
c = c.replace(old_end, old_end + flywheel)

# Add model layering after the 9 models table
old_models = "| AIGEOAttribution（效果归因）| GA4归因模型 | 投了GEO优化，带来了多少收入？ |"
new_models = old_models + "\n\n### 决策模型分层\n\n9个模型按认知→判断→增长三层组织：\n\n**第一层：认知模型** — 理解世界\n- EntityIntelligence（企业实体理解）\n- ModelIntelligence（AI模型理解）\n- IndustryIntelligence（产业理解）\n\n**第二层：判断模型** — 为什么推荐\n- AITrustScore（AI信任评分）\n- AIContentReadiness（AI内容就绪度）\n- CompetitionMatrix（竞争矩阵）\n\n**第三层：增长模型** — 怎么提升\n- GEOSpaceScore（推荐空间竞争）\n- GrowthExperiment（增长实验）\n- GEOAttribution（效果归因）\n- AIOpportunityScore（商业机会）\n\n> 第一阶段使用规则模型（固定权重），第二阶段演进为数据驱动（ML调整权重），第三阶段由Agent自主优化。"

c = c.replace(old_models, new_models)

open(p00, "w", encoding="utf-8").write(c)
print("00 updated")