import os

# === 12/14/15: 加算法阶段说明 ===
for fname in ['12_GEO用户行为与AI决策路径模型.md', '14_GEO实体智能与信息供应链模型.md', '15_GEO竞争情报与增长实验模型.md']:
    fp = os.path.join("D:\\GEO-IE", "docs", fname)
    c = open(fp, "r", encoding="utf-8").read()
    note = "\n\n> **算法阶段说明**：当前模型使用规则权重（Phase 1）。随着数据积累将演进到机器学习驱动（Phase 2），最终由Agent自主优化（Phase 3）。"
    # Add note to AITrustScore section if it exists
    if 'AITrustScore' in c and '权重' in c.split('AITrustScore')[1][:200]:
        # Find a good insertion point - after the AITrustScore formula
        marker = '验证性信号'
        if marker in c:
            c = c.replace(marker, marker + note, 1)
            open(fp, "w", encoding="utf-8").write(c)
            print(fname + " updated")
        else:
            print(fname + " marker not found")
    else:
        print(fname + " - skipped (no AITrustScore)")

# === 04_Agent_OS设计.md: 加Tool Layer描述 ===
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

tool_layer = """

## Agent Tool Layer（决策模型调用层）

不增加Agent数量。现有Agent通过Tool Layer调用决策模型：

| Agent | 调用模型 | 用途 |
|-------|---------|------|
| Scanner Agent | AI模型智能库、用户意图模型AIOpportunityScore、CompetitionMatrix | 生成模型感知的扫描策略 |
| Content Agent | AITrustScore、AIContentReadiness | 生成AI可理解、易引用的内容 |
| Industry Agent | 产业认知库、职业生态、IndustryIntelligence | 产业趋势分析和机会发现 |
| Market Agent | 竞争矩阵、商业机会模型 | 需求匹配和商机推荐 |
"""

old_end = "# GEO产业引擎 — Agent OS设计"
c = c.replace(old_end, old_end + tool_layer)
open(p04, "w", encoding="utf-8").write(c)
print("04 Agent Tool Layer added")