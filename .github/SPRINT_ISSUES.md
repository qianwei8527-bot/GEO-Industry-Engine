# Phase C5.5 Sprint Issues

## 说明
这些 issues 应在 GitHub 上创建以跟踪下一阶段开发。
使用 `gh issue create --title "..." --body "..." --label "enhancement"` 或通过 GitHub Web UI 创建。

---

### Issue 1: C5.5 Universe Home
- **Title:** [C5.5] Universe Home — 节点仪表盘
- **Labels:** enhancement, frontend, P0
- **Body:**
  ```
  ## Universe First Law Check
  - 服务哪个节点？所有节点，提供统一的"我的Universe"视图
  - 帮节点解决什么问题？一站式查看身份、位置、信誉、关系、机会
  - 增加了什么长期记忆？访问记录、关注节点、操作历史
  - 是否增强未来连接能力？是，Home 是连接决策的入口

  ## 验收标准
  - [ ] 左侧身份面板：名称、类型、阶段、信誉等级
  - [ ] 中间 3D Universe 场景：节点可视化
  - [ ] 右侧智能面板：位置、机会、风险、成长路径
  - [ ] 底部时间线：节点 Memory 时间轴
  - [ ] 集成 Context Engine API
  - [ ] 集成 Connection Engine API
  - [ ] 集成 Reputation/Relationship API

  ## 设计文档
  docs/04_Universe_UI_Design.md

  ## API 端点
  GET /api/v1/universe/home/{node_type}/{node_id}
  ```

### Issue 2: C5.5 Universe 3D Scene Enhancement
- **Title:** [C5.5] 3D Universe 场景增强 — 节点/关系可视化
- **Labels:** enhancement, frontend, 3d, P0
- **Body:**
  ```
  ## 验收标准
  - [ ] 节点按类型着色和大小区分
  - [ ] 关系边显示连接强度（粗/细/虚线）
  - [ ] 点击节点展开 Context 面板
  - [ ] 相机动画：节点间飞行切换
  - [ ] 节点脉冲动画：新机会信号

  ## 技术栈
  - React Three Fiber + Drei
  - 复用现有 backend/app/universe/ 数据

  ## 文件
  frontend/src/app/universe/3d/
  ```

### Issue 3: C5.5 Intelligence Panel Integration
- **Title:** [C5.5] Intelligence Panel 集成 Context + Decision + Possibility
- **Labels:** enhancement, frontend, P1
- **Body:**
  ```
  ## 验收标准
  - [ ] Status tab: 当前 Identity + Position
  - [ ] Assessment tab: Reputation 多维雷达图
  - [ ] Direction tab: Decision Engine 路径建议
  - [ ] Learning tab: Memory Engine 时间线
  - [ ] Resources tab: Capability 能力矩阵
  - [ ] Data tab: Evidence 证据列表
  - [ ] Business tab: Connection + Opportunity 推荐

  ## API
  GET /api/v1/universe/panel/{node_type}/{node_id}
  ```

### Issue 4: Backend Test Infrastructure
- **Title:** [Infra] 后端测试基础设施完善
- **Labels:** enhancement, backend, P1
- **Body:**
  ```
  ## 验收标准
  - [ ] 所有 Universe 模块有覆盖率 > 60% 的测试
  - [ ] CI pipeline 中 backend-tests job 绿灯
  - [ ] 测试数据库 migration 自动执行
  - [ ] 添加 test fixtures/conftest.py 共享数据

  ## 当前状态
  10个测试文件已存在，但缺少：
  - position_engine 测试
  - capability_engine 测试
  - future_registry 测试
  - connection_engine 集成测试
  - world_model 测试
  ```

### Issue 5: Frontend CI/Lint Fix
- **Title:** [Infra] Frontend TypeScript strict mode + ESLint fix
- **Labels:** bug, frontend, P1
- **Body:**
  ```
  ## 验收标准
  - [ ] `pnpm lint` 零错误
  - [ ] `npx tsc --noEmit` 零错误
  - [ ] CI pr-check job 绿灯
  - [ ] 修复所有现有 lint/type 错误

  ## 文件
  frontend/tsconfig.json
  frontend/.eslintrc
  ```

### Issue 6: Protected Branch Setup
- **Title:** [Infra] GitHub Branch Protection + CODEOWNERS
- **Labels:** infra, P0
- **Body:**
  ```
  ## 验收标准
  - [ ] master 分支受保护
  - [ ] 要求 PR review (至少 1 人)
  - [ ] 要求 CI status checks 通过
  - [ ] 禁止 force push
  - [ ] CODEOWNERS 文件设置

  ## 操作
  1. GitHub Settings → Branches → Add rule
  2. Branch name pattern: master
  3. Require a pull request before merging: ✓
  4. Require approvals: 1
  5. Require status checks to pass: ✓
  6. search: pr-check, backend-tests, frontend-build
  7. Do not allow bypassing: ✓
  ```
