import os

# === 00：引用新层 ===
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()
old = "AIGEOAttribution（效果归因）| GA4归因模型 | 投了GEO优化，带来了多少收入？ |"
new = old + '\n| GEOSpaceScore（推荐空间竞争）| - | 还有多少AI推荐席位可以占？ |\n| EntityIntelligence（实体智能）| - | AI眼中的企业画像完整吗？ |\n| InfoSupplyChain（信息供应链）| - | AI从哪里知道企业的信息？ |\n| CompetitionMatrix（竞争矩阵）| - | 你和竞争对手比怎么样？ |\n| GrowthExperiment（增长实验）| 内容实验框架 | 优化有效吗？效果可重复吗？ |'
c = c.replace(old, new)
open(p00, "w", encoding="utf-8").write(c)
print("00 updated")

# === 11：加P0-11 + P0-12 ===
p11 = os.path.join("D:\\GEO-IE", "docs", "11_MVP范围.md")
c = open(p11, "r", encoding="utf-8").read()
new = "\n\n### P0-11 实体智能与信息供应链（新增）\n- [ ] 企业实体画像模型（身份/能力/关系/信任完整度）\n- [ ] 信息源注册表与权威性评估\n- [ ] 信息供应链追踪\n- [ ] 行业知识图谱关系网络\n\n### P0-12 竞争情报与增长实验（新增）\n- [ ] 竞争矩阵（多企业多模型对比）\n- [ ] 可见度差距分析\n- [ ] 增长实验框架（假设→执行→重扫→评估）\n- [ ] 实验结果评估与学习沉淀"
c += new
p11_clean = open(p11, "r", encoding="utf-8").read() + new
open(p11, "w", encoding="utf-8").write(c if c.endswith(new) else p11_clean)
print("11 updated")