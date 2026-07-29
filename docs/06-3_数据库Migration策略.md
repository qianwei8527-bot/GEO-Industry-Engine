---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine 数据库 Migration 策略

> 状态：架构设计 | 版本：v1.0 | 日期：2026-07-28
> 关联：03_数据架构.md、02_领域模型设计.md、CTO长期开发协议.md
> 本文件是协议 C.2-5 设计任务的产出

---

## 一、Migration 工具与目录

| 项目 | 选型/路径 |
|------|---------|
| ORM | SQLAlchemy 2.0 |
| Migration 工具 | Alembic |
| 配置 | `backend/alembic/env.py` |
| 版本目录 | `backend/alembic/versions/` |
| 数据库 | PostgreSQL 15+（开发/测试/生产统一） |
| Docker | `infrastructure/docker-compose.yml`（PostgreSQL + Redis） |

---

## 二、初始 Schema 定稿（17 张表）

| # | 表名 | 对应模型 | 核心字段 | 状态 |
|---|------|---------|---------|:--:|
| 1 | entities | entity.py | geo_id, entity_type, name, tenant_id | ✅ |
| 2 | companies | company.py | entity_id(FK), industry_id, geo_score, trust_score | ✅ |
| 3 | industries | industry.py | name, parent_id, level, description | ✅ |
| 4 | capabilities | capability.py | entity_id(FK), name, level, evidence_count | ✅ |
| 5 | relationships | relationship.py | source_id(FK), target_id(FK), rel_type, strength | ✅ |
| 6 | events | event.py | entity_id(FK), event_type, data, occurred_at | ✅ |
| 7 | evidence | evidence.py | entity_id(FK), evidence_type, source, credibility | ✅ |
| 8 | trust_scores | domain/trust | entity_id(FK), score, factors, calculated_at | ✅ |
| 9 | certifications | certification.py | entity_id(FK), level, status, valid_until | ✅ |
| 10 | users | user.py | email, hashed_password, role, tenant_id | ✅ |
| 11 | analytics_events | analytics_event.py | event_name, user_id, entity_id, data, timestamp | ✅ |
| 12 | market_demands | market_demand.py | publisher_id, title, budget, status | ✅ |
| 13 | orders | order.py | demand_id, provider_id, status, amount | ✅ |
| 14 | transaction_reviews | transaction_review.py | order_id(FK), reviewer_id, rating, content | ✅ |
| 15 | subscriptions | subscription.py | user_id(FK), plan_id, status, valid_until | ✅ |
| 16 | payment_transactions | payment_transaction.py | subscription_id(FK), amount, status, provider | ✅ |
| 17 | competitors | competitor.py | entity_id(FK), competitor_id(FK), data | ✅ |

> 当前 Migration 文件：`backend/alembic/versions/002_all_tables.py`
> Status: 已编写，未执行（需 docker-compose up postgres）

---

## 三、Migration 版本管理策略

### 3.1 命名规范

```
versions/
├── 001_initial_schema.py      # 初始基础表
├── 002_all_tables.py          # 完整17表
├── 003_add_<feature>.py       # 后续增量
└── ...
```

每次生成：`alembic revision -m "<简短描述>" --autogenerate`

### 3.2 版本规则

| 规则 | 说明 |
|------|------|
| 每个 PR 最多包含 1 个 migration | 禁止一个 PR 包含多个 migration |
| migration 必须可回滚 | 每个 `upgrade()` 必须有对应的 `downgrade()` |
| 禁止修改已合并的 migration | 已合并到 main 的 migration 文件永不修改 |
| 新字段必须有默认值 | 或允许 NULL，否则存量数据迁移失败 |
| 生产执行前先在 staging 验证 | staging 数据库是生产数据的近实时副本 |

### 3.3 执行流程

```
开发:
  docker-compose up postgres
  alembic upgrade head

部署(staging):
  backup database
  alembic upgrade head
  运行冒烟测试

部署(production):
  backup database
  maintenance mode ON
  alembic upgrade head
  maintenance mode OFF
  监控错误日志 30min
```

---

## 四、种子数据设计

### 4.1 种子数据目录

`scripts/seed_data.py` — 已存在，未执行。

### 4.2 种子数据内容

| 类别 | 内容 | 数据量 |
|------|------|:----:|
| 行业分类 | GEO产业9层价值链分类 | ~50 条 |
| 认证等级 | L0-L4 等级定义 | 5 条 |
| 定价套餐 | Free/Growth/Pro/Business/Enterprise | 5 条 |
| 权限定义 | 所有权限ID及描述 | ~30 条 |
| 示例企业 | 3-5 家虚构企业用于开发测试 | 3-5 条 |
| 管理员账户 | admin@geo-industry.com | 1 条 |

### 4.3 种子数据执行

```bash
# 开发环境
docker-compose up postgres
alembic upgrade head
python scripts/seed_data.py

# 测试环境（CI）
docker-compose up -d postgres
alembic upgrade head
python scripts/seed_data.py --env test
pytest
```

### 4.4 种子数据设计原则

- 种子数据是**开发/测试基础数据**，不是生产数据
- 生产数据通过系统正常运行积累，不通过种子脚本注入
- 种子数据的 ID 固定化，方便测试断言
- 行业分类、认证等级等**配置类数据**属于种子数据
- 企业、用户、认证记录等**业务数据**不属于种子数据

---

## 五、多环境数据库配置

| 环境 | 数据库 | 数据来源 | 用途 |
|------|--------|---------|------|
| 本地开发 | Docker PostgreSQL | 种子数据 | 日常开发 |
| CI/测试 | Docker PostgreSQL（临时实例） | 种子数据 + 测试夹具 | 自动化测试 |
| Staging | 云 PostgreSQL | 脱敏的生产近实时副本 | 部署前验证 |
| Production | 云 PostgreSQL（托管） | 真实用户数据 | 正式环境 |

### 环境变量

```
DATABASE_URL=postgresql://user:password@host:5432/geo_industry
DATABASE_URL_TEST=postgresql://user:password@localhost:5433/geo_test
```

---

## 六、当前待执行操作

| # | 操作 | 命令 | 阻塞因素 |
|---|------|------|---------|
| 1 | 启动 PostgreSQL | `docker-compose up postgres` | 环境就绪即可 |
| 2 | 执行初始 Migration | `alembic upgrade head` | PostgreSQL 已启动 |
| 3 | 加载种子数据 | `python scripts/seed_data.py` | Migration 已执行 |
| 4 | 修复 6 个集成测试 | 执行后重跑 | PostgreSQL 已就绪 |

> 以上 4 步是**架构设计阶段不需要执行的环境操作**，记录在此供编码阶段启动时参考。
