import os
p04 = os.path.join("D:\\GEO-IE\\docs\\04_Agent_OS设计.md")
c = open(p04, "r", encoding="utf-8").read()

# Upgrade Scanner Agent
old_scanner = "| **调用工具** | AI搜索API、评分引擎、告警系统 |"
new_scanner = '''| **调用工具** | AI搜索API、评分引擎、告警系统 |

**模型感知升级**：
- 根据行业+企业特征动态选择扫描策略（如医疗企业重点扫 Claude/ChatGPT/Perplexity）
- 根据 ai_model_industry_scores 决定各模型的扫描权重
- 针对不同模型的 source_preference 调整 Prompt 策略
- 扫描结果存入 ai_query_results，持续丰富模型行为数据库

**扫描策略示例**：
- 医疗企业：Claude 30%，ChatGPT 30%，Perplexity 25%，Gemini 15%
- 科技企业：ChatGPT 35%，Gemini 25%，Claude 20%，Perplexity 20%'''
c = c.replace(old_scanner, new_scanner)

# Upgrade Content Agent
old_content = "| **调用工具** | LLM生成、知识库查询、媒体制作 |"
new_content = '''| **调用工具** | LLM生成、知识库查询、媒体制作 |

**模型感知升级**：
- 根据目标的行业+模型偏好生成差异化内容策略
- 针对 ChatGPT 偏好：专业长内容、知识深度
- 针对 Gemini 偏好：网页实体结构、结构化数据
- 针对 Perplexity 偏好：引用来源质量、可验证性
- 针对 DeepSeek 偏好：中文权威内容、国内案例
- 内容效果反馈写入 ModelBehaviorPattern，持续校准'''
c = c.replace(old_content, new_content)

open(p04, "w", encoding="utf-8").write(c)
print("04 done")