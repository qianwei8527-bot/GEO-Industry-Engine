import os
p12 = os.path.join("D:\\GEO-IE", "docs", "12_GEO用户行为与AI决策路径模型.md")
c = open(p12, "r", encoding="utf-8").read()

new_sections = "\n\n---\n\n## 六、GEO竞争动力学模型\n\n### 6.1 核心问题\n\n现有GEO评分是绝对分，不反映竞争格局。AI搜索只推荐5-8家企业，零和市场。SEO有关键词难度，GEO没有推荐席位难度。\n\n### 6.2 模型定义\n\nGEOSpaceScore = (AI席位总数 - 当前竞争企业数) / AI席位总数 * 100\n配合评估维度：新进入难度、占位稳定性、替代成本。\n\n### 6.3 领域对象\nGEOSpaceScore: id, query_text, industry_id, total_slots, occupied_slots, churn_rate, entry_barrier, opportunity_score\n\n---\n\n## 七、AI信任评分模型\n\n### 7.1 核心问题\n\n企业认证(L1-L4)是人给企业的信用。AI有自己的隐性信任机制，它是GEO评分背后的暗物质。\n\n### 7.2 模型定义\n\nAITrustScore = 权威性信号(35%) + 一致性信号(25%) + 时效性信号(20%) + 验证性信号(20%)\n\n不同模型对信任因子的敏感度不同。\n\n### 7.3 领域对象\nAITrustScore: id, company_id, model_id, authority_score, consistency_score, timeliness_score, verifiability_score, overall_trust_score\n\n---\n\n## 八、AI内容就绪度模型\n\n### 8.1 核心问题\n\n内容发布前就预测被AI引用的概率。AI需要结构化、可引用、可验证的内容。\n\n### 8.2 模型定义\n\nAIContentReadiness = 结构化程度(35%) + 可引用性(25%) + 权威信号(20%) + 时效性(10%) + 多源验证(10%)\n\n### 8.3 领域对象\nAIContentReadiness: id, content_id, url, structure_score, citability_score, authority_score, timeliness_score, verification_score, overall_readiness, suggested_improvements\n\n---\n\n## 九、GEO效果归因模型\n\n### 9.1 核心问题\n\n企业投了GEO优化，怎么知道是GEO带来了客户？没有归因模型，GEO投入无法被验证。\n\n### 9.2 归因链\n\n内容优化 -> AI引用增加 -> 用户通过AI发现品牌 -> 用户访问 -> 转化 -> 收入归因\n\n### 9.3 归因模型类型\nLast-Touch, Linear, Time-Decay, Position-Based\n\n### 9.4 领域对象\nGEOAttribution: id, company_id, campaign_id, attribution_model, ai_impressions, ai_clicks, website_visits, conversions, revenue_attributed, roi"

old_ref = "## 六、关联文档"
c = c.replace(old_ref, new_sections + "\n\n---\n\n## 六、关联文档")

# Add domain objects to section 4
new_domain = "\n\n### 4.4 GEOSpaceScore\nSame fields as above\n\n### 4.5 AITrustScore\nSame fields as above\n\n### 4.6 AIContentReadiness\nSame fields as above\n\n### 4.7 GEOAttribution\nSame fields as above"
old_44 = "### 4.3 AIOpportunityScore"
c = c.replace(old_44, old_44 + new_domain)

open(p12, "w", encoding="utf-8").write(c)
print("12 updated")