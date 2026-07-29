---
status: stable
authority: secondary
version: v1.0
last_review: 2026-07-28
related_docs: [02_领域模型设计.md]
---

# GEO-Industry-Engine 产业本体模型

> 状态：架构设计 | 版本：v2.0 | 日期：2026-07-28
> 关联：02_领域模型设计.md、31_GEO产业上下文层.md

---

## 一、产业本体定义

GEO产业本体 (Ontology) 是对GEO产业世界的结构化描述框架，定义产业中有什么、它们之间是什么关系、以及如何理解这个产业。

它是产业知识图谱的Schema层。

---

## 二、核心本体类别

### 2.1 实体类 (Entity Types)

| 类 | 定义 | 关键属性 | 实例 |
|----|------|---------|------|
| Company | 企业 | industry, size, geo_score | 腾讯云 |
| Person | 个人 | profession, certification_level | 张三(GEO专家) |
| Organization | 机构 | org_type, jurisdiction | 某高新区管委会 |
| Service | 服务 | category, price_range | AI内容优化服务 |
| Product | 产品/工具 | category, tech_stack | AI写作工具 |
| Technology | 技术/能力 | maturity, category | 大模型微调技术 |

### 2.2 关系类 (Relationship Types)

| 关系 | 定义 | 方向 | 示例 |
|------|------|:--:|------|
| provides | 提供服务 | A->B | 服务商->企业 |
| uses | 使用技术/产品 | A->B | 企业->AI工具 |
| partners | 合作伙伴 | A<->B | 企业A<->企业B |
| competes | 竞争关系 | A<->B | 企业A<->企业B |
| invests | 投资关系 | A->B | VC->企业 |
| certified_by | 被认证 | A->B | 企业->认证机构 |
| employs | 雇佣 | A->B | 企业->个人 |
| belongs_to | 属于 | A->B | 企业->行业 |

### 2.3 事件类 (Event Types)

| 事件类 | 示例 |
|--------|------|
| ProductLaunch | 企业发布新产品 |
| FundingRound | 企业获得融资 |
| CertificationUpgrade | 认证等级提升 |
| PartnershipFormed | 建立合作关系 |
| MarketEntry | 进入新市场 |
| TalentMovement | 关键人才流动 |

### 2.4 证据类 (Evidence Types)

| 证据类 | 来源 | 可信度权重 |
|--------|------|:--------:|
| OfficialDocument | 政府/官方 | 1.0 |
| ThirdPartyReport | 第三方报告 | 0.8 |
| MediaCoverage | 媒体报道 | 0.6 |
| UserReview | 用户评价 | 0.5 |
| SelfReported | 自报 | 0.3 |

---

## 三、本体与系统的关系

- Entity + Relationship -> 产业知识图谱 -> 产业导航
- Event -> 时间轴 -> 趋势分析 + 风险预警
- Evidence -> Trust Score -> 认证体系
- 本体 Schema -> ORM Models -> PostgreSQL

---

## 四、本体演进

本体不是一成不变的。随着GEO产业发展，会新增实体类/关系类型/事件类。通过配置化扩展，不修改代码。

