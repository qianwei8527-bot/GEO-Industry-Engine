# Doc-Code 映射表

> 本文档记录 34 份设计文档与源码模块的对应关系。
> 开发时以本文档为准，新增代码模块时必须更新此表。

---

## 核心映射

| 文档 | 对应代码 | 状态 |
|------|---------|------|
| 00_项目宪章.md | — | 架构指引，无直接代码 |
| 01_产品架构PRD.md | — | 产品需求，无直接代码 |
| 02_领域模型设计.md | backend/app/models/ | 数据模型标准 |
| 03_数据架构.md | backend/app/database.py | 数据架构标准 |
| 04_Agent_OS设计.md | agents/ | Agent 框架标准 |
| 05_技术架构.md | — | 技术选型标准 |
| 06_前端设计.md | frontend/src/ | 前端实现标准 |
| 07_后端设计.md | backend/app/ | 后端架构标准 |
| 08_API接口规范.md | backend/app/api/v1/ | API 实现标准 |
| 09_产业导航交互设计.md | frontend/src/ | 前端导航 |
| 10_数据更新与认证机制.md | backend/app/ | 后台数据更新 |
| 11_MVP范围.md | — | 路线图文档 |
| 12-16_决策模型.md | backend/app/models/ | 评分/决策逻辑 |
| 17_商业模式.md | — | 无直接代码 |
| 18_工程实践.md | — | 运维标准 |
| 19_用户体验.md | frontend/src/ | 前端 UX |
| 20_数据生产机制.md | backend/app/ | 数据采集 |
| 21_应用场景.md | — | 产品场景 |
| 22_测量方法论.md | backend/app/ | 测量/验证逻辑 |
| 23_合规.md | backend/app/ | 合规检查 |
| 24_执行方案.md | — | 路线图文档 |
| 25_本体模型.md | backend/app/models/entity.py | 实体体系 |
| 26_内核与协议.md | backend/app/api/ | 协议实现 |
| 27_数字孪生.md | backend/app/ | 分析引擎 |
| 30_运行地图.md | frontend/src/ | 前端地图 |
| 31_贡献者生态.md | backend/app/ | 贡献者 API |
| 32_标准体系.md | config/ | 配置标准 |
| 33_上下文层.md | backend/app/api/context/ | Context Engine |
| 34_数据飞轮.md | backend/app/ | 反馈闭环 |
| CTO_FINAL_ARCHITECTURE.md | — | 架构冻结，开发必须遵守 |

## 数据结构映射

| 数据模型 | 文档来源 | 代码位置 | Sprint |
|---------|---------|---------|--------|
| User | 02/07 | backend/app/models/user.py | 已有 |
| Industry | 02/03 | backend/app/models/industry.py | 已有 |
| Company | 02/03/07 | backend/app/models/company.py | 已有(Sprint 0.5对齐) |
| Entity(Base) | 02 | backend/app/models/entity.py | Sprint 1 |
| Capability | 02/26 | backend/app/models/capability.py | Sprint 1 |
| Relationship | 02/26 | backend/app/models/relationship.py | Sprint 1 |
| Event | 02 | backend/app/models/event.py | Sprint 1 |
| Evidence | 22/23 | backend/app/models/evidence.py | Sprint 1 |
| GeoScore | 16 | backend/app/models/geo_score.py | Sprint 5 |
| ContextItem | 33 | backend/app/models/context.py | Sprint 3 |

## API 映射

| API | 文档 | 代码 | Sprint |
|-----|------|------|--------|
| /api/v1/auth/register | 08 | backend/app/api/v1/auth.py | 已有 |
| /api/v1/auth/login | 08 | backend/app/api/v1/auth.py | 已有 |
| /api/v1/users/me | 08 | backend/app/api/v1/users.py | 已有 |
| /api/v1/companies/ | 08 | — | Sprint 2 |
| /api/v1/industries/ | 08 | — | Sprint 2 |
| /api/v1/capabilities/ | 08 | — | Sprint 2 |
| /api/v1/context/ | 33/08 | — | Sprint 3 |
| /api/v1/geo-scores/ | 16/08 | — | Sprint 5 |
| MCP Server | 26/33 | — | Sprint 3 |
