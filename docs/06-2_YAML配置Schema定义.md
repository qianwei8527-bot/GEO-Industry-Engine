---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine YAML 配置 Schema 定义

> 状态：架构设计 | 版本：v1.0 | 日期：2026-07-28
> 关联：CTO长期开发协议.md（8.5 配置生命周期管理）
> 本文件是协议 C.2-3 设计任务的产出

---

## 一、Schema 约定

每个 YAML 文件必须包含 `schema_version` 字段用于版本管理。字段类型使用 JSON Schema 子集标注：`string` `integer` `float` `boolean` `array` `object` `null`。

配置目录结构遵循 8.5 节的 active/experiments/deprecated 三级管理。

---

## 二、Scoring（评分配置）— 6 文件

### 2.1 scoring/geo_visibility.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

weights:                          # 评分权重（总和=1.0）
  entity_quality: float           # 实体信息质量权重 [0.0-1.0] 默认: 0.25
  evidence_score: float           # 证据评分权重 默认: 0.25
  capability_match: float         # 能力匹配度权重 默认: 0.20
  relationship_density: float     # 关系密度权重 默认: 0.15
  recency: float                  # 数据时效性权重 默认: 0.15

thresholds:                       # 等级线
  high: integer                   # 高分线 [0-100] 默认: 80
  medium: integer                 # 中等线 默认: 60
  low: integer                    # 低分线 默认: 30
```

### 2.2 scoring/trust_score.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

weights:
  evidence_multiplier: float      # 证据加权系数 [1.0-3.0] 默认: 1.5
  certification_bonus: object     # 认证加分
    L0: integer                   # L0加分 默认: 0
    L1: integer                   # L1加分 默认: 10
    L2: integer                   # L2加分 默认: 25
    L3: integer                   # L3加分 默认: 40
    L4: integer                   # L4加分 默认: 60
  recency_decay_days: integer     # 数据衰减周期(天) 默认: 90
  min_evidence_for_score: integer # 最低证据数(未达标返回null) 默认: 1

source_credibility:               # 来源可信度权重
  official: float                 # 官方来源 默认: 1.0
  third_party: float              # 第三方 默认: 0.8
  self_reported: float            # 自报 默认: 0.4
  community: float                # 社区贡献 默认: 0.3
```

### 2.3 scoring/assessment.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

dimensions:                       # 评估维度
  - id: identity                  # 维度标识
    name: 身份完整度               # 显示名称
    weight: float                 # 权重 [0.0-1.0] 默认: 0.30
  - id: capability
    name: 能力深度
    weight: float                 # 默认: 0.25
  - id: relationship
    name: 生态连接度
    weight: float                 # 默认: 0.20
  - id: evidence
    name: 证据可信度
    weight: float                 # 默认: 0.15
  - id: growth
    name: 增长趋势
    weight: float                 # 默认: 0.10

entity_type_overrides:            # 不同实体类型的维度权重覆盖
  enterprise: {}                  # 使用默认
  individual:
    capability: 0.35              # 个人更看重能力
    evidence: 0.10
  provider:
    evidence: 0.25                # 服务商更看重证据
    relationship: 0.15
```

### 2.4 scoring/visibility.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

model:                            # AI可见度模型
  factors:
    - id: content_presence        # AI搜索结果中出现频率
      weight: float               # 默认: 0.30
      sources: [knowledge_graph, external_search]
    - id: authority_signals       # 权威信号(认证/引用/背书)
      weight: float               # 默认: 0.25
      sources: [certification, evidence]
    - id: freshness               # 内容新鲜度
      weight: float               # 默认: 0.20
      sources: [event, relationship]
    - id: structured_data         # 结构化数据完整度
      weight: float               # 默认: 0.15
      sources: [entity, capability]
    - id: industry_relevance      # 行业相关性
      weight: float               # 默认: 0.10
      sources: [industry, relationship]

thresholds:
  excellent: integer              # 默认: 85
  good: integer                   # 默认: 65
  average: integer                # 默认: 45
  below_average: integer          # 默认: 25
```

### 2.5 scoring/opportunity.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

opportunity_model:
  trend_weight: float             # 趋势影响权重 默认: 0.35
  gap_weight: float               # 产业空白权重 默认: 0.30
  competitor_weight: float        # 竞争强度权重(反向) 默认: 0.20
  match_weight: float             # 能力匹配权重 默认: 0.15

min_opportunity_score: integer    # 最低机会分(低于此值不展示) 默认: 40
max_opportunities: integer        # 最多展示机会数 默认: 5

risk_model:
  degradation_threshold: float    # 退化预警线(变化率) 默认: -0.10
  competitor_change_threshold: float  # 竞品变化预警线 默认: 0.15
  lookback_days: integer          # 回溯天数 默认: 90
  max_risks: integer              # 最多展示风险数 默认: 5
```

### 2.6 scoring/industry_index.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

index_dimensions:
  - id: total_entities            # 实体总数 权重: 0.15
  - id: avg_visibility            # 平均可见度 权重: 0.25
  - id: avg_trust                 # 平均可信度 权重: 0.20
  - id: growth_rate               # 增长率 权重: 0.25
  - id: certification_coverage    # 认证覆盖率 权重: 0.15

update_interval_hours: integer    # 更新间隔(小时) 默认: 24
enable_auto_update: boolean       # 是否自动更新 默认: true
```

---

## 三、Certification（认证配置）— 2 文件

### 3.1 certification/levels.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ⚠️ 部分 | 归属: active/

certification:
  levels:
    L0..L4:                       # 等级键名 L0-L4
      name: string                # 显示名称
      badge: string               # 徽章 emoji 或空
      badge_color: string         # 徽章颜色 hex
      requirements: array<string> # 通过条件列表
      unlocked_abilities: array<string>  # 解锁能力ID列表
        # 可选值: browse_map, basic_search, view_score, generate_report,
        #         comparison, appear_in_recommend, priority_listing,
        #         data_export, api_access, mcp_access, white_label,
        #         marketplace_post, custom_model, private_deploy,
        #         apply_cert_L1-L4
      ai_review: boolean          # 是否AI审核
      human_review: boolean       # 是否人工审核
      valid_years: integer|null   # 有效期(年) null=永久

  entity_types: array<string>     # 认证对象类型
    # 默认: [enterprise, individual, provider, institution, other]

  ai_review_rules:
    min_completeness: integer     # 最低完整度 默认: 60
    required_fields_by_type: object  # 各类型必填字段
      enterprise: array<string>
      individual: array<string>
      provider: array<string>
      institution: array<string>
    auto_reject_triggers: array<string>   # 自动驳回触发条件
    auto_flag_for_human: array<string>    # 人工复核触发条件
```

### 3.2 certification/review.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ⚠️ 部分 | 归属: active/

review:
  ai_review_timeout_minutes: integer  # AI审核超时(分) 默认: 5
  human_review_sla_hours: integer     # 人工审核SLA(时) 默认: 72
  max_retry_count: integer            # 驳回后最多重试次数 默认: 3
  cooldown_days: integer              # 拒绝后冷却期(天) 默认: 30

  evidence_requirements:              # 证据要求
    L1: integer                       # L1最低证据数 默认: 0
    L2: integer                       # L2最低证据数 默认: 1
    L3: integer                       # L3最低证据数 默认: 3
    L4: integer                       # L4最低证据数 默认: 10

  auto_renewal:                       # 自动续期
    enabled: boolean                  # 默认: true
    reminder_days_before: integer     # 到期前提醒天数 默认: 30
```

---

## 四、Pricing（定价配置）— 3 文件

### 4.1 pricing/plans.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

plans:
  <plan_id>:                         # free/growth/pro/business/enterprise
    name: string                     # 显示名称
    price_monthly: integer|null      # 月价(元) null=联系销售
    price_yearly: integer|null       # 年价(元)
    description: string              # 简述
    target: string                   # 目标用户
    trial_days: integer|null         # 试用天数
    contact_sales: boolean           # 是否联系销售(替代定价) 默认: false
    quota: object                    # 配额
      reports_per_month: integer|null
      comparisons: integer|null
      api_calls_per_month: integer|null
      sub_accounts: integer|null
      data_export_rows: integer|null
    permissions: array<string>       # 权限ID列表
    features: array<string>          # 功能卖点(展示用)
    limitations: array<string>       # 限制说明(展示用)

  payment:                           # 支付配置
    providers: array<string>         # 支付提供商 [stripe, lemon_squeezy, alipay, wechat_pay]
    default_currency: string         # 默认货币 默认: CNY
    trial_days_default: integer      # 默认试用天数
    auto_renew_default: boolean      # 默认是否自动续费
```

### 4.2 pricing/permissions.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

permissions:
  - id: string                      # 权限ID
    name: string                    # 显示名称
    category: string                # 分类: data/products/platform/certification
    description: string             # 描述
    default_roles: array<string>    # 默认拥有该权限的角色
```

### 4.3 pricing/payment.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/ (远期)

payment:
  methods: array<string>            # [wechat, alipay, card, bank_transfer]
  currency: string                  # 默认: CNY
  tax_rate: float                   # 税率 默认: 0.06
  invoice: object
    enabled: boolean                # 是否支持开票 默认: true
    types: array<string>            # [vat, general]
  refund:
    window_days: integer            # 退款窗口(天) 默认: 7
    max_refund_rate: float          # 最高退款比例 默认: 1.0
```

---

## 五、Marketplace（交易市场配置）— 1 文件

### 5.1 marketplace/categories.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ⚠️ 部分 | 归属: experiments/

categories:
  - id: string                     # 分类ID
    name: string                   # 显示名称
    description: string
    subcategories: array<object>
      - id: string
        name: string
    service_types: array<string>   # 该分类下的服务类型
      # 可选: 内容优化/策略咨询/技术实施/数据分析/培训/认证辅导/其他

matching:                          # 匹配权重
  certification_weight: float      # 认证等级权重 默认: 0.30
  capability_weight: float         # 能力匹配权重 默认: 0.35
  review_weight: float             # 评价权重 默认: 0.20
  geo_score_weight: float          # GEO分权重 默认: 0.15
```

---

## 六、Competitive（竞争情报配置）— 1 文件

### 6.1 competitive/intelligence.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ❌ | 归属: experiments/

intelligence:
  competitive:                     # 竞争情报
    comparison_dimensions: array<string>  # 对比维度
      # [geo_score, visibility, trust, capability, growth, content]
    alert_threshold: float         # 竞品变化预警线 默认: 0.10
    lookback_days: integer         # 默认: 30
    max_competitors: integer       # 默认: 10

  opportunity:                     # 机会情报
    emerging_threshold: float      # 新兴赛道增长率阈值 默认: 0.20
    gap_detection: boolean         # 是否启用缺口检测 默认: true
    trend_sources: array<string>   # 趋势数据源 [internal_event, external_news, industry_data]

  risk:                            # 风险情报
    severity_levels: object
      critical: integer            # 阈值 默认: 80
      high: integer                # 默认: 60
      medium: integer              # 默认: 40
      low: integer                 # 默认: 20
    auto_monitor: boolean          # 自动监控 默认: true
    alert_channels: array<string>  # 告警渠道 [system_notification, email]
```

---

## 七、Analytics（分析配置）— 1 文件

### 7.1 analytics/events.yaml

```yaml
schema_version: "1.0"
# 已接入代码: ✅ | 归属: active/

events:
  - name: string                   # 事件名称如 user.registered
    category: string               # 分类: user/entity/certification/marketplace
    description: string
    fields: array<object>          # 事件携带字段
      - name: string               # 字段名
        type: string               # string/integer/float/boolean
        required: boolean
    retention_days: integer        # 数据保留天数 默认: 365

export:                            # 导出配置
  max_rows_per_export: integer     # 单次导出最大行数 默认: 50000
  formats: array<string>           # [csv, json, parquet]
```

---

## 八、Schema 版本管理约定

每个 YAML 文件的 `schema_version` 字段在以下情况递增：
- **major**: 删除或重命名字段
- **minor**: 新增可选字段
- **patch**: 修改默认值或描述

代码读取 YAML 时校验 `schema_version`，不匹配时警告但允许继续（向后兼容原则）。

当前所有文件均为 `schema_version: "1.0"`，定稿后统一移入 `config/active/` 目录。

---

## 九、设计覆盖度统计

| 目录 | 文件数 | Schema 已定义 | 已接入代码 |
|------|:-----:|:----------:|:--------:|
| scoring/ | 6 | ✅ 6/6 | ❌ 0/6 |
| certification/ | 2 | ✅ 2/2 | ⚠️ 2/2(部分) |
| pricing/ | 3 | ✅ 3/3 | ❌ 0/3 |
| marketplace/ | 1 | ✅ 1/1 | ⚠️ 1/1(部分) |
| competitive/ | 1 | ✅ 1/1 | ❌ 0/1 |
| analytics/ | 1 | ✅ 1/1 | ✅ 1/1 |
| **合计** | **14** | **14/14** | **3/14** |
