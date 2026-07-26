import os

c2 = open(os.path.join("D:\\GEO-IE", "docs", "02_领域模型设计.md"), "r", encoding="utf-8").read()
c3 = open(os.path.join("D:\\GEO-IE", "docs", "03_数据架构.md"), "r", encoding="utf-8").read()
c8 = open(os.path.join("D:\\GEO-IE", "docs", "08_API接口规范.md"), "r", encoding="utf-8").read()
c6 = open(os.path.join("D:\\GEO-IE", "docs", "06_前端设计.md"), "r", encoding="utf-8").read()
c1 = open(os.path.join("D:\\GEO-IE", "docs", "01_产品架构PRD.md"), "r", encoding="utf-8").read()
c4 = open(os.path.join("D:\\GEO-IE", "docs", "04_Agent_OS设计.md"), "r", encoding="utf-8").read()

checks = []
passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        checks.append("[PASS] " + name)
        passed += 1
    else:
        checks.append("[FAIL] " + name)
        failed += 1

# ========== Layer 1: Model Ecosystem ==========
check("L1 01描述全球通用模型", "ChatGPT" in c1 and "Gemini" in c1 and "Claude" in c1)
check("L1 01描述中国市场模型", "DeepSeek" in c1 and "通义千问" in c1 and "豆包" in c1)
check("L1 02领域对象 AiModel 属性完整", "access_type" in c2 and "provider" in c2 and "country" in c2)
check("L1 03数据表 ai_models 存在", "ai_models" in c3)
check("L1 03 ai_models 含 access_type", "access_type" in c3 and "official_api" in c3)
check("L1 08 API /ai-models/ 全部CRUD", "手动新增模型" in c8 and "编辑模型信息" in c8 and "删除模型" in c8)

# ========== Layer 2: User Persona ==========
check("L2 02领域对象 UserPersona 存在", "UserPersona" in c2)
check("L2 02 UserPersona 属性完整", "user_group" in c2 and "decision_influence" in c2)
check("L2 03数据表 model_user_personas 存在", "model_user_personas" in c3)
check("L2 08 API /personas 存在", "/personas" in c8)

# ========== Layer 3: Industry x Model ==========
check("L3 01行业x模型矩阵 含6行业", "医疗" in c1 and "电商" in c1 and "金融" in c1)
check("L3 02领域对象 ModelIndustryScore 存在", "ModelIndustryScore" in c2)
check("L3 03数据表 ai_model_industry_scores 存在", "ai_model_industry_scores" in c3)
check("L3 08 API /industry-scores 存在", "/industry-scores" in c8)

# ========== Layer 4: Prompt Knowledge Base ==========
check("L4 01描述Prompt知识库 含字段", "问题" in c1 and "引用来源" in c1 and "出现频率" in c1)
check("L4 02领域对象 PromptKnowledgeBase 存在", "PromptKnowledgeBase" in c2)
check("L4 02 PromptKnowledgeBase 属性完整", "query_text" in c2 and "citations" in c2)
check("L4 03数据表 prompt_knowledge_base 存在", "prompt_knowledge_base" in c3)
check("L4 06前端 Prompt知识库 可浏览", "Prompt知识库" in c6 and "浏览" in c6)
check("L4 08 API /prompt-knowledge-base 存在", "/prompt-knowledge-base" in c8)

# ========== Layer 5: Brand Ranking ==========
check("L5 01描述品牌排名 含评分字段", "综合GEO评分" in c1 and "ChatGPT评分" in c1)
check("L5 02领域对象 AIBrandRanking 存在", "AIBrandRanking" in c2)
check("L5 02 AIBrandRanking 属性完整", "overall_score" in c2 and "rank_position" in c2)
check("L5 03数据表 ai_brand_rankings 存在", "ai_brand_rankings" in c3)
check("L5 06前端含AI品牌排名页面", "AI品牌排名" in c6 and "综合排名" in c6)
check("L5 08 API /brand-ranking 存在", "/brand-ranking" in c8)

# ========== Cross-document references ==========
check("01关联文档引用02", "02_领域模型设计.md" in c1)
check("04关联文档引用03", "03_数据架构.md" in c4)
check("06引用02", "02_领域模型设计.md" in c6)

# ========== Attribute consistency ==========
check("PromptKnowledgeBase citations是JSON", "JSON" in c2[c2.find("PromptKnowledgeBase"):c2.find("UserPersona")])
check("AIBrandRanking scores_by_model是JSON", "JSON" in c2[c2.find("AIBrandRanking"):])
check("UserPersona industry_focus是JSON", "JSON" in c2[c2.find("UserPersona"):c2.find("AIBrandRanking")])

print()
print("=" * 50)
print("架构一致性检查报告")
print("=" * 50)
print(f"通过: {passed}  失败: {failed}  总计: {passed + failed}")
print()
print("逐项明细:")
for c in checks:
    print(c)