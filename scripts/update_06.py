import os
path = os.path.join("D:\\GEO-IE\\docs\\06_前端设计.md")
c = open(path, "r", encoding="utf-8").read()
c = c.replace("- Dashboard：GEO评分趋势图 + AI提及热力图 + 三线预测图", "- Dashboard：GEO评分趋势图 + AI提及热力图 + 三线预测图 + 竞争对标仪表盘(多企业对比) + ROI计算器(效果模拟)")
c = c.replace("- 行业/企业/个人数据库 + AI回答库 + 知识图谱 + 研究资料库", "- 行业/企业/个人数据库 + AI回答库 + 知识图谱 + 研究资料库 + 跨行业对比面板 + API数据服务管理")
open(path, "w", encoding="utf-8").write(c)
print("06 done")