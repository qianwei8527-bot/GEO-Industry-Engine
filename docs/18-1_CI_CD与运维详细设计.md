---
status: stable
authority: secondary
version: v1.0
last_review: 2026-07-28
related_docs: [18_工程实践与运维设计.md]
---

# GEO-Industry-Engine CI/CD与运维详细设计

> 状态：架构设计 | 版本：v2.0 | 日期：2026-07-28
> 关联：05_技术架构.md、18_工程实践与运维设计.md

---

## 一、CI/CD流水线

### 1.1 流水线设计 (GitHub Actions)

```
触发: push/PR到main分支
  |
  Step 1: Lint & Type Check (3min)
  |-- ruff check (Python)
  |-- eslint + tsc (TypeScript)
  |-- yamllint (Config)
  |
  Step 2: Unit Tests (5min)
  |-- pytest backend/ (覆盖率 > 80%)
  |-- vitest frontend/
  |
  Step 3: Build (5min)
  |-- docker build backend
  |-- pnpm build frontend
  |
  Step 4: Integration Tests (8min)
  |-- docker-compose up (DB + Redis)
  |-- pytest tests/integration/
  |-- API smoke tests
  |
  Step 5: Deploy (5min)
  |-- staging: 自动部署 (PR merge后)
  |-- production: 手动审批 + Tag push
```

### 1.2 质量门禁

| 门禁 | 条件 | 阻断级别 |
|------|------|:--:|
| Lint通过 | 0 error | 阻断 |
| 类型检查通过 | 0 error | 阻断 |
| 单元测试通过 | 100% pass | 阻断 |
| 覆盖率下降 | 不得低于上次 | 警告 |
| 构建成功 | 退出码0 | 阻断 |
| 集成测试通过 | 关键路径pass | 阻断(关键) |

### 1.3 制品管理

| 制品 | 仓库 | 标签策略 |
|------|------|---------|
| Docker Image (backend) | GitHub Container Registry | git-sha / latest / semver |
| Docker Image (frontend) | GitHub Container Registry | git-sha / latest / semver |
| Python Package | PyPI (未来) | semver |
| Migration脚本 | Git (database/migrations/) | 跟随代码版本 |

---

## 二、环境管理

### 2.1 环境矩阵

| 环境 | 用途 | 部署方式 | 数据 |
|------|------|---------|------|
| local | 本地开发 | docker-compose up | 种子数据 |
| staging | 集成测试/演示 | CI自动部署 | 匿名化生产子集 |
| production | 生产环境 | 手动审批部署 | 完整生产数据 |

### 2.2 Docker Compose (开发环境)

```
services:
  postgres:    端口5432
  redis:       端口6379
  backend:     端口8000 (hot reload)
  frontend:    端口3000 (hot reload)
```

### 2.3 生产部署架构

```
用户 -> CDN (静态资源)
     -> Load Balancer -> API Server (多实例)
                      -> PostgreSQL (主+只读副本)
                      -> Redis (缓存+Session)
                      -> Object Storage (文件/导出)
```

---

## 三、监控与告警

### 3.1 监控栈

| 层面 | 工具 | 关键指标 |
|------|------|---------|
| 基础设施 | Prometheus + Grafana | CPU/内存/磁盘/网络 |
| 应用 | OpenTelemetry + Jaeger | 请求量/延迟/错误率/追踪 |
| 数据库 | pg_stat_statements | 慢查询/连接数/锁等待 |
| 前端 | Web Vitals + Sentry | LCP/FID/CLS + JS错误 |
| 业务 | 自建埋点 | 评估量/认证量/日活/转化率 |

### 3.2 告警规则

| 告警 | 条件 | 级别 | 通知 |
|------|------|:--:|------|
| API错误率 > 5% | 5分钟内 | P0 | 电话+即时消息 |
| P99延迟 > 5s | 持续10分钟 | P1 | 即时消息+邮件 |
| 磁盘使用 > 85% | 任意时刻 | P1 | 即时消息+邮件 |
| 日活下降 > 30% | 同比 | P2 | 邮件 |
| 证书即将过期 | 30天内 | P2 | 邮件 |

### 3.3 日志策略

| 日志类型 | 保留期 | 存储 |
|---------|--------|------|
| 应用日志 | 30天 | Elasticsearch/Loki |
| 审计日志 | 永久 | PostgreSQL + 冷归档 |
| 访问日志 | 90天 | S3/对象存储 |
| 错误日志 | 90天 | Sentry |

---

## 四、备份与恢复

### 4.1 备份策略

| 数据 | 频率 | 保留 | 加密 |
|------|------|------|:--:|
| PostgreSQL全量 | 每日 | 30天 | 是 |
| PostgreSQL增量(WAL) | 持续 | 7天 | 是 |
| 配置文件 | 每次变更 | 永久(Git) | -- |
| 用户上传文件 | 每日 | 30天 | 是 |

### 4.2 恢复流程

1. 定位备份点 (RPO: < 24小时)
2. 恢复数据库 (RTO: < 1小时)
3. 验证数据完整性
4. 切换流量
5. 事后复盘

### 4.3 灾难恢复

- 主区域故障 -> 切换备用区域 (DNS failover)
- 数据库主库故障 -> 自动提升只读副本
- 配置: Terraform/Ansible IaC (可重建)

