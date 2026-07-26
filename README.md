# GEO-Industry-Engine

**AI时代企业智能可见度基础设施与GEO产业生态平台**

> 构建企业在AI世界中的定位、认知、信任、推荐和交易基础设施。

---

## 为什么需要GEO？

用户获取信息的入口正从搜索引擎转向AI：

```
传统路径：用户需求 -> Google搜索 -> 网站 -> 比较 -> 购买
AI时代：  用户需求 -> 询问AI -> AI推荐 -> 用户决策
```

企业面临一个新问题：**如何被AI发现、理解、信任和推荐？**
GEO（Generative Engine Optimization）就是解决这个问题的。

---

## 项目定位

> Semrush（数据分析） + Gartner（行业地图） + Salesforce（客户增长） + Marketplace（交易市场） + AI Agent OS（智能团队）

以智能认知为底座，以产业地图为入口，以交易市场完成商业闭环。

---

## GEO产业生态飞轮

```
企业进入平台 -> 建立AI实体资产 -> 获得AI可见度评分
    -> 进入产业地图 -> 获得曝光和商机
    -> 进入交易市场 -> 产生服务和人才需求
    -> 数据反馈优化智能模型 -> 更多企业进入
```

---

## 整体架构

```
                   商业生态层

AI可见度增长系统 | GEO产业导航系统 | GEO交易市场 | 认证体系
   企业增长         产业发现         商业连接      信用

                       ↓

                 智能认知中心（底座）

AI模型智能库 | 用户决策模型 | 产业认知库 | 实体智能图谱 | 竞争与增长智能

                       ↓

                   GEO Agent OS
```

---

## 四大业务系统

### 1. AI可见度增长系统

企业AI搜索可见性分析与优化。含AI品牌扫描、GEO评分、竞争分析、内容优化、内容就绪度预测、增长实验、效果归因。

### 2. GEO产业导航系统

构建GEO产业地图，让企业、人才、机构找到自己的位置。含产业生态地图(9层MECE)、商业赚钱地图、人才地图(L1-L4技能)、区域地图。

### 3. GEO交易市场

连接需求方、服务方、人才和工具。含企业需求、服务市场、人才交易、数据与工具交易。

### 4. GEO认证体系

不只是给人看，更是给AI看的信任背书。企业/个人/产品四级认证(L1-L4)。

---

## 智能认知中心（底座）

支撑所有业务系统的智能决策层。五大认知资产：

| 认知资产 | 解决的问题 |
|----------|-----------|
| AI模型智能库 | 不同AI如何理解和推荐？ |
| 用户行为与AI决策模型 | 用户为什么问AI？AI为什么推荐这个企业？ |
| GEO产业认知库 | 产业如何发展？谁参与？谁赚钱？ |
| GEO实体智能图谱 | 企业、产品、行业之间的知识网络关系 |
| GEO竞争与增长智能 | 如何与对手比较？如何持续优化和归因？ |

九个决策模型分层：认知(Entity/Industry/Model) -> 判断(Trust/Readiness/Competition) -> 增长(Space/Experiment/Attribution/Opportunity)

---

## 技术栈

| 层 | 选型 |
|----|------|
| 前端 | Next.js |
| 后端 | FastAPI |
| 数据库 | PostgreSQL / Neo4j / Chroma / ES |
| Agent | LangGraph / CrewAI |
| 决策智能 | GEOSpaceScore / AITrustScore / AIContentReadiness / GEOAttribution |

## 项目结构

```
GEO-Industry-Engine/
├── .codex/         # AI CTO开发规则
├── docs/           # 21份架构文档
├── backend/        # FastAPI后端
├── frontend/       # Next.js前端
├── agents/         # Agent OS
├── database/       # 数据库迁移
├── infrastructure/ # Docker部署
└── scripts/        # 工具脚本
```

## 开发原则

1. 架构优先 > 功能优先
2. 数据资产优先 > 页面展示
3. 长期扩展 > 临时代码
4. 所有模块服务商业闭环
5. 所有数据必须可沉淀
6. 所有功能考虑Agent调用

---

*让每一家企业在AI搜索时代被看见、被理解、被推荐。*
