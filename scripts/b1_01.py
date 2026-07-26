import os, re
p01 = os.path.join("D:\\GEO-IE\\docs\\01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()

# 1. Add AI Model Intelligence to data assets table
old = "| API数据服务 | 企业/行业GEO数据API访问，支持按调用量计费 | 数据服务层 |"
new = old + '\n| AI模型智能库 | 全模型注册表、用户量估算、行业热度矩阵、来源偏好、查询结果样本 | 自建追踪管道+AI分析 |'
c = c.replace(old, new)

# 2. Add description of AI model intelligence after the data assets table
old_end = "## 六、跨地图通用能力"
new_before = "\n\n### AI模型智能库影响说明\n\nAI模型智能库不是独立系统，而是GEO数据资产中心的核心智能子模块。它影响：\n\n- **GEO评分引擎**：模型成为评分变量——不同模型的引用行为、来源偏好、行业倾向直接影响企业的GEO评分\n- **Scanner Agent**：根据行业+目标企业+模型权重选择扫描策略（如医疗企业重点扫描Claude/ChatGPT/Perplexity）\n- **Content Agent**：针对不同模型偏好生成差异化内容策略\n- **产业导航地图**：模型-行业热度矩阵为地图提供\"哪个行业在哪个模型最火\"的数据层\n\n内部架构：\n\n```\nGEO数据资产中心\n├── 数据层：行业/企业/Prompt/回答/研究资料\n└── 智能层：AI Model Intelligence\n    ├── Model Profile（模型画像）\n    ├── Model Behavior（行为模式）\n    ├── Industry Preference（行业偏好）\n    ├── Source Preference（来源偏好）\n    ├── Query Result（查询结果）\n    └── Ranking Signal（排名信号）\n```"
c = c.replace(old_end, new_before + "\n\n" + old_end)
open(p01, "w", encoding="utf-8").write(c)
print("01 done")