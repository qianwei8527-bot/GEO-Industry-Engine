import os
p11 = os.path.join("D:\\GEO-IE\\docs\\11_MVP范围.md")
c = open(p11, "r", encoding="utf-8").read()

new_items = """

### P0-9 AI模型智能库（新增）
- [ ] 模型注册表（ai_models）：注册全部已知AI模型及其基本信息
- [ ] 模型指标采集（ai_model_metrics）：用户量估算、市场份额、引用频率
- [ ] 模型-行业热度矩阵（ai_model_industry_scores）：行业X模型的热度评分
- [ ] 模型行为模式库（ai_model_behavior_patterns）：来源偏好、回答风格、语言偏向
- [ ] 模型来源偏好（ai_model_sources）：各模型对不同来源的引用权重
- [ ] 查询结果样本库（ai_query_results）：批量查询+结果解析+实体提取
- [ ] Scanner Agent 升级：模型感知扫描策略
- [ ] Content Agent 升级：模型偏好内容生成
- [ ] GEO评分引擎升级：模型权重纳入评分算法
- [ ] 新模型自动发现管道"""

c += new_items
open(p11, "w", encoding="utf-8").write(c)
print("11 done")