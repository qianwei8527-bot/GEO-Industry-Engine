import os

# 00: Add scoring algorithm + pricing reference
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()
new_goals = """### 评分算法

GEO评分由9因子加权模型计算：实体清晰度(15%)+信任评分(15%)+内容就绪度(12%)+空间评分(12%)+竞争态势(10%)+行业相关(10%)+模型偏好(10%)+时效性(8%)+情感倾向(8%)。详见 16_GEO评分算法与模拟验证.md。

### 定价模型

四层SaaS定价：Free(免费) / Pro($99/mo) / Growth($499/mo) / Enterprise(定制)。交易市场抽佣8-15%。认证收费$99-999。详见 17_产品定义与商业模式.md。"""
old_goals = "### 评分算法"
c = c.replace(old_goals, new_goals)
open(p00, "w", encoding="utf-8").write(c)

# 01: Add algorithm summary
p01 = os.path.join("D:\\GEO-IE", "docs", "01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()
old_algo = "### AI模型智能库影响说明"
new_algo = "### GEO评分算法\n\nGEO评分 = EntityClarity(15%) + AITrustScore(15%) + AIContentReadiness(12%) + GEOSpaceScore(12%) + CompetitionScore(10%) + IndustryRelevance(10%) + ModelPreference(10%) + Timeliness(8%) + Sentiment(8%)。详见16_GEO评分算法与模拟验证.md。\n\n### " + old_algo
c = c.replace(old_algo, new_algo)
open(p01, "w", encoding="utf-8").write(c)

# 08: Add pricing/billing endpoints
p08 = os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md")
c = open(p08, "r", encoding="utf-8").read()
new_ep = """

#### 订阅与账单接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /plans/ | 产品定价方案列表 |
| POST | /subscriptions/ | 创建订阅 |
| GET | /subscriptions/me | 当前用户订阅详情 |
| PUT | /subscriptions/me | 变更订阅方案 |
| DELETE | /subscriptions/me | 取消订阅 |
| GET | /invoices/ | 账单历史 |
| GET | /usage/ | 使用量统计 |"""
old_ep = "### 4.11 AI模型智能库（/api/v1/ai-models）"
c = c.replace(old_ep, old_ep + new_ep)
open(p08, "w", encoding="utf-8").write(c)

# 04: Deepen Tool Layer with 9 model matrix
p04 = os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()
old_tool = "| Market Agent | 竞争矩阵、商业机会模型 | 需求匹配和商机推荐 |"
new_tool = old_tool + "\n\n### 九模型调用矩阵\n\n| 决策模型 | 调用Agent | 输入 | 输出 |\n|----------|----------|------|------|\n| EntityClarity | Scanner Agent | 企业ID | 实体完整度评分 |\n| AITrustScore | Content Agent | 企业ID+模型ID | 信任评分 |\n| AIContentReadiness | Content Agent | 内容URL | 就绪度分数+优化建议 |\n| GEOSpaceScore | Scanner Agent | 行业ID+查询 | 席位竞争分析 |\n| CompetitionScore | Market Agent | 企业ID+行业ID | 竞争差距报告 |\n| IndustryRelevance | Industry Agent | 企业ID+行业ID | 相关度评分 |\n| ModelPreference | Scanner Agent | 企业ID+模型ID | 推荐倾向评分 |\n| Timeliness | Data Agent | 企业ID | 信息新鲜度评分 |\n| Sentiment | Industry Agent | 企业ID+模型ID | 情感倾向评分 |"
c = c.replace(old_tool, new_tool)
open(p04, "w", encoding="utf-8").write(c)

print("00, 01, 08, 04 updated")
print('done')