import os
p06 = os.path.join("D:\\GEO-IE", "docs", "06_前端设计.md")
c = open(p06, "r", encoding="utf-8").read()

old_view = "| 模型生态地图 | 全球模型+中国模型列表（GEO价值标注、生态定位）| 浏览 |"
new_view = old_view + "\n| 用户行为分析 | 查询意图分布、会话模式分析、任务-模型关联矩阵、格式偏好统计 | 浏览+导出 |"

c = c.replace(old_view, new_view)

open(p06, "w", encoding="utf-8").write(c)
print("06 done")