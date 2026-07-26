import os
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

# Add user behavior scanning to Scanner Agent
old_scanner = "#### 扫描策略示例"
new_scanner = """**用户行为研究能力**：
- 扫描并分类用户查询意图（factual/comparative/exploratory/transactional）
- 跟踪用户在多模型间的切换模式（session级行为）
- 分析用户满意度信号（点击引用/继续追问/离开）
- 洞察任务类型与模型选择的关联规律

#### 扫描策略示例"""
c = c.replace(old_scanner, new_scanner)

# Add format-aware generation to Content Agent
old_content = "**模型感知升级**"
new_content = "**格式感知生成**：\n- 根据查询意图选择最优回答格式（factual→段落, comparative→表格, exploratory→列表, transactional→结构化）\n- 不同行业默认格式不同（电商→表格, 医疗→段落, 法律→列表）\n- 用户满意度信号反馈校准格式选择\n\n**模型感知升级**"
c = c.replace(old_content, new_content)

open(p04, "w", encoding="utf-8").write(c)
print("04 done")