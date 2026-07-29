---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---


> ⚠️ **本文档已被 [CTO长期开发协议.md](CTO长期开发协议.md) v2.9 替代。** 所有架构原则、五大系统定义、禁止事项以 CTO长期开发协议 为准。本文仅做历史参考。
---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-27
related_docs: [00]
---
﻿# GEO-Industry-Engine — CTO 最终架构冻结文件

> 这是所有开发必须遵守的唯一架构标准。非经 CTO 审批，不得修改冻结项。
> 版本：v1.0 | 冻结日期：2026-07-27 | 审批人：CTO

---

## 一、产品定位（已冻结）

### 一句话定位

> GEO-Industry-Engine 是 AI 时代连接人工智能与真实产业世界的行业上下文基础设施（Industry Context Layer）。

### 核心使命

建立 AI 时代产业认知、连接和价值分配的新型基础设施。让全球产业数据、关系、能力、信任持续积累，并反过来提升 AI 理解产业世界的能力。

### 5 项核心原则（禁止修改）

| # | 原则 | 含义 |
|---|------|------|
| 1 | 产业实体是基础，页面是视图 | 先建数据模型再做 UI，页面只是产业数据的展示层 |
| 2 | 数据模型优先于功能开发 | 每个 Sprint 先确保数据模型稳定，再构建上层功能 |
| 3 | 所有评分和规则可配置化 | 权重、阈值、Prompt 模板走 YAML 配置，不走硬编码 |
| 4 | AI 能力必须基于 Context API | Agent、评分引擎不能直接读数据库，必须通过 Context Layer |
| 5 | 所有功能未来必须支持 API/MCP | 每个模块设计时考虑第三方 AI Agent 接入可能性 |

---

## 二、技术架构（已冻结）

### 7 层闭环架构

```

                         GEO Data Flywheel
                    （数据反馈：越用越聪明）
                               |
              +-----------------+-----------------+
              |          用户层                     |
              |   产业导航 / 搜索 / Dashboard       |
              +-----------------+-----------------+
                               | REST API / WebSocket
              +-----------------+-----------------+
              |    GEO Protocol / MCP Server       |
              |   （外部 AI Agent 调用的标准入口）    |
              +-----------------+-----------------+
                               |
              +-----------------+-----------------+
              |         应用能力层                   |
              |  产业地图 / AI增长 / 交易市场        |
              |  API Gateway / Auth / Cache         |
              +-----------------+-----------------+
                               |
              +-----------------+-----------------+
              |         智能引擎层                   |
              |  Agent OS / 决策模型 / 评分算法     |
              +-----------------+-----------------+
                               |
              +-----------------+-----------------+
              |      GEO Context Layer              |
              |   Context Engine / MCP / Memory     |
              +-----------------+-----------------+
                               |
              +-----------------+-----------------+
              |         产业知识层                   |
              |  实体 / 能力 / 关系 / 事件 / 信任   |
              +-----------------+-----------------+
                               |
              +-----------------+-----------------+
              |           数据层                    |
              |  PostgreSQL / GraphDB / VectorDB    |
              |  企业 / 人才 / 行业 / 案例          |
              +----------------------------------+

```

### 技术栈冻结

| 层 | 技术选型 | 状态 |
|---|---------|------|
| 前端框架 | Next.js (React, TypeScript, Tailwind) | 冻结 |
| 后端框架 | FastAPI (Python 3.12) | 冻结 |
| 关系数据库 | PostgreSQL 16 (asyncpg) | 冻结 |
| 缓存/队列 | Redis 7 | 冻结 |
| ORM | SQLAlchemy 2.0 (异步) | 冻结 |
| API 文档 | OpenAPI (自动生成) | 冻结 |
| Agent 框架 | BaseAgent + Registry (自定义) | 冻结 |
| 容器化 | Docker + docker-compose | 冻结 |
| 图数据库 | 第一阶段不用，保留 Neo4j 接口 | 待审批 |
| 向量数据库 | 第一阶段不用，保留接口 | 待审批 |
| 任务队列 | Celery (requirements 已有) | 允许扩展 |

### 架构冻结范围

| 冻结级别 | 含义 | 涵盖 |
|---------|------|------|
| 已冻结 | 开发中不得修改，除非 CTO 书面审批 | 定位、7 层架构、技术栈、API 规范 |
| 允许扩展 | 可在冻结基础上增加能力 | Agent 数量、决策模型因子、YAML 配置项 |
| 禁止修改 | 不得以任何理由修改 | 一句话定位、7 层结构、Entity 继承体系 |

---

## 三、数据模型原则（已冻结）

### Entity 继承体系（禁止修改）

```
Entity（基类，表 entities）
  +-- Company（企业，表 companies）
  +-- Product（产品/服务，表 products）
  +-- Person（产业个人，表 persons）
  +-- Organization（机构，表 organizations）
  +-- Agent（AI Agent，表 agents）
  +-- Region（区域，表 regions）
```

Entity 基类字段（禁止修改）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| geo_id | VARCHAR(64) | 统一产业身份标识 (GEO-COMPANY-xxx) |
| entity_type | VARCHAR(32) | 实体类型枚举 |
| name | VARCHAR(255) | 实体名称 |
| description | TEXT | 实体描述 |
| is_verified | BOOLEAN | 是否认证 |
| tenant_id | UUID | 多租户隔离（预留） |
| region | VARCHAR(32) | 区域（预留） |
| lang_tag | VARCHAR(10) | 语言标记（预留） |
| metadata | JSONB | 扩展字段 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

### 核心实体表

| 表 | 继承自 | 特有字段 |
|----|--------|---------|
| users | 独立 | email, password_hash, role, status |
| entities | — | 基类字段 |
| companies | entities | website, size, contact_email, subscription_tier |
| industries | — (独立树) | code, parent_id, level, sort_order |
| capabilities | — | company_id, name, level, evidence_ids |
| relationships | — | source_id, target_id, relation_type, weight |
| events | — | entity_id, event_type, occurred_at, impact_level |
| evidences | — | target_id, source_type, source_url, confidence_level |
| geo_scores | — | company_id, score_value, factors_json, config_version |

### 字段规范（已冻结）

- 所有表必须带 `created_at`、`updated_at`（TIMESTAMPTZ）
- 预留字段：`tenant_id`、`region`、`lang_tag`、`metadata`（JSONB）
- 主键统一 UUID v4
- `geo_id` 格式：`GEO-{ENTITY_TYPE}-{UUID_SHORT}`

---

## 四、API 原则（已冻结）

### 版本化

- 所有 API 以 `/api/v1/` 开头
- 向后兼容：新增字段不许删除旧字段

### 认证

- JWT Bearer Token（已实现）
- Token 过期时间 30 分钟（配置化）

### 统一响应格式

```json
{
  "code": 200,
  "data": {},
  "error": null,
  "meta": { "page": 1, "page_size": 20, "total": 100 }
}
```

### API 分类冻结

| 分类 | 前缀 | 第一阶段 |
|------|------|---------|
| Auth | /api/v1/auth/ | 已有 |
| Users | /api/v1/users/ | 已有 |
| Companies | /api/v1/companies/ | Sprint 2 |
| Industries | /api/v1/industries/ | Sprint 2 |
| Capabilities | /api/v1/capabilities/ | Sprint 2 |
| Relationships | /api/v1/relationships/ | Sprint 2 |
| Events | /api/v1/events/ | Sprint 2 |
| Context | /api/v1/context/ | Sprint 3 |
| GEO Score | /api/v1/geo-scores/ | Sprint 5 |
| MCP Server | MCP Protocol | Sprint 3 |

---

## 五、Agent 原则（已冻结）

### 架构位置 / 数据流（禁止修改）

```
Agent → Context API（/api/v1/context/）→ Context Engine → 产业知识层 → 数据层
```

Agent 不直接访问数据库，不直接调用 LLM。所有数据获取走 Context API，所有决策调用走决策模型。

### Agent 注册

所有 Agent 通过 `AgentRegistry` 注册，框架在 `agents/core/base.py` 中已有。

### Agent 开发顺序（已冻结）

| 顺序 | Agent | Sprint | 依赖 |
|------|-------|--------|------|
| 1 | Context Agent（基础设施） | 4 | Sprint 3 Context API |
| 2 | Industry Analyst Agent | 4 | Context Agent |
| 3 | Data Filler Agent | 4 | — |
| 4+ | Scanner / Company Intelligence / GEO Optimization | 后续 | 数据层就绪 |

---

## 六、数据资产原则（已冻结）

### 数据生命周期

```
发现 -> 验证 -> 结构化 -> 应用 -> 反馈
```

详见 `32_GEO数据飞轮与生命周期.md`。

### 数据来源等级（已冻结）

| 等级 | 含义 | 示例 |
|------|------|------|
| L0 | 用户自填 | 企业自己提交的信息 |
| L1 | 平台审核 | 经过人工审核 |
| L2 | 第三方证明 | 客户案例、行业报告 |
| L3 | 市场验证 | 持续 AI 推荐表现 |
| L4 | AI 交叉验证 | 多模型一致认可 |

每条数据记录附带 `confidence_level` 字段。

---

## 七、扩展原则（已冻结）

### 多租户

- 所有核心表预留 `tenant_id`（UUID，可为 NULL）
- 第一阶段：单租户模式，`tenant_id = NULL`
- Phase 2：启用租户隔离

### 多区域

- `entities` 表预留 `region`（VARCHAR(32)）
- 枚举值：`cn-north`、`cn-east`、`global` 等
- 第一阶段不实现区域功能

### 多语言

- 预留 `lang_tag`（VARCHAR(10)，如 `zh-CN`、`en-US`）
- 第一阶段所有内容为中文，不实现 i18n

### 配置中心

- 配置目录：`config/`
- 评分配置：`config/scoring/*.yaml`
- Agent 配置：`config/agents/*.yaml`
- Prompt 模板：`config/prompts/*.yaml`

---

## 八、禁止事项（禁止修改）

以下行为在架构冻结期间不被允许：

| # | 禁止行为 | 理由 |
|---|---------|------|
| 1 | 跳过 Entity 基类直接建 Company 表 | 破坏继承体系，后续 Person/Product 无法统一 |
| 2 | Agent 直接调 LLM 或读数据库 | 绕过 Context API 导致数据不一致 |
| 3 | 评分权重硬编码 | 违背可配置原则 |
| 4 | 删减 `tenant_id`/`region`/`lang_tag` 预留字段 | 未来扩展需要重建表 |
| 5 | 修改 7 层架构的层顺序 | 依赖关系已锁定 |
| 6 | 前端页面直接调数据库 | 必须经过 API Gateway |
| 7 | 为赶进度跳过 Sprint 边界规则 | 数据模型优先于页面 |

---

## 九、文档-代码一致性矩阵

| 模块 | 设计文档 | 代码状态 | 差距 | 处理方式 | 优先级 |
|------|---------|---------|------|---------|-------|
| User | 02_领域模型, 07_后端 | models/user.py (36L) | 功能完整 | 冻结 | — |
| Company | 02_领域模型, 03_数据, 07_后端 | models/company.py (39L) | 字段与 02 不一致 | **开发前修改** | P0 |
| Industry | 02_领域模型, 03_数据 | models/industry.py (22L) | 功能完整 | 冻结 | — |
| Entity(Base) | 02_领域模型(##五) | ❌ | 必须建立 | **Sprint 1** | P0 |
| Capability | 02_领域模型, 26_内核 | ❌ | 必须建立 | **Sprint 1** | P0 |
| Relationship | 02_领域模型, 26_内核 | ❌ | 必须建立 | **Sprint 1** | P0 |
| Event | 02_领域模型(##六) | ❌ | 必须建立 | **Sprint 1** | P0 |
| Evidence | 22_测量方法论, 23_合规 | ❌ | 需要建立 | **Sprint 1** | P1 |
| Trust | 22_测量方法论, 32_标准 | ❌ | 先建评分再建信任 | **Sprint 4** | P2 |
| Intent | 33_上下文层 | ❌ | 随 Context Engine 实现 | **Sprint 3** | P1 |
| GEO Score | 16_评分算法 | ❌ | 评分引擎 | **Sprint 5** | P1 |
| Visibility Record | 12_决策路径, 16_评分 | ❌ | 数据采集层 | **Sprint 5** | P2 |
| Context API | 33_上下文层 | ❌ | 核心接口 | **Sprint 3** | P0 |
| Agent Framework | 04_Agent OS | agents/core/base.py (36L) | 骨架就绪，需填充 | **Sprint 4** | P1 |
| MCP Server | 26_内核, 33_上下文 | ❌ | 随 Context Engine | **Sprint 3** | P1 |
| Dashboard | 09_导航交互 | ❌ | 前端页面 | **Sprint 5** | P1 |
| Map System | 09_导航, 30_运行地图 | ❌ | 前端页面 | **Sprint 5** | P2 |
| Transaction | 17_商业模式, 21_场景 | ❌ | 延后 | **后续版本** | P3 |
| Auth | 07_后端, 08_API | api/v1/auth.py (41L) | 功能完整 | 冻结 | — |
| Config System | 16_评分算法(##七) | ❌ | config/scoring/ 目录 | **Sprint 0.5** | P0 |

### 问题分类汇总

| 分类 | 数量 | 说明 |
|------|------|------|
| **(A) 开发前必须修改** | 1 | Company 字段对齐 |
| **(B) Sprint 1 解决** | 5 | Entity/Capability/Relationship/Event/Evidence |
| **(C) Sprint 3-5 解决** | 9 | Context API/MCP/Scoring/Dashboard 等 |
| **(D) 暂不实现** | 1 | 交易系统 (Transaction) |
| **已冻结（代码已就绪）** | 4 | User/Industry/Auth/Agent Framework 骨架 |

---

## 十、开发路线（重新定义）

### Sprint 0.5：工程整理 + 基础修复（Week 1）

**目标**：消除开发前的技术债，建立工程基线。

**输入**：架构冻结文件、索引.md 映射、数据模型对齐

| 任务 | 输出 | 目录 |
|------|------|------|
| Company 字段对齐 | 统一 company.py, 更新 03/07 文档 | backend/app/models/ |
| 扩展性预留 | 在建表时增加 tenant_id, region, lang_tag | backend/app/models/ |
| Doc->Code 映射 | .codex/索引.md | .codex/ |
| scripts 清理 | 活跃脚本移入 scripts/active/ | scripts/ |
| 配置目录 | config/scoring/visibility.yaml | config/ |
| Docker 确认 | docker compose up -> /health ok | — |

**数据库变化**：无新表，修改 companies 表字段定义

**验收标准**：docker compose up 后后端 /health 返回 ok，所有模型字段与 02 文档一致

---

### Sprint 1：Core Model（Week 2-3）

**目标**：跑通数据闭环——输入企业 -> 建立实体 -> 关联关系 -> AI 理解 -> 输出画像。

**输入**：对齐后的 Company 模型、Entity 基类设计

| 模型 | 输出 | 目录 |
|------|------|------|
| Entity(Base) | models/entity.py | backend/app/models/ |
| Company（继承 Entity） | 重构 company.py | backend/app/models/ |
| Capability | models/capability.py | backend/app/models/ |
| Relationship | models/relationship.py | backend/app/models/ |
| Event | models/event.py | backend/app/models/ |
| Evidence | models/evidence.py | backend/app/models/ |

**数据库变化**：新建 entities, capabilities, relationships, events, evidences 表
**API 变化**：无（Sprint 2 才加 API）

**验收标准**：Python shell 中可以创建 Entity -> Company -> 关联 Capability -> 添加 Event -> 查询完整企业画像

---

### Sprint 2：CRUD API（Week 4-5）

**目标**：所有核心模型的 REST API 就绪，前端可以调数据。

**输入**：Sprint 1 的数据模型

| API | 端点 |
|-----|------|
| Company | POST/GET/PUT /companies/{id} |
| Industry | GET /industries（树形）, GET /industries/{id} |
| Capability | POST/GET /capabilities |
| Relationship | POST/GET /relationships |
| Event | POST/GET /events |

**数据库变化**：无
**API 变化**：新增 10+ 端点

**验收标准**：Postman/Curl 可以创建企业、关联能力、查询关系

---

### Sprint 3：Context Engine（Week 6-7）

**目标**：建立 AI Agent 可以调用的上下文接口。

**输入**：Sprint 1+2 的数据 + API

| 模块 | 输出 |
|------|------|
| Context Engine | /api/v1/context/company/{id} |
| Context Engine | /api/v1/context/industry/{id} |
| Context Engine | /api/v1/context/search (RAG) |
| MCP Server | GEO MCP Protocol 注册 |
| 配置化 | config/scoring/*.yaml 生效 |

**数据库变化**：无
**API 变化**：新增 /context/* 端点

**验收标准**：调用 /context/company/{id} 返回企业完整上下文（含能力+关系+事件）

---

### Sprint 4：Agent Framework（Week 8-9）

**目标**：第一个 Agent 跑通——输入企业 -> 分析产业结构 -> 输出发展建议。

**输入**：Sprint 3 的 Context API

| Agent | 功能 |
|-------|------|
| Context Agent | 基础上下文获取工具 |
| Industry Analyst Agent | 产业分析 + 机会发现 |
| Agent Tool Layer | Tool 注册系统 |

**验收标准**：调用 Industry Analyst Agent -> 输入企业 ID -> 返回产业分析报告

---

### Sprint 5：Graph View + GEO Intelligence（Week 10-12）

**目标**：前端可视化和基础智能。

**输入**：Sprint 1-4 的全部输出

| 模块 | 功能 |
|------|------|
| Graph View | 关系展示（力导向图或列表） |
| Dashboard | 企业画像 + 产业位置 |
| GEO Scoring | 评分引擎上线（配置化权重） |
| GEO Index | 企业 500 榜 / 行业指数 |

**验收标准**：Dashboard 展示企业画像，GEO Score 可查询

---

## 十一、CTO 批准报告

### CTO Review Result

**架构状态：通过**

### 当前成熟度

| 维度 | 评分 | 说明 |
|------|------|------|
| 战略 | 95/100 | 已冻结，无需调整 |
| 产品 | 90/100 | 7 层闭环完整 |
| 技术 | 85/100 | 数据模型层待校对，架构正确 |
| 代码 | 30/100 | 正常开发前状态，地基层待建 |

### 开发前必须完成事项（A 类）

| # | 事项 | 状态 |
|---|------|------|
| 1 | Company 字段对齐（02/03/07 统一） | 计划中 |
| 2 | 扩展性预留字段入模型 | 计划中 |
| 3 | .codex/索引.md 映射表 | 计划中 |

### 可以立即进入开发的事项（B 类）

| # | 事项 | Sprint |
|---|------|--------|
| 1 | Entity(Base) 模型 | Sprint 1 |
| 2 | Capability + Relationship + Event 模型 | Sprint 1 |
| 3 | CRUD API | Sprint 2 |
| 4 | Context Engine | Sprint 3 |

### 第一阶段开发目标

> 跑通 GEO Industry Intelligence Loop——输入一个企业 -> 建立企业实体 -> 关联行业/能力/关系/证据/事件 -> AI 理解 -> 输出企业画像和产业位置。

### CTO 签字结论

GEO-Industry-Engine 的顶层设计已通过全部架构审查。34 份文档的架构描述与代码实现之间不存在不可修复的偏差。Phase 1-3 发现的 4 个风险中，2 个已确认并写入修复计划（模型重复、扩展性预留），2 个被判断为不成立（页面依赖、AI 外挂）。

**开发可以启动。Sprint 0.5 前置条件修复完成后，进入 Sprint 1 Core Model 编码阶段。**

> CTO 签字确认
> 日期：2026-07-27
> 版本：GEO-Industry-Engine v1.0
