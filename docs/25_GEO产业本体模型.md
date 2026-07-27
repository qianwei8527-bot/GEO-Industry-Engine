---
status: stable
authority: secondary
version: v1.0
last_review: 2026-07-26
related_docs: [02]
---
# GEO产业本体模型

> GEO世界的“元素周期表”——定义这个产业中到底存在什么、它们之间是什么关系。

---

## 一、为什么需要本体模型

现有系统的设计是从“功能”出发的（用户系统、企业系统、交易系统）。
本体模型是从“存在”出发的——先定义这个世界里有什么，再定义功能。

## 二、核心实体

### 2.1 GEO Enterprise（企业）
定义：在AI搜索生态中具有独立身份的组织实体。
关系：produces → Product | has → Capability | located_in → Region | employs → Person

### 2.2 GEO Product（产品/服务）
定义：可被AI识别和推荐的商业价值载体。
关系：belongs_to → Enterprise | cited_by → AIModel

### 2.3 GEO Capability（能力）
定义：企业或个人在特定领域的可验证专长。
关系：owned_by → Enterprise | owned_by → Person

### 2.4 GEO Person（个人）
定义：在GEO产业生态中的个体参与者。
关系：has → Capability | located_in → Region | seeks → Opportunity

### 2.5 GEO Region（区域）
定义：具有GEO产业特征的地理空间单元。
关系：contains → Enterprise | contains → Person

### 2.6 GEO AIModel（AI模型）
定义：生成AI推荐和搜索结果的智能系统。
关系：recommends → Enterprise | cites → Product



### 2.8 GEO Event（事件）
定义：产业中发生的重要动态。
类型：融资 | 招聘 | 产品发布 | 政策 | 合作 | 技术突破 | 市场变化
关系：impacts → Enterprise | impacts → Region

### 2.9 GEO Intent（意图）
定义：用户搜索背后的真实需求。
类型：Discovery | Comparison | Procurement | Solution | Verification
关系：drives → Search | matches → Opportunity
a（机会）
定义：需求和能力之间的可匹配价值空间。
关系：matches → Enterprise | targets → Person | exists_in → Region

---

## 三、实体关系图

Enterprise → produces → Product
Enterprise → has → Capability
Enterprise → located_in → Region
Enterprise → visible_in → AIModel
Enterprise → employs → Person

Person → has → Capability
Person → located_in → Region
Person → seeks → Opportunity

AIModel → recommends → Enterprise
AIModel → cites → Product

Opportunity → matches → Enterprise
Opportunity → targets → Person

---

## 四、与现有架构的关系

| 现有模块 | 对应本体 | 说明 |
|---------|---------|------|
| 02_领域模型设计.md | Enterprise, Product, Capability | 数据层实现 |
| 12_用户行为与AI决策路径.md | Person, AIModel | 决策层 |
| 13_产业发展趋势与职业生态.md | Person, Region | 生态层 |
| 14_实体智能与信息供应链.md | Enterprise, Product | 认知层 |
| 03_数据架构.md | 全部 | 存储层 |


### 关系强度计算

关系强度 = 频率 x 时间 x 影响范围 x 可信度 x 结果反馈


## 语义层（Semantic Layer）

AI缺不是数据，缺理解。你的系统需要告诉AI：某企业不是普通软件公司，它属于AI营销自动化领域，核心能力是企业知识库建设，服务对象是B2B制造企业，竞争位置是中高端，增长趋势是快速。语义层将这些信息结构化后供AI调用。
