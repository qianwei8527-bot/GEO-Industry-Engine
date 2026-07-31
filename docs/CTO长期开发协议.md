---
status: stable
authority: primary
version: v3.2
last_review: 2026-07-30
related_docs: [GEO_Universe_v5.2, 项目核心纲领_v3.2]
---

# GEO-Industry-Engine 长期工程开发协议 v3.2

> 最后更新：2026-07-30 | 状态：stable | 权威等级：primary
> 替代：v3.1 (2026-07-30)
> 关联：GEO_Universe_v5.2.md — 新架构基准文档

---

## 零、最高指令

任何开发任务必须回答三个问题：

1. 这个功能让用户在产业中照见自己了吗？（照见自己）
2. 它增强了六层架构的哪一层？（Rules / Node / Graph / Dynamic / Evolution / Intelligence）
3. 它是否让 GEO 知识图谱、Decision Engine、Intelligence Panel 变得更强？

三个问题不能全部回答的，不开发。

---

## 一、最高原则

### 1.1 事实优先线

代码 > 测试 > API > 配置 > 文档 > 历史报告。

### 1.2 能力评估标准

| 状态 | 定义 |
|------|------|
| 可演示 | 前端->API->引擎->模型 全链路数据流通 |
| 骨架就绪 | 代码结构正确但数据流中断或关键流程缺失 |
| 仅设计 | 只有文档，代码未开始 |

### 1.3 代码质量约束

- 核心模型测试覆盖率 >= 80%
- API 契约测试必须覆盖所有端点
- YAML 配置必须被代码实际读取，否则删除
- Agent 执行链必须可追踪（Intent -> Plan -> Tool -> Result -> Citation -> Rule）
- 所有评分输出必须带解释（score + reason + improvement_action）
- 所有 Agent 解释必须引用 Universe Rules，禁止自由发挥
- Intelligence Panel 数据必须从各层实时聚合，禁止硬编码

---

## 二、禁止事项（v3.2 更新）

### 2.1 战略层面

1. 禁止把 GEO Universe 降级为单纯 GEO 评分工具或企业数据库
2. 禁止删除五张产业地图中的任何一张
3. 禁止把五张地图做成独立页面 — 必须是联动视图（一个 Universe + 五个 Camera View）
4. 禁止做成 SaaS 菜单导航页 — 首页必须是产业宇宙入口
5. 禁止把产业地图做成静态图表 — 必须是动态、可交互、AI驱动
6. 禁止把 Marketplace 当作附加功能 — 它是产业地图的自然商业出口
7. 禁止闭门造车 — 必须借助外部AI（GPT/豆包/Kimi）加速建设

### 2.2 产品层面

8. 禁止因模块暂未开发就从架构中删除
9. 禁止把 TODO、占位接口写成已完成
10. 禁止未经验证就声称功能完成
11. 禁止 Agent 替企业做采购决策 — 只能提供可信候选集
12. 禁止 Intelligence Panel 数据脱节 — 必须与Graph/Decision/Evolution层同步

### 2.3 工程层面

13. 禁止大量新建重复 Markdown 文档。
14. 禁止重复建立已有能力
15. 禁止 Agent 绕过 Context Engine + Decision Engine + Universe Rules 直接生成结论
16. 禁止硬编码业务规则 — 必须走 YAML 或 Universe Rules
17. 禁止保留不工作的配置

---

## 三、命名规范（v3.2 新增）

### 3.1 统一术语

| 中文 | 英文 | 使用场景 |
|------|------|---------|
| GEO宇宙 | GEO Universe | 产品名、文档标题 |
| 产业宇宙 | Industry Universe | 用户界面 |
| 视图 | View | 五个观察角度（不用"地图"作为API/代码名称） |
| 节点 | Node | 图中的企业/服务商/行业等 |
| 智能面板 | Intelligence Panel | 节点点击后弹出的固定面板 |
| 候选服务商 | Candidate Provider | 匹配结果（不用"推荐/winner"） |
| 背书 | Backing / Endorsement | 信誉认证 |
| 产业认知空间 | Industry Cognitive Space | 顶层产品定位 |

### 3.2 代码命名约束

- 前端路由: `/navigation` (不是 `/map`)
- API路径: `/api/v1/graph/ecosystem` (不是 `/map`)
- 组件名: `IntelligencePanel` (不是 `NodePanel`)
- 配置目录: `config/universe/` (不是 `config/map/`)

---

## 四、GEO Universe 六层架构

```
Layer 5: Intelligence — Agent OS + Intelligence Panel + Citation + Memory
Layer 4: Evolution    — 产业演化 (Growth Stage / Value Chain / Future Path)
Layer 3: Dynamic      — 动态事件 (GeoEvent / Change Detection / Pulse)
Layer 2: Graph        — 关系网络 (合作/竞争/供应/投资/能力/学习/交易/社交)
Layer 1: Node         — 统一节点 (Company/Provider/Industry/Person/Product/Capability/Resource/Agent/AI)
Layer 0: Rules        — Universe Rules
```

---

## 五、Intelligence Panel 规范（v3.2 新增）

### 5.1 面板结构

每个节点点击后打开统一的7栏智能面板：状态/测评/方向/学习/资源/数据/商业。

### 5.2 数据聚合规则

Panel API 必须聚合六层数据:
- Layer 1 Node: 节点基本信息
- Layer 2 Graph: 关系列表、竞争信息
- Layer 3 Dynamic: 最近GeoEvent
- Layer 4 Evolution: 成长阶段、价值链位置
- Layer 5 Intelligence: GEO Score、Reputation、Agent诊断
- Layer 0 Rules: 适用的Universe Rules

### 5.3 面板约束

- 面板配置由 `config/universe/intelligence_panel.yaml` 驱动
- 不同节点类型显示不同Section组合
- 所有评分和建议必须引用Universe Rules
- 商业机会Section展示candidates，不是winner

---

## 六、开发优先级

| Sprint | 目标 | 状态 |
|--------|------|------|
| Sprint 3.x | Entity/Context/Decision/Agent OS | DONE |
| Sprint 4.0 | GEO Node Foundation + Universe Rules + 五图 + Intelligence Panel | 重构中 |
| Sprint 4.1 | 动态生态地图 + 五图联动 + Marketplace激活 | 进行中 |
| Sprint 4.2 | Intelligence Panel 完善 + 背书体系 | 计划中 |
| Sprint 4.3 | 3D宇宙 + 外部AI集成 | 计划中 |
| Sprint 5 | AI Evolution + Person/Product节点 | 远期 |

---

> 最高优先级: 解冻所有架构，补全进入架构设计
