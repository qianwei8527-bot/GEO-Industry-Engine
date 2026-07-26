# GEO实体智能与信息供应链模型

> AI眼中的企业长什么样？AI从哪里获取关于企业的信息？

---

## 一、为什么需要实体智能？

### 1.1 AI推荐的前提

AI推荐一个企业，前提是AI**知道**这个企业。

但"知道"不是简单的二值判断——AI对企业的认知有深度：从"听说过这个名字"到"了解产品、能力、行业地位、客户评价"。

当前系统存储的是企业的基础数据（名称、行业、规模等）。但缺少的是**AI视角的企业画像**——AI知道这个企业的哪些信息、信息完整度多高、信息来自哪里、信息是否一致。

### 1.2 实体智能的定义

GEO实体智能 = AI对一个企业认知的完整度和质量。

由五个维度组成：

| 维度 | 说明 | 影响GEO评分权重 |
|------|------|----------------|
| 身份清晰度 | AI是否知道企业是谁 | 25% |
| 能力清晰度 | AI是否知道企业能做什么 | 25% |
| 关系清晰度 | AI是否知道企业和谁合作/竞争 | 15% |
| 证据强度 | AI是否有足够的证据支撑对企业的描述 | 20% |
| 信息一致性 | 来自不同来源的信息是否一致 | 15% |

---

## 二、企业实体画像模型

### 2.1 AI视角的企业画像

```
AI认知中的企业 = {
  身份: {名称, 行业, 成立时间, 总部, 规模}
  能力: {产品线, 核心技术, 服务类型, 解决方案}
  市场: {主要客户, 市场份额, 覆盖区域}
  关系: {合作伙伴, 供应商, 客户, 竞争对手}
  信任: {认证, 资质, 客户评价, 媒体报道}
}
```

每个维度的完整度决定AI在多大程度上"认识"这个企业。

### 2.2 实体完整度评分

```
EntityCompleteness =
  身份完整度(0-1) x 0.20
+ 能力完整度(0-1) x 0.25
+ 市场完整度(0-1) x 0.20
+ 关系完整度(0-1) x 0.15
+ 信任完整度(0-1) x 0.20
```

评分区间0-100。低于40分意味着AI对企业认知非常有限，很难被推荐。

---

## 三、信息供应链模型

### 3.1 AI的信息来源

AI对企业信息的了解来自多种信源：

| 来源类型 | 权威等级 | AI引用概率 | 典型模型偏好 |
|---------|---------|-----------|------------|
| 官方网站 | 高 | 极高 | ChatGPT/Gemini |
| 百科(Wikipedia/Baidu) | 高 | 极高 | ChatGPT/Perplexity |
| 权威新闻 | 高 | 高 | Gemini/ChatGPT |
| 行业报告 | 高 | 高 | Claude/ChatGPT |
| 学术论文 | 高 | 中 | Claude |
| 用户评价 | 中 | 中 | Gemini/Perplexity |
| 社交媒体 | 低 | 低 | Grok |
| 论坛/社区 | 低 | 低 | Perplexity |

### 3.2 信息供应链追踪

``` 
企业创建数字信息(官网/百科/新闻/报告)
    ↓
AI模型爬取/训练/索引
    ↓
AI在回答中引用
    ↓
用户通过AI了解企业
    ↓
企业获得可见度
```

不同模型的信息供应链不同：
- ChatGPT：训练数据+联网搜索（Bing）
- Gemini：Google索引+Knowledge Graph
- Perplexity：实时搜索+引用评分
- DeepSeek：中文语料+联网搜索

### 3.3 来源权威性评估

每条来源需要评估：

| 维度 | 评估方式 |
|------|---------|
| 源可信度 | 域名权威性、编辑质量 |
| 时效性 | 发布时间、最后更新 |
| 相关性 | 信息与企业的关联强度 |
| 独立性 | 是否为独立第三方来源 |
| 引用频率 | 被其他来源引用的次数 |

---

## 四、行业知识图谱

### 4.1 从分类树到关系网络

现有的9层产业地图是分类树。但AI理解行业的方式是关系网络：

```
[新能源汽车行业]
    ├── 关系类型: 包含
    │   ├── 整车制造
    │   ├── 电池制造
    │   └── 充电设施
    ├── 关系类型: 供应链
    │   ├── 原材料 → 电池 → 整车
    │   └── 芯片 → 系统 → 整车
    ├── 关系类型: 竞争
    │   ├── 企业A ↔ 企业B
    │   └── 技术路线A ↔ 技术路线B
    └── 关系类型: 合作关系
        ├── 车企 ↔ 电池厂
        └── 整车厂 ↔ 经销商
```

### 4.2 节点类型

| 节点类型 | 示例 | 属性 |
|---------|------|------|
| Industry | 新能源汽车 | 名称、描述、规模 |
| Sector | 电池制造 | 名称、技术路线 |
| Enterprise | 宁德时代 | 实体画像的所有维度 |
| Product | 麒麟电池 | 名称、性能参数 |
| Technology | 固态电池 | 成熟度、玩家 |
| Geography | 长三角 | 企业集群 |

### 4.3 关系类型

| 关系类型 | 示例 | 说明 |
|---------|------|------|
| contains | 行业包含子行业 | 层级关系 |
| supply_chain | A供应B | 供应链上下游 |
| competes_with | A竞争B | 竞争关系 |
| cooperates_with | A合作B | 合作伙伴 |
| located_in | A位于B地区 | 地域关系 |
| invests_in | A投资B | 投资关系 |
| customer_of | A是B的客户 | 客户关系 |

---

## 五、领域对象设计

### 5.1 EntityProfile（企业实体画像）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| company_id | UUID | FK -> Company |
| identity_completeness | Decimal | 身份完整度(0-1) |
| capability_completeness | Decimal | 能力完整度(0-1) |
| market_completeness | Decimal | 市场完整度(0-1) |
| relationship_completeness | Decimal | 关系完整度(0-1) |
| trust_completeness | Decimal | 信任完整度(0-1) |
| overall_completeness | Decimal | 综合实体完整度(0-100) |

### 5.2 EntityCapability（企业能力）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| entity_id | UUID | FK -> EntityProfile |
| capability_name | String | 能力名称 |
| category | Enum | product/technology/service/solution |
| description | Text | 能力描述 |
| evidence_count | Int | 支撑证据数 |

### 5.3 InformationSource（信息来源）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| source_name | String | 来源名称 |
| source_type | Enum | official/encyclopedia/news/academic/review/social |
| authority_level | Int | 权威等级(1-5) |
| ai_citation_probability | Decimal | AI引用概率(0-1) |
| model_preferences | JSON | 偏好此来源的模型列表 |

### 5.4 EntitySourceLink（实体-来源关联）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| entity_id | UUID | FK -> EntityProfile |
| source_id | UUID | FK -> InformationSource |
| url | String | 具体来源URL |
| mention_context | Text | 提及企业的上下文 |
| first_detected | DateTime | 首次发现时间 |
| last_detected | DateTime | 最近发现时间 |

### 5.5 KnowledgeGraphNode（知识图谱节点）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| node_type | Enum | industry/sector/enterprise/product/technology/geography |
| name | String | 节点名称 |
| properties | JSON | 节点属性 |

### 5.6 KnowledgeGraphEdge（知识图谱边）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| source_node_id | UUID | FK -> KnowledgeGraphNode |
| target_node_id | UUID | FK -> KnowledgeGraphNode |
| relationship_type | Enum | contains/supply_chain/competes/cooperates/located_in/invests_in/customer_of |
| weight | Decimal | 关系强度 |
