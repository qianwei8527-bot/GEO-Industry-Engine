import os
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

new_agent = """

### 11. Intent Analyst Agent（意图分析Agent）

| 属性 | 定义 |
|------|------|
| **职责** | 分析用户搜索意图、识别高商业价值问题、发现行业机会 |
| **输入** | Prompt样本、行业数据、用户搜索会话数据 |
| **输出** | 意图分类报告、高价值问题列表、行业机会分析 |
| **权限** | UserIntent 数据读写、PromptKnowledgeBase 查询 |
| **调用工具** | LLM意图分类、数据分析、报告生成 |

**核心任务**：
- 对新采集的Prompt做意图分类（5类意图）
- 识别高商业价值但低竞品占位的Prompt（商机发现）
- 分析行业-意图-模型关联（哪个行业在哪个模型上最适合什么意图）
- 输出优化建议给Content Agent和Scanner Agent

**在Agent协作中的位置**：
Industry Agent -> Intent Analyst -> Scanner Agent -> Content Agent"""

old_end = "### 10. QA Agent"
c = c.replace(old_end, old_end + new_agent)

open(p04, "w", encoding="utf-8").write(c)
print("04 done")