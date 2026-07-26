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

### 2.7 GEO Opportunity（机会）
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
