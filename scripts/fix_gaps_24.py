import os

p24 = os.path.join("D:\\GEO-IE", "docs", "24_执行方案与90天计划.md")
c = open(p24, "r", encoding="utf-8").read()

new_content = """

---

## 补充：遗漏清单

### 1. API端点清单（按Sprint）

| Sprint | Endpoint | 说明 |
|--------|----------|------|
| 1-2 | POST /auth/register, /auth/login | 用户注册登录 |
| 1-2 | GET /health | 健康检查 |
| 3-4 | GET /users/me, PUT /users/me | 用户管理 |
| 3-4 | POST /companies, GET /companies/{id}, PUT /companies/{id} | 企业CRUD |
| 5-6 | GET /geo-score/{company_id} (Mock) | 评分查询(模拟数据) |
| 7-8 | GET /geo-score/{company_id} (真实) | 评分查询(真实数据) |
| 7-8 | GET /geo-score/{company_id}/history | 评分趋势 |
| 9-10 | GET /reports/{company_id} | 报告生成 |
| 9-10 | POST /subscriptions, GET /subscriptions/me | 订阅管理 |
| 11-12 | (维护) | 上线支持 |

### 2. 成本预估

| 项目 | 月费用 | 说明 |
|------|--------|------|
| OpenAI API | $50-150 | GPT-4o mini, ~0.01-0.03/次 |
| Gemini API | $30-100 | Gemini 1.5 Pro, ~0.01/次 |
| DeepSeek API | $5-20 | DeepSeek Chat, ~0.001/次 |
| 服务器(开发) | $50-100 | 1台云服务器 |
| 服务器(生产) | $100-300 | 2台+负载均衡 |
| 域名+邮箱 | $10-20 | DNS+企业邮箱 |
| **合计** | **$245-690/月** | 初期低成本运行 |

### 3. API Key申请周期

| 模型 | 申请方式 | 预计周期 | 注意事项 |
|------|---------|---------|---------|
| OpenAI | 官网注册+绑定信用卡 | 即时-1天 | 需要海外信用卡 |
| Google AI | Google Cloud Console | 即时-1天 | 需要Google账号 |
| DeepSeek | 官网注册 | 即时 | 国内手机号 |
| Anthropic Claude | 官网申请(可选) | 1-3天 | (备用模型，非必须) |

**建议Week 1就申请所有API Key**，Week 5-6集成时确保可用。

### 4. 开发期间用户反馈计划

| 阶段 | 反馈方式 | 目标 | 指标 |
|------|---------|------|------|
| Week 4 | 向3-5家B2B企业展示Mock原型 | 验证方向是否对 | 用户能理解产品价值 |
| Week 8 | 5-10家B2B企业试用PoC | 验证产品可用性 | 完成率>60% |
| Week 10 | 10-20家Beta用户 | 验证付费意愿 | Free->Pro转化率>5% |
| Week 12 | 公开上线 | 验证市场接受度 | 注册量>100 |

### 5. 错误处理策略

| 场景 | 策略 | 用户看到 |
|------|------|---------|
| LLM API超时/限流 | 重试3次+降级到Mock数据 | 页面正常显示(数据可能来自历史) |
| LLM响应格式异常 | 用LLM重新解析或跳过 | 部分指标缺失，标注"数据暂缺" |
| 评分计算异常 | 使用上次有效评分 | 显示"上次更新时间: XX分钟前" |
| 数据库连接失败 | 使用Redis缓存数据 | 正常使用(数据可能有分钟级延迟) |
| 前端API调用失败 | 重试2次+显示友好错误 | 提示"网络异常，请稍后刷新" |
"""

c += new_content
open(p24, "w", encoding="utf-8").write(c)
print("24 updated with gaps: " + str(os.path.getsize(p24)) + " bytes")