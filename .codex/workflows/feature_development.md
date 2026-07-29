# GEO-Industry-Engine 功能开发流程

> 所有功能开发必须遵循本流程，确保质量与一致性。

---

## 一、开发全流程

```
Step 1: 需求加载
  - 产品经理 Agent 分析需求
  - 明确用户价值和归属系统
  - 输出产品需求单

Step 2: 架构审查
  - CTO Agent 审查架构影响
  - 确认是否在冻结范围内
  - 输出审查结论

Step 3: 技术方案
  - 后端 Agent 设计数据模型和 API
  - 前端 Agent 设计页面和交互
  - 输出技术方案

Step 4: 方案评审
  - CTO Agent 审批技术方案
  - 测试 Agent 确认可测试性
  - 确认后进入开发

Step 5: 编码实现
  - 按目录规范和代码质量要求编码
  - 遵守模块化、配置化原则
  - 预留 Agent 调用接口

Step 6: 测试验证
  - 单元测试覆盖核心逻辑
  - API 测试覆盖所有端点
  - 回归测试确保不破坏旧功能

Step 7: 文档同步
  - 文档 Agent 更新所有受影响文档
  - 更新 .codex/REFERENCES.md
  - 更新 索引.md

Step 8: 提交与关闭
  - 按 Git 规范提交
  - CTO Agent 确认完成
  - Sprint 验收关闭
```

---

## 二、开发前检查清单

每次开发前由 CTO Agent 执行：

[ ] 需求属于哪个产品模块？
[ ] 影响哪些已有模块？
[ ] 是否需要修改数据模型？
[ ] 是否影响未来 Agent OS？
[ ] 是否已有开源方案可复用？
[ ] 是否属于当前 Sprint 范围？
[ ] 是否有明确的验收标准？

**只要有一项无法回答，禁止开始编码。**

---

## 三、代码提交流程

```
开发完成 -> 自测通过 -> 提交审查 -> 测试验证 -> 文档同步 -> CTO 确认 -> Git 提交
```

### Git 提交规范

| 类型 | 用途 | 示例 |
|------|------|------|
| feat | 新增功能 | feat: add company registration API |
| fix | 修复问题 | fix: correct GEO score calculation |
| refactor | 架构调整 | refactor: split auth into core module |
| docs | 文档更新 | docs: update CTO_AGENT.md |
| db | 数据库变更 | db: add certification tables |
| infra | 基础设施 | infra: add docker-compose config |
| test | 测试相关 | test: add auth unit tests |

---

## 四、开发原则优先级

P0 项目长期战略 > P1 系统整体架构 > P2 数据资产模型 >
P3 产品核心流程 > P4 用户体验优化 > P5 页面视觉效果

**禁止为 P5 牺牲 P0-P3。**

---

> 版本：v1.0 | 2026-07-28
