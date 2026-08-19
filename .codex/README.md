# .codex 系统结构说明

> 本目录不自动加载。实际加载入口：仓库根 AGENTS.md。
> 上位架构：恒域世界 V10.6（docs/恒域世界_V10.6_四阶段演进架构总纲_含参考平台.md、docs/17-2_恒域世界_V10.6_整体重构_细节设计方案.md）。

## 结构

```
.codex/
├── README.md                 # 本文件：结构说明
├── runtime.md                # 运行时参考（原 AGENTS.md 内容，已降级为参考）
├── roles/                    # 专业视角（9 个角色）
├── rules/                    # 详细规则
├── workflows/                # 分级工作流（含 risk_channels.md）
├── protocol.md               # 协作协议（限高价值场景）
├── lessons_candidates.md     # 经验候选区（新发现先落这里）
├── LESSONS.md                # 已确认经验
└── CHANGELOG.md              # 事实日志
```

## 角色速查

| 文件 | 视角 |
|------|------|
| roles/cto_架构师.md | 架构与商业判断 |
| roles/pm_产品经理.md | 节点需求与证据 |
| roles/be_后端开发.md | FastAPI 后端 |
| roles/fe_前端开发.md | Next.js 前端 |
| roles/qa_质量测试.md | 测试与审计 |
| roles/docs_文档管理.md | 文档一致性 |
| roles/de_数据工程.md | 数据真实性与采集 |
| roles/algo_评分算法.md | 评分模型 |
| roles/ops_运维部署.md | 部署与回滚 |

## 规则速查

| 规则 | 文件 |
|------|------|
| R-001 外部模型评审 | rules/external_review.md |
| R-002 模糊指令（限高成本） | rules/ambiguity_handling.md |
| R-003 代码复用 | rules/component_reuse.md |
| 架构 / 编码 / 文档 | rules/architecture_rules.md 等 |
