---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine Decision Engine 详细设计

> 状态：架构设计 | 版本：v2.0 | 日期：2026-07-28
> 关联：02_领域模型设计.md、16_GEO评分算法与模拟验证.md、config/scoring/*.yaml
> 总控：CTO长期开发协议.md §Decision Engine

---

## 一、Decision Engine 定位

Decision Engine 是整个 GEO-Industry-Engine 的智能决策中枢。它不是检测中心专属的计算模块，而是为五大产品系统提供评分、评估、预测、机会发现、风险识别、排名、匹配、推荐、路线规划、解释等通用决策能力的共享基础设施。

核心约束：Decision Engine 不直接拥有业务逻辑。它的输入来自 Entity/Context/Evidence，输出为 Recommendation/Action/Roadmap。所有计算必须可解释。

---

## 二、计算架构

`
输入层 (Context Engine提供)
  ├── EntityContext (身份/能力/关系/证据/信任)
  ├── IndustryContext (行业规模/成熟度/趋势)
  ├── EventStream (事件时间序列)
  └── ComparativeContext (竞品/对标数据)
            ↓
评分配置层 (YAML Config)
  ├── scoring/assessment.yaml (四层评估)
  ├── scoring/geo_visibility.yaml (AI可见度)
  ├── scoring/visibility.yaml (传统可见度)
  ├── scoring/trust_score.yaml (可信度)
  ├── scoring/industry_index.yaml (产业指数)
  └── scoring/opportunity.yaml (机会评分)
            ↓
计算引擎层 (Decision Engine Core)
  ├── Scoring Engine (评分计算)
  │   ├── WeightedSumCalculator (加权求和)
  │   ├── Normalizer (归一化: MinMax/Z-Score)
  │   ├── ThresholdClassifier (阈值分级)
  │   └── IndustryAdjuster (行业系数调整)
  ├── Ranking Engine (排名计算)
  │   ├── PercentileCalculator (百分位)
  │   ├── SegmentClassifier (分层)
  │   └── TrendingRanker (趋势排名)
  ├── Prediction Engine (预测计算)
  │   ├── TrendProjector (趋势外推)
  │   ├── AnomalyDetector (异常检测)
  │   └── ScenarioSimulator (情景模拟)
  ├── Matching Engine (匹配计算)
  │   ├── CapabilityMatcher (能力匹配)
  │   ├── DemandSupplyMatcher (供需匹配)
  │   └── OpportunityScout (机会发现)
  ├── Risk Engine (风险计算)
  │   ├── MomentumTracker (动量追踪)
  │   ├── VulnerabilityScanner (弱点扫描)
  │   └── AlertGenerator (预警生成)
  └── Explanation Engine (可解释性)
      ├── ReasonGenerator (原因生成)
      ├── FactorAttribution (因子归因)
      └── EvidenceTracer (证据溯源)
            ↓
输出层 (API/Agent消费)
  ├── Assessment Report → 检测中心
  ├── Trust Score → 认证中心
  ├── Industry Index → 产业导航
  ├── Data Quality → 数据资产中心
  ├── Match Score → 交易市场
  └── Intelligence → 产业情报
`

---

## 三、评分模型详解

### 3.1 GEO Score (综合GEO得分)

`
GEO_Score = 
  visibility_score × W_v +
  trust_score × W_t +
  capability_score × W_c +
  industry_position × W_i +
  growth_score × W_g

其中所有权重来源: config/scoring/assessment.yaml
行业系数调整: assessment.yaml#industry_adjustments
`

计算公式实现路径: ackend/app/decision/scoring/calculator.py::GeoScoreCalculator

| 输入 | 来源 | 类型 | 说明 |
|------|------|------|------|
| visibility_score | geo_visibility.yaml 计算 | float 0-100 | AI可见度 |
| trust_score | trust_score.yaml 计算 | float 0-100 | 可信度 |
| capability_score | capability_match 模型 | float 0-100 | 能力匹配度 |
| industry_position | industry_index.yaml 计算 | float 0-100 | 行业位置 |
| growth_score | opportunity.yaml 计算 | float 0-100 | 成长性 |

输出格式 (API 响应):
`json
{
  "geo_score": 72.5,
  "level": "B+",
  "percentile": 18,
  "dimensions": {
    "visibility": { "score": 65, "weight": 0.25, "reason": "..." },
    "trust": { "score": 72, "weight": 0.20, "reason": "..." },
    "capability": { "score": 80, "weight": 0.20, "reason": "..." },
    "industry_position": { "score": 68, "weight": 0.20, "reason": "..." },
    "growth": { "score": 78, "weight": 0.15, "reason": "..." }
  },
  "improvement_actions": [
    { "dimension": "visibility", "action": "增加技术文档输出", "impact": "+12" },
    { "dimension": "trust", "action": "申请L2认证", "impact": "+8" }
  ]
}
`

### 3.2 产业战略评估 (四层报告)

四层评估对应 config/scoring/assessment.yaml 的四个 section：

**第一层: 身份与位置**
- 输入: EntityContext (实体完整度 + 能力 + 可见度 + 信任 + 排名)
- 输出: GEO数字身份卡 + 行业排名 + 等级标签
- 模型: ackend/app/decision/models/assessment/ecosystem_position.py

**第二层: 机会发现**
- 输入: IndustryContext + Opportunity Scoring
- 输出: 机会列表 (评级A-D) + 推荐动作
- 模型: ackend/app/decision/models/assessment/opportunity_index.py
- 时间窗口: 3/6/12个月

**第三层: 风险预警**
- 输入: EventStream分析 + CompetitorTracking
- 输出: 风险列表 (红/橙/黄/绿) + 响应建议
- 模型: ackend/app/decision/models/assessment/risk_warning.py
- 追踪窗口: 90天

**第四层: 行动路线**
- 输入: 前三层综合 + Gap分析
- 输出: 分阶段路线图 (30天/90天/180天/365天)
- 模型: ackend/app/decision/models/assessment/roadmap.py

### 3.3 预测模型

**趋势外推 (TrendProjector)**
`
预测值 = 当前值 + 变化率 × 时间 + 季节性修正
变化率 = (最近N期值 - 前N期值) / N / 前N期值
置信区间 = 预测值 ± 1.96 × 标准差
`

**异常检测 (AnomalyDetector)**
`
Z-Score = (当前值 - 均值) / 标准差
|Z| > 2.0 → 黄色预警
|Z| > 3.0 → 红色预警
`

**情景模拟 (ScenarioSimulator)**
支持三种预设情景: 乐观/基准/悲观，用户可调整参数。

---

## 四、决策反馈闭环

`
Decision Engine 输出 Recommendation
           ↓
用户执行 (或不执行) Action
           ↓
系统追踪 Action Result (通过Event/Evidence变化)
           ↓
Evaluation: 实际变化 vs 预测变化
           ↓
Model Update: 调整权重/修正预测参数
`

闭环数据记录:
- decision_feedback 表: 记录每次推荐的用户响应和结果
- 权重调优周期: 季度 (避免过拟合)
- 最小反馈样本: 100

---

## 五、可解释性保证

每条评分输出必须包含:
1. **score** (得分: 0-100)
2. **reason** (原因: 自然语言解释)
3. **improvement_action** (改进建议: 具体可执行的动作)
4. **evidence_sources** (证据来源: 引用Entity/Evidence ID)
5. **confidence** (置信度: 0-1)

示例:
`json
{
  "score": 58,
  "reason": "AI可见度偏低，主要因为技术文档类内容少(仅3篇)，且未建立与行业权威机构的关系。",
  "improvement_action": "建议未来30天发布5-8篇技术博客，并与至少2家行业媒体建立引用关系。",
  "evidence_sources": ["EV-042", "EV-128", "REL-015"],
  "confidence": 0.82
}
`

---

## 六、实现状态

| 组件 | 代码位置 | 状态 | 备注 |
|------|---------|------|------|
| Decision Engine Core | backend/app/decision/engine.py | 骨架就绪 | 评分调度逻辑完成 |
| Scoring Calculator | backend/app/decision/scoring/calculator.py | 骨架就绪 | 待接入YAML |
| Weight Loader | backend/app/decision/scoring/weights.py | 骨架就绪 | 待接入YAML |
| 6个评分YAML | config/scoring/*.yaml | ✅ 设计完成 | v1.0完整定义 |
| YAML→Engine接入 | — | 🔴 P0待编码 | C.3-1 |
| Assessment Models (6) | backend/app/decision/models/assessment/ | 骨架就绪 | 数据结构+接口定义 |
| Company Growth | backend/app/decision/models/company_growth.py | 骨架就绪 | 4.2KB含完整模型 |
| GEO Visibility | backend/app/decision/models/geo_visibility.py | 骨架就绪 | 1.6KB |
| Industry Benchmark | backend/app/decision/models/industry_benchmark.py | 骨架就绪 | 2KB |
| Reason Generator | backend/app/decision/explanation/reason_generator.py | 骨架就绪 | 1.7KB含模板 |
| Recommendation | backend/app/decision/recommendation/recommendation_engine.py | 骨架就绪 | 2KB |
| Decision API | backend/app/api/v1/decision.py | 骨架就绪 | 端点定义完成 |

### 编码阶段P0任务 (C.3-1)

将6个YAML接入Decision Engine的实际计算代码:
1. WeightLoader 改为从YAML读取而非硬编码
2. ScoringCalculator 对接6个YAML的完整维度
3. 单元测试验证: 给定输入 → 输出可复现
4. API端到端测试: POST /decision/geo-score → 返回完整四层报告

---

## 七、关键质量门禁

- [ ] 所有评分能从YAML配置驱动（不能有硬编码）
- [ ] 每个评分输出包含reason + improvement_action
- [ ] 评分计算结果可复现（相同输入→相同输出）
- [ ] 行业系数调整测试覆盖≥3个行业
- [ ] 单元测试覆盖率≥80% (decision/模块)
- [ ] API集成测试：四层报告完整链路
