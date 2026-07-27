---
status: stable
authority: primary
version: v2.0
last_review: 2026-07-27
related_docs: [12, 22, 31]
---
# GEO评分算法与模拟验证

> 定义从9个决策模型到最终GEO评分的完整计算链路，并用模拟数据进行验证。

---

## 一、GEO评分算法

### 1.1 九因子加权模型

```
GEO_Score = 
  EntityClarity (实体清晰度)       × 0.15
+ AITrustScore (AI信任评分)        × 0.15
+ AIContentReadiness (内容就绪度)  × 0.12
+ GEOSpaceScore (推荐空间)         × 0.12
+ CompetitionScore (竞争态势)       × 0.10
+ IndustryRelevance (行业相关度)    × 0.10
+ ModelPreference (模型偏好)       × 0.10
+ Timeliness (时效性)              × 0.08
+ Sentiment (情感倾向)             × 0.08
```

每个因子0-100分。总分0-100分。权重总和 = 1.00。

### 1.2 因子计算方式

| 因子 | 计算方式 | 数据来源 |
|------|---------|---------|
| EntityClarity | 身份/能力/市场/关系/信任五维完整度平均 | entity_profiles |
| AITrustScore | 权威35%+一致25%+时效20%+验证20%加权 | ai_trust_scores |
| AIContentReadiness | 结构35%+引用25%+权威20%+时效10%+验证10% | ai_content_readiness |
| GEOSpaceScore | (总席位-占位数)/总席位 x (1-变动频率) x 100 | geo_space_scores |
| CompetitionScore | (平均分-本企业分)/标准差 归一化 | competition_snapshots |
| IndustryRelevance | 企业与查询行业语义关联度 | 知识图谱 |
| ModelPreference | 模型对企业所在行业的推荐倾向 | intent_model_scores |
| Timeliness | 信息新鲜度(30天内=100, 1年=50, 3年=0) | ai_model_metrics |
| Sentiment | AI回答中对该企业的正面/负面/中性比例 | ai_query_results |

---

## 二、模拟数据验证

选取制造业和科技行业10家企业，展示全链路计算。

### 2.1 原始数据

| 企业 | 实体清晰度 | 信任评分 | 内容就绪度 | 空间评分 | 竞争分 | 行业相关 | 模型偏好 | 时效性 | 情感分 |
|------|-----------|---------|-----------|---------|-------|---------|---------|-------|-------|
| 华为 | 95 | 92 | 88 | 85 | 80 | 90 | 95 | 90 | 85 |
| 宁德时代 | 85 | 78 | 75 | 70 | 65 | 88 | 80 | 85 | 75 |
| 比亚迪 | 82 | 75 | 80 | 72 | 68 | 85 | 78 | 88 | 80 |
| 科大讯飞 | 78 | 80 | 85 | 75 | 70 | 85 | 82 | 85 | 82 |
| 新松机器人 | 60 | 55 | 62 | 58 | 72 | 80 | 70 | 65 | 62 |
| 埃斯顿 | 55 | 50 | 58 | 52 | 68 | 78 | 68 | 60 | 55 |
| 格力 | 45 | 48 | 40 | 42 | 55 | 45 | 40 | 50 | 50 |
| 某小型AI公司 | 30 | 25 | 35 | 28 | 45 | 55 | 50 | 35 | 40 |
| 某传统制造厂 | 18 | 15 | 12 | 10 | 30 | 10 | 15 | 8 | 20 |
| 某初创品牌 | 8 | 10 | 15 | 5 | 20 | 40 | 30 | 25 | 15 |

### 2.2 计算过程（以华为为例）

```
GEO_Score = 95x0.15 + 92x0.15 + 88x0.12 + 85x0.12
          + 80x0.10 + 90x0.10 + 95x0.10 + 90x0.08 + 85x0.08

= 14.25 + 13.80 + 10.56 + 10.20
+ 8.00 + 9.00 + 9.50 + 7.20 + 6.80

= 89.31（四舍五入 89）
```

### 2.3 全部企业计算结果

| 企业 | 加权计算 | GEO评分 | 等级 |
|------|---------|---------|------|
| 华为 | 95x0.15+92x0.15+88x0.12+85x0.12+80x0.10+90x0.10+95x0.10+90x0.08+85x0.08=89.3 | **89** | L5引领 |
| 宁德时代 | 85x0.15+78x0.15+75x0.12+70x0.12+65x0.10+88x0.10+80x0.10+85x0.08+75x0.08=78.3 | **78** | L4系统 |
| 比亚迪 | 82x0.15+75x0.15+80x0.12+72x0.12+68x0.10+85x0.10+78x0.10+88x0.08+80x0.08=78.0 | **78** | L4系统 |
| 科大讯飞 | 78x0.15+80x0.15+85x0.12+75x0.12+70x0.10+85x0.10+82x0.10+85x0.08+82x0.08=79.5 | **80** | L4系统 |
| 新松机器人 | 60x0.15+55x0.15+62x0.12+58x0.12+72x0.10+80x0.10+70x0.10+65x0.08+62x0.08=64.0 | **64** | L3主动 |
| 埃斯顿 | 55x0.15+50x0.15+58x0.12+52x0.12+68x0.10+78x0.10+68x0.10+60x0.08+55x0.08=59.6 | **60** | L3主动 |
| 格力 | 45x0.15+48x0.15+40x0.12+42x0.12+55x0.10+45x0.10+40x0.10+50x0.08+50x0.08=45.5 | **46** | L2被动 |
| 某小型AI公司 | 30x0.15+25x0.15+35x0.12+28x0.12+45x0.10+55x0.10+50x0.10+35x0.08+40x0.08=36.8 | **37** | L2被动 |
| 某传统制造厂 | 18x0.15+15x0.15+12x0.12+10x0.12+30x0.10+10x0.10+15x0.10+8x0.08+20x0.08=14.9 | **15** | L1未入局 |
| 某初创品牌 | 8x0.15+10x0.15+15x0.12+5x0.12+20x0.10+40x0.10+30x0.10+25x0.08+15x0.08=16.6 | **17** | L1未入局 |

### 2.4 评分等级分布

| 等级 | 范围 | 企业 | 策略 |
|------|------|------|------|
| L5 引领 | 85-100 | 华为 | 持续建设、保持行业标杆 |
| L4 系统 | 70-84 | 宁德时代、比亚迪、科大讯飞 | 系统性GEO管理 |
| L3 主动 | 50-69 | 新松、埃斯顿 | 主动优化内容+来源 |
| L2 被动 | 30-49 | 格力、某AI公司 | 基础内容建设 |
| L1 未入局 | 0-29 | 制造厂、初创品牌 | 从建立数字身份开始 |

---

## 三、模型间关系

### 3.1 九模型→GEO评分 映射关系

```
                                GEO评分
                                   ↑
                    ┌──────────────┼──────────────┐
                    │              │              │
          ┌─────────┴──┐   ┌──────┴──────┐   ┌───┴──────┐
          │  基础层     │   │  增强层      │   │  增长层   │
          │ EntityClarity│  │ AITrustScore │   │ SpaceScore│
          │ IndustryRel. │  │ ContentRead. │   │ Competit. │
          │ ModelPref.  │  │ Timeliness   │   │ Sentiment │
          └─────────────┘   │ Sentiment   │   └──────────┘
                             └─────────────┘
```

---



## 五、用户反馈校准

### 5.1 反馈机制

| 反馈类型 | 触发方式 | 处理方式 |
|---------|---------|---------|
| 评分感知偏差 | 用户点击"评分不准？"按钮 | 记录偏差，标记该企业评分待校准 |
| 排名感知偏差 | 用户提交自己的排名观察 | 交叉验证后更新排名 |
| 优化效果反馈 | 用户确认优化动作完成 | 启动重扫+对比分析 |

### 5.2 反馈数据应用

积累100条反馈后，启动权重校准：
1. 分析反馈中评分偏差的分布
2. 修正偏差较大的因子权重
3. 发布新版评分算法
## 四、关联文档

| 文档 | 关系 |
|------|------|
| 02_领域模型设计.md | 本算法使用的领域对象定义 |
| 03_数据架构.md | 本算法使用的数据表定义 |
| 12_GEO用户行为与AI决策路径模型.md | 9个决策模型的完整定义 |
| 17_产品定义与商业模式.md | 本算法支撑的产品定价 |

> 本文件中的权重为非对称规则权重（Phase 1）。数据积累到100家企业后使用ML调整。


---

## 多目标排名

| 实体类型 | 排名维度 |
|------------|-----------|
| 企业 | AI可见度排名 / 行业权威排名 / 能力排名 / 增长排名 / 信任排名 |
| 个人 | 技能排名 / 贡献排名 / 影响力排名 |
| 区域 | 产业密度 / 人才密度 / 创新指数 |
| 产品 | AI推荐率排名 / 认证等级排名 |

---

## 七、评分配置化

从 V1 起评分权重使用 YAML 配置化，不做硬编码。

### 配置目录结构

```
config/scoring/
  visibility.yaml    # AI可见度评分权重
  trust.yaml         # AI信任评分权重
  authority.yaml     # 行业权威评分权重
  growth.yaml        # 增长评分权重
```

### visibility.yaml 示例

```yaml
weights:
  completeness: 0.3
  authority: 0.3
  evidence: 0.2
  activity: 0.2
thresholds:
  high: 80
  medium: 50
  low: 20
```

### 设计原则

| 原则 | 说明 |
|------|------|
| 权重可配 | 各因子权重从 YAML 读取，不硬编码 |
| 阈值可调 | 评分等级阈值（高/中/低）可调 |
| 公式固定 | 评分计算逻辑（加权求和+归一化）写在代码中 |
| 行业差异 | 不同行业可加载不同配置文件 |

详见 [24_执行方案与90天计划.md](24_执行方案与90天计划.md) Sprint 3 评分配置化。

---

## Implementation Reference

> Content from 03_DECISION_ENGINE_IMPLEMENTATION.md, integrated for developer reference.

﻿# Decision Engine Implementation

## Architecture

Decision Engine sits above Context Engine, transforming contextual data into actionable business intelligence.

`
Context API (Sprint 2)
    |
    v
Decision Engine
    |
    +-- 9 Decision Models (3 layers)
    |       |-> Layer 1: Visibility, Industry Index, Trust Score
    |       |-> Layer 2: Capability Match, Opportunity, Competitive Position
    |       |-> Layer 3: Roadmap, Content Strategy, Market Connection
    |
    +-- Scoring Calculator (YAML-configured weights)
    |
    +-- Explanation Generator (score + reason + action)
    |
    +-- Recommendation Engine (rule-based)
    |
    v
Decision API / MCP Tools
`

## 9 Decision Models

### Layer 1: Cognitive (Understanding)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| GEO Visibility Score | CompanyContext | visibility_score (0-100) | AI search visibility |
| Industry GEO Index | IndustryContext | index_score (0-100) | Industry AI maturity |
| Entity Trust Score | Evidence list | trust_score (0-100) | AI trustworthiness |

### Layer 2: Judgment (Analysis)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| Capability Match | CapabilityContext | match_score (0-100) | Capability-market fit |
| Opportunity Score | CompanyContext | opportunity_score (0-100) | Growth potential |
| Competitive Position | CompanyContext | position_score (0-100) | Market position |

### Layer 3: Growth (Action)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| GEO Optimization Roadmap | CompanyContext | action_plan | Improvement steps |
| Content Strategy | CompanyContext | content_plan | Content recommendations |
| Market Connection | CompanyContext | connection_opps | Partnership opportunities |

## Scoring System

All weight configurations are in config/scoring/*.yaml:

| Config File | Models Using It | Factors |
|-------------|-----------------|---------|
| geo_visibility.yaml | GEOVisibilityScore | entity_quality, evidence, capability_match, relationship, recency |
| trust_score.yaml | (future) | evidence_quality, quantity, verification, longevity |
| industry_index.yaml | IndustryOpportunityScore | company_density, capability_depth, event_frequency, growth |
| opportunity.yaml | (future) | market_growth, competition_gap, capability_overlap, trend |

## Explanation System

Every score returns: score + level + reasons[] + actions[]

Score levels: excellent (80+), good (60-79), average (40-59), developing (<40)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/decision/company/{id} | Full decision report with 6 model scores + recommendations |
| GET | /api/v1/decision/industry/{id} | Industry analysis with index score |
| POST | /api/v1/decision/analyze | Natural language analysis query |

## MCP Tools

| Tool | Description | Source |
|------|-------------|--------|
| get_company_context | Full context | ContextTool (Sprint 2) |
| get_geo_score | GEO score + explanation | DecisionTool |
| get_recommendation | Actionable recommendations | DecisionTool |

## Key Design Decisions

1. **No hardcoded weights** - All weights loaded from YAML at runtime
2. **No black-box scores** - Every score has reasons[] and actions[] for explainability
3. **No LLM dependency** - All calculations are rule-based, no AI API calls
4. **Context Engine dependency** - Decision Engine never reads database directly

