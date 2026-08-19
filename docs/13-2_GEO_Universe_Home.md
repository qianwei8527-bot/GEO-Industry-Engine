---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.10 Universe Home - node interface
governance_tier: Implemented (prototype)
precedes:
  - C7 Node Demand Intelligence
interfaces_with:
  - UniverseHomeService
  - Context Engine
  - Ecosystem Graph Engine
  - Reputation Engine
  - Possibility Engine
  - Frontend /universe/home/[node]
---

# GEO Universe Home - 节点界面

> Universe Home 不是首页，是“一个节点进入 Universe 后看见自己的世界”。

---

## 一、五个问题

| 问题 | 内容 | 来源 |
|---|---|---|
| 我是谁 | Identity | Context Engine |
| 我在哪里 | Position / Industry / Stage / Reputation | Context + Reputation |
| 我为什么在这里 | Story / Causality / Milestones | Reputation Events + Memory + Ecosystem Graph |
| 谁影响我 | Ecosystem / Relations | Ecosystem Graph Engine |
| 下一步去哪 | Future / Possibility / Opportunities | Possibility + Connection Engine |

## 二、API

```text
GET /api/v1/universe/node/{node_type}/{node_id}/home
```

返回：

```json
{
  "node_id": "...",
  "node_type": "company",
  "generated_at": "...",
  "identity": {},
  "position": {},
  "story": {},
  "ecosystem": {},
  "future": {},
  "opportunities": {}
}
```

- `UniverseHomeService` 自行从 DB 加载节点、关系、证据、能力数据，前端不再准备 `extra_data`。
- 无数据时不编造：story.causality 返回 `available=false`，关系为空则返回空列表。

## 三、前端

- 路由：`/universe/home/[node]`
- 展示五段：我的位置 / 我的故事 / 我的生态 / 未来路径 / 下一步机会
- 支持 company / provider / ai_agent / government 类型切换
- 不展示 KPI 仪表盘、不渲染 3D 地图

## 四、Relationship 集成修复

- 修复 `RelationshipReputationCalculator.value_creation` 未定义问题，关系信誉计算不再崩溃。
- 修复 `Relationship` 数据类缺失 `purpose / industry / value_exchange` 字段。
- Home 首次真实消费 Relationship 时，Relation Graph 可正常投影。

## 五、验证

- 后端全量回归：195 passed
- 前端 `tsc --noEmit`：通过
- 前端 production build：通过
- 新路由 `/universe/home/[node]`：已生成并返回 200
