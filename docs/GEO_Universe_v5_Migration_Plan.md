---
status: stable
version: v2.1
last_review: 2026-07-30
---

# GEO Universe v5 迁移方案

> 版本: v2.1 | 基准: GEO_Universe_v5.2.md

---

## 一、迁移概览

从 v4.x / v5.0 / v5.1 架构迁移到 v5.2 统一架构。

### 核心变化

| 旧概念 | 新概念 | 说明 |
|--------|--------|------|
| 5张地图 | 5个 View | 不是独立页面，是联动视角 |
| 6大系统 | 三层认知入口 | 首页从菜单导航改为认知入口 |
| 检测中心/认证中心/... | GEO Universe 统一入口 | 所有功能从 Universe 进入 |
| 推荐服务商 | 候选服务商 (Candidate) | 平台不替用户决策 |
| NodePanel | IntelligencePanel | 统一7栏面板 |
| /map/* | /navigation?view=* | 路由统一 |

---

## 二、命名映射表

| 旧命名 | 新命名 | 作用域 |
|--------|--------|--------|
| 产业地图 | 产业视图 (View) | 全局 |
| 生态地图 | Ecosystem View | UI/API |
| 商业地图 | Business View | UI/API |
| 成长地图 | Growth View | UI/API |
| 分布地图 | Distribution View | UI/API |
| 未来地图 | Future View | UI/API |
| 推荐服务商 | 候选服务商 (Candidate Provider) | 全局 |
| 6大系统 | 三层认知入口 | 首页 |
| 检测中心 | /detection (检测) | 路由 |
| 认证中心 | /certification (认证) | 路由 |
| 产业导航 | /navigation (产业宇宙) | 路由 |
| 数据资产中心 | /assets (资产) | 路由 |
| 交易市场 | /marketplace (市场) | 路由 |
| 产业情报 | /intelligence (情报) | 路由 |

---

## 三、路由迁移

| 旧路由 | 新路由 | 行为 |
|--------|--------|------|
| / | / | 三层认知入口（重构） |
| /detection | /detection | 保留，作为 Universe 子入口 |
| /certification | /certification | 保留 |
| /navigation | /navigation?view=ecosystem | 新增 view 参数 |
| /assets | /assets | 保留 |
| /marketplace | /marketplace | 保留 |
| /intelligence | /intelligence | 保留 |

---

## 四、API迁移

| 旧端点 | 新端点 | 说明 |
|--------|--------|------|
| - | /api/v1/universe/panel/{type}/{id} | 新增：Intelligence Panel 数据聚合 |
| - | /api/v1/universe/rules | 新增：Universe Rules 查询 |
| - | /api/v1/universe/cite | 新增：规则引用 |
| /api/v1/map/* | /api/v1/graph/ecosystem | 路由重命名 |

---

## 五、数据库迁移

### 新增表（v5.2）
- `competitors` — 竞争关系表
- `growth_stage` — 成长阶段表
- `reputation` — 信誉表
- `geo_event` — 动态事件表

### 保留不变
- 所有现有 22+ 张表
- PostgreSQL + asyncpg
- Alembic migration 历史

---

## 六、前端组件迁移

| 旧组件 | 新组件 | 说明 |
|--------|--------|------|
| - | IntelligencePanel | 新增：7栏统一面板 |
| - | AgentInsight | 新增：Agent UI 组件 |
| Header (旧nav) | Header (新nav) | 品牌更新、导航重构 |
| Home (6卡片) | Home (三层认知入口) | 首页重构 |

---

## 七、配置迁移

```
config/
├── universe/
│   ├── intelligence_panel.yaml  ← 新增
│   ├── rules.yaml               ← 保留
│   └── views.yaml               ← 新增
└── ...
```

---

## 八、验收清单

- [x] 首页三层认知入口
- [x] Header GEO Universe 品牌
- [x] Intelligence Panel 7栏面板
- [x] Navigation 5 View 联动
- [x] API /universe/panel 端点
- [x] API /universe/rules 端点
- [x] 命名统一（View/Candidate/Node）
- [ ] 全部旧文档中文乱码修复
- [ ] 架构冻结文档标记为已废弃
- [ ] Sprint 4.2 计划制定

---

> 迁移原则：零数据丢失，现有表全部保留，新增表仅用于增强。
