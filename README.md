# GEO-Industry-Engine

**AI时代企业增长基础设施 + GEO产业导航与交易平台**

GEO产业引擎是一个集企业增长基础设施、GEO产业导航与交易于一体的综合平台。它是AI搜索时代的增长入口，也是每个个体发现产业位置、学习成长、连接参与的生态平台。

## 定位

> Semrush（数据分析） + Gartner（行业地图） + Salesforce（客户增长） + Marketplace（交易市场） + AI Agent OS（智能团队）

## 五大核心系统

| 系统 | 描述 |
|------|------|
| **AI可见度增长系统** | 企业/个人AI检测、GEO评分、AI曝光分析、内容优化、增长建议 |
| **GEO产业导航系统** | 五大地图：产业生态地图、商业赚钱地图、运营流程地图、地域生态地图、发展方向地图 |
| **GEO交易市场** | 开放交易平台（服务/工具/数据/知识/人才），支持企业+个人 |
| **认证背书体系** | 企业认证、个人认证、产品认证，四级认证等级 |
| **GEO数据资产中心** | 行业/企业/个人数据库、GEO指数、知识图谱、AI回答数据库 |

## 技术栈

| 层 | 技术选型 |
|----|---------|
| 前端 | Next.js |
| 后端 | FastAPI |
| 关系数据库 | PostgreSQL |
| 知识图谱 | Neo4j |
| 向量数据库 | Milvus / Chroma |
| 搜索引擎 | ElasticSearch |
| Agent框架 | LangGraph / AutoGen / CrewAI |
| 决策智能 | GEOSpaceScore / AITrustScore / AIContentReadiness / GEOAttribution |

## 项目结构

`
GEO-Industry-Engine/
├── README.md
├── .codex/              # AI CTO 开发规则
│   ├── AGENTS.md
│   └── REFERENCES.md
├── docs/               # 项目文档体系
│   ├── 00_项目宪章.md            # 战略
│   ├── 01_产品架构PRD.md          # 产品
│   ├── 02_领域模型设计.md         # 领域（共享契约）
│   ├── 03_数据架构.md             # 数据
│   ├── 04_Agent_OS设计.md         # Agent
│   ├── 05_技术架构.md             # 技术
│   ├── 06_前端设计.md             # 前端
│   ├── 07_后端设计.md             # 后端
│   ├── 08_API接口规范.md          # API
│   ├── 09_产业导航交互设计.md      # 交互
│   ├── 10_数据更新与认证机制.md    # 数据机制
│   └── 11_MVP范围.md              # 规划
├── frontend/           # Next.js 前端
├── backend/            # FastAPI 后端
├── agents/             # AI Agent 运行时
├── database/           # 数据库迁移与模型
├── infrastructure/     # 部署与基础设施
├── tests/              # 测试套件
└── scripts/            # 工具脚本
`

## 开发原则

1. 先设计文档，再写代码
2. 所有模块必须服务商业闭环
3. 所有数据必须可沉淀
4. 所有功能必须考虑未来Agent调用
5. 所有架构必须支持扩展

---

*让每一家企业在AI搜索时代被看见、被理解、被选择。*
*让每一个个体在GEO产业中找到自己的位置、发现价值、参与成长。*
