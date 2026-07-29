# GEO-Industry-Engine

**面向GEO产业生态的产业认知、身份、信任、知识、智能决策与生态连接基础设施。**

> 让GEO产业生态中的企业、个人、服务商、机构、政府、投资者、研究者，都能找到自己的位置、理解自己的状态、发现机会、识别风险、建立可信身份、积累数字资产、找到生态连接。

---

## 为什么需要GEO？

用户获取信息的入口正从搜索引擎转向AI：

```
传统：用户需求 -> 搜索引擎 -> 网站 -> 比较 -> 决策
AI时代：用户需求 -> 询问AI -> AI推荐 -> 用户决策
```

企业面临新问题：**如何被AI发现、理解、信任和推荐？** GEO（Generative Engine Optimization）就是答案。

---

## 六大产品系统

```
首页 — GEO生态入口广场（飞轮 + 快速检测 + 角色分流）
  |
  +-- 检测中心 · GEO战略评估      — 我是谁？在产业中排哪里？
  +-- 认证中心 · 可信身份证明      — 如何证明我是谁？
  +-- 产业导航 · 产业数字地图      — 行业在哪里？机会在哪里？
  +-- 数据资产中心 · 知识沉淀     — 我拥有什么？还缺什么？
  +-- 交易市场 · 生态连接器        — 谁需要我？我需要谁？
  +-- 产业情报系统 · 共享能力层    — 竞争/机会/风险在哪？
```

> 详见 [CTO长期开发协议.md](docs/CTO长期开发协议.md) v2.9（最高开发宪章）

---

## GEO产业生态飞轮

```
数据进入 -> Entity/Capability/Relationship/Event/Evidence
  -> 产业知识形成 -> Context Engine理解产业
  -> Decision Engine评估/预测/发现 -> Agent OS自动执行
  -> 用户获得认知 -> 建立GEO数字身份 -> 认证建立信任
  -> 产业导航发现机会 -> 数据资产沉淀 -> 交易市场连接
  -> 用户行为与新事件再次进入 -> 数据持续增长 -> 循环
```

---

## 文档体系

67份设计文档，详见 [索引.md](docs/索引.md)

### 必读（3份）
| 文件 | 说明 |
|------|------|
| [CTO长期开发协议](docs/CTO长期开发协议.md) | **最高开发宪章 v2.9** — 战略、六大系统、引擎、禁止事项 |
| [00_项目宪章](docs/00_项目宪章.md) | 定位、技术架构层、术语映射 |
| [项目核心纲领](docs/项目核心纲领.md) | 战略层面核心原则 |

### 产品架构
[01_产品架构PRD](docs/01_产品架构PRD.md) · [17_商业模式](docs/17_产品定义与商业模式.md) · [21_应用场景](docs/21_应用场景设计.md) · [17-1_投资人视角](docs/17-1_投资人视角报告.md)

### 领域与技术
[02_领域模型](docs/02_领域模型设计.md) · [02-1_Decision Engine](docs/02-1_Decision%20Engine设计.md) · [03_数据架构](docs/03_数据架构.md) · [05_技术架构](docs/05_技术架构.md) · [05-1~05-6 技术子设计](docs/)

### 前端与后端
[06_前端设计](docs/06_前端设计.md) · [06-*系列 11份](docs/) · [07_后端设计](docs/07_后端设计.md) · [08_API规范](docs/08_API接口规范.md) · [08-1_API契约](docs/08-1_API契约补充定义.md)

### Agent与AI
[04_Agent OS](docs/04_Agent_OS设计.md) · [04-1_Agent工作流](docs/04-1_Agent工作流详细设计.md) · [40_Agent指令手册](docs/40_Agent系统指令手册.md) · [16_评分算法](docs/16_GEO评分算法与模拟验证.md)

### 产业生态
[09_产业导航交互](docs/09_产业导航交互设计.md) · [26_产业内核](docs/26_GEO产业内核与开放协议.md) · [26-1_开放生态](docs/26-1_开放生态技术规范.md) · [27_数字孪生](docs/27_GEO产业数字孪生与演化模拟.md) · [28~30 产业子设计](docs/)

### 快速进入（按角色）
- **工程师**: CTO长期开发协议 -> 05_技术架构 -> 02_领域模型 -> 08_API规范
- **产品经理**: CTO长期开发协议 -> 01_产品PRD -> 06_前端设计 -> 21_应用场景
- **投资人**: CTO长期开发协议 -> 17-1_投资人视角 -> 01_产品PRD
- **Codex/Agent**: 40_Agent指令手册 -> 04-1_工作流设计 -> 04_Agent OS

---

## 技术栈

| 层 | 选型 |
|----|------|
| 前端 | Next.js 14 (App Router) + Tailwind CSS + Recharts + D3.js |
| 后端 | FastAPI (Python 3.12) + SQLAlchemy 2.0 + Alembic |
| 数据库 | PostgreSQL 16 + Redis 7 |
| 配置 | YAML驱动 (config/scoring/*.yaml, config/certification/*.yaml etc.) |
| Agent | Agent OS (4基础Agent + IntentRouter + TaskPlanner) |
| 协议 | REST API + MCP + Webhook (开放生态) |
| 基础设施 | Docker + GitHub Actions CI/CD |

---

## 项目结构

```
GEO-Industry-Engine/
├── docs/           # 67份架构设计文档
├── backend/        # FastAPI后端 (57端点/17模型/14Schema)
├── frontend/       # Next.js前端 (13路由已开发/27路由设计)
├── agents/         # Agent OS (4 Agent + 路由 + 规划器)
├── config/         # 14个YAML配置 (评分/认证/定价/市场/情报)
├── database/       # Alembic Migration
├── tests/          # 单元+集成测试
├── infrastructure/ # Docker部署
└── scripts/        # 工具脚本
```

---

## 开发原则

1. 任何开发必须回答: 服务哪个角色？增强哪个系统？增强哪个引擎能力？
2. 配置化优先: 评分/认证/定价/权限全部YAML驱动，不硬编码
3. Agent不能创造事实，只能解释知识图谱中已有数据
4. 所有评分输出必须带 reason + improvement_action + evidence_sources
5. 数据 > 展示，长期 > 临时，生态 > 功能

---

## 当前状态

| 阶段 | 状态 |
|------|:--:|
| 架构设计 | ✅ 完成 (67份文档, 20维度≥96, 综合96.8) |
| C.2 设计补全 | ✅ 完成 (前端信息架构/用户流程/YAML Schema/API契约/Migration) |
| C.3 编码阶段 | 🔜 就绪 (6个YAML接入Decision Engine + Agent多步链 + 首页改造) |

> *让GEO产业中的每一个参与者，找到自己的位置。*