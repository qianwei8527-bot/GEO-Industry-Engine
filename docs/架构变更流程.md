# GEO-Industry-Engine Architecture Change Process

> 任何影响架构的变更必须经过此流程。未经审批的架构变更将被 revert。

---

## 变更类型

| 类型 | 示例 | 审批人 |
|------|------|--------|
| **Level 1** | 新增字段、修改注释 | 无需审批，但需更新 metadata |
| **Level 2** | 新增模块、修改 API | CTO 审批 + 影响分析 |
| **Level 3** | 修改 7 层结构、删除实体 | CTO 审批 + 架构委员会 |

## 变更流程

`
1. 提交变更说明（原因 + 方案 + 影响范围）
       ↓
2. 影响分析（哪些文档/代码/API 受影响）
       ↓
3. 文档更新计划（列出需修改的文档）
       ↓
4. CTO 审批（Level 2+）
       ↓
5. 实施变更（代码 + 文档同步）
       ↓
6. 测试验证
       ↓
7. 更新 affected docs 的 metadata.last_review
`

## 影响分析模板

`
变更说明：
原因：
影响的文档：
影响的模块：
影响的 API：
测试方案：
回退方案：
`

## 文档更新要求

- 修改模型 → 更新 02_领域模型 和 03_数据架构 的 metadata
- 修改 API → 更新 08_API规范 和 affected router docs
- 新增模块 → 更新 INDEX.md 和 35_CTO冻结
