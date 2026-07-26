import os

# === 08：+/opportunities/ endpoints ===
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()

new_08 = """

#### 商机接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /opportunities/ | 商机列表（支持按行业/模型/竞争级别筛选）|
| GET | /opportunities/{id} | 商机详情 |
| GET | /opportunities/high-value | 高价值商机排行（高频率+低竞争）|
| GET | /opportunities/industry/{industry_id} | 指定行业商机分析 |
| POST | /opportunities/refresh | 手动刷新商机计算 |"""

old_end = "### 4.11 AI模型智能库（/api/v1/ai-models）"
c = c.replace(old_end, old_end + new_08)
open(p08, "w", encoding="utf-8").write(c)
print("08 refined")