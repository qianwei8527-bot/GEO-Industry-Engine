import os
path = os.path.join("D:\\GEO-IE\\docs\\08_API接口规范.md")
c = open(path, "r", encoding="utf-8").read()
c = c.replace("### 4.7 数据查询（/api/v1/data）", "### 4.7 对标与ROI（/api/v1/benchmark）\n\n| 方法 | 路径 | 说明 |\n|------|------|------|\n| POST | /benchmark/compare | 多企业AI可见度对比 |\n| GET | /benchmark/industry | 跨行业指数对比 |\n| GET | /benchmark/roi | ROI计算 |\n| GET | /benchmark/maturity | 企业GEO成熟度评估 |\n\n### 4.8 数据查询（/api/v1/data）")
c = c.replace("### 4.8 Agent（/api/v1/agents）", "### 4.9 API数据服务（/api/v1/data-api）\n\n| 方法 | 路径 | 说明 |\n|------|------|------|\n| POST | /data-api/keys | 创建API密钥 |\n| GET | /data-api/keys | 密钥列表 |\n| GET | /data-api/usage | 调用量统计 |\n\n### 4.10 Agent（/api/v1/agents）")
open(path, "w", encoding="utf-8").write(c)
print("08 done")