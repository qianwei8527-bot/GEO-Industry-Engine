# GEO-Industry-Engine 架构规则

> 所有架构设计必须遵守的规则。违反以下规则属于重大架构偏差。

---

## 一、核心架构原则

### 原则 1：数据模型优先于页面展示

```
任何开发前：
  先确认数据模型是否完整
  再确认 API 是否就绪
  最后开发前端页面
```

### 原则 2：模块化原则

- 每个模块有明确的职责边界
- 模块间通过 API 通信，不直接依赖
- 低耦合，高内聚

### 原则 3：配置化原则

- 评分权重、阈值走 YAML 配置
- Agent 配置走 YAML
- Prompt 模板走 YAML
- 禁止硬编码任何业务参数

### 原则 4：Agent 兼容原则

- 所有核心能力通过 Function Calling 暴露
- 业务逻辑封装为可组合的 Tool
- 支持 Agent 间协作流程

---

## 二、禁止事项

1. 跳过 Entity 基类直接建表
2. Agent 直接调用 LLM 或读数据库
3. 评分权重硬编码
4. 删除 tenant_id/region/lang_tag 预留字段
5. 修改 7 层架构的层顺序
6. 前端页面直接调数据库
7. 为赶进度跳过 Sprint 边界规则

---

## 三、技术栈约束

| 层次 | 技术选型 | 状态 |
|------|---------|------|
| 前端 | Next.js (React, TypeScript, Tailwind) | 冻结 |
| 后端 | FastAPI (Python 3.12) | 冻结 |
| 关系数据库 | PostgreSQL 16 (asyncpg) | 冻结 |
| 缓存 | Redis 7 | 冻结 |
| ORM | SQLAlchemy 2.0 (异步) | 冻结 |
| API 文档 | OpenAPI 自动生成 | 冻结 |
| Agent 框架 | BaseAgent + Registry | 冻结 |
| 容器化 | Docker + docker-compose | 冻结 |
| 图数据库 | 第一阶段不用，保留接口 | 待审批 |
| 向量数据库 | 第一阶段不用，保留接口 | 待审批 |

---

## 四、目录结构规范

```
backend/
  app/
    api/v1/     # Router，仅路由
    core/       # 配置/依赖
    models/     # SQLAlchemy
    schemas/    # Pydantic
    services/   # 业务逻辑
    domain/     # 领域服务
    context/    # Context Engine
    decision/   # 决策模型
    mcp/        # MCP 协议

frontend/
  src/
    app/        # Next.js App Router
    components/ # 组件
    lib/        # 工具

config/
  scoring/*.yaml
  agents/*.yaml
  prompts/*.yaml
```

---

> 版本：v1.0 | 2026-07-28 | 基于：35_CTO架构冻结.md
