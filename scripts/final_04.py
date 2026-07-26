import os

# === 04：删除 Intent Analyst Agent，扩展 Industry Agent + Scanner Agent ===
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

# 1. Remove Intent Analyst Agent section
old_intent_agent = "\n### 11. Intent Analyst Agent（意图分析Agent）\n\n| 属性 | 定义 |\n|------|------|\n| **职责** | 分析用户搜索意图、识别高商业价值问题、发现行业机会 |\n| **输入** | Prompt样本、行业数据、用户搜索会话数据 |\n| **输出** | 意图分类报告、高价值问题列表、行业机会分析 |\n| **权限** | UserIntent 数据读写、PromptKnowledgeBase 查询 |\n| **调用工具** | LLM意图分类、数据分析、报告生成 |\n\n**核心任务**：\n- 对新采集的Prompt做意图分类（5类意图）\n- 识别高商业价值但低竞品占位的Prompt（商机发现）\n- 分析行业-意图-模型关联（哪个行业在哪个模型上最适合什么意图）\n- 输出优化建议给Content Agent和Scanner Agent\n\n**在Agent协作中的位置**：\nIndustry Agent -> Intent Analyst -> Scanner Agent -> Content Agent"
c = c.replace(old_intent_agent, "")

# 2. Revert diagram (remove Intent Analyst)
old_diagram = "         |          |     Intent Analyst\n         |          |          |\n   +-----+-----+    |          |"
new_diagram = "   +-----+-----+    |          |"
c = c.replace(old_diagram, new_diagram)

# 3. Extend Industry Agent with intent analysis
old_industry = "| **调用工具** | Neo4j查询、数据爬取、报告生成 |"
new_industry = "| **调用工具** | Neo4j查询、数据爬取、报告生成 |\n\n**意图分析扩展**：\n- 分析本行业用户搜索意图分布（5类意图）\n- 识别行业内的高商业价值问题\n- 输出行业AI需求地图给Scanner Agent参考"
c = c.replace(old_industry, new_industry)

# 4. Extend Scanner Agent with intent-aware scanning
old_scanner = "**用户行为研究能力**"
new_scanner_ext = "**意图感知扫描**：\n- 根据 Industry Agent 输出的行业AI需求地图选择扫描优先级\n- 高商业价值意图对应的Prompt优先扫描\n- 高频率低占位问题触发商机预警\n\n**用户行为研究能力**"
c = c.replace(old_scanner, new_scanner_ext)

open(p04, "w", encoding="utf-8").write(c)
print("04 refined")