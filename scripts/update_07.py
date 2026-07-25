import os
path = os.path.join("D:\\GEO-IE\\docs\\07_后端设计.md")
c = open(path, "r", encoding="utf-8").read()
c = c.replace("### 2.3 GEO Score Service", "### 2.3 Benchmarking and ROI Service\n| 接口 | 领域模型对应 | 说明 |\n|------|-----------|------|\n| 竞争对标 | Company | 多企业AI可见度对比分析 |\n| ROI计算 | GeoScore | GEO评分提升的商业价值换算 |\n| 成熟度评估 | Company Maturity | L1-L5成熟度模型计算 |\n| 行业对比 | Industry | 跨行业GEO指数横向对比 |\n\n### 2.4 GEO Score Service")
c = c.replace("### 2.6 Certification Service", "### 2.6 API Data Service\n| 接口 | 领域模型对应 | 说明 |\n|------|-----------|------|\n| API产品化 | 全领域 | 数据API封装+计量 |\n| API密钥管理 | User | 开发者API访问控制 |\n| 调用计量 | API Usage | 按调用量计费 |\n\n### 2.7 Certification Service")
open(path, "w", encoding="utf-8").write(c)
print("07 done")