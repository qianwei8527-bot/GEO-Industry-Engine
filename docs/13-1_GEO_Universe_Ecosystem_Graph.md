---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.9 Ecosystem Graph Engine - dynamic projection
governance_tier: Implemented (prototype)
precedes:
  - C6.10 Universe Home
interfaces_with:
  - Context Engine
  - Reputation Engine
  - Memory Engine
  - Relationship Engine
  - Connection Engine
  - Registry
---

# GEO Universe Ecosystem Graph - 世界关系结构动态投影

> C6.9 不是漂亮地图，也不是图数据库。
> 它是 Universe 对“一个节点为什么处于现在的位置”的动态投影。

---

## 一、第一原则

1. **Graph 是投影，不是新数据源。**
   - 节点、关系、因果、演化全部来自现有 Engine，不建立 Neo4j，不复制关系数据。

2. **先解释节点，再画图。**
   - 最小闭环是“一个节点的世界解释”，不是全行业大图。

3. **没有真实数据时不编造。**
   - 无事件时 causality 返回 `available=false`，无关系时不生成假边。

## 二、五层输出

| 层 | 问题 | 来源 |
|---|---|---|
| Structure | 谁存在、在哪里 | Context + Registry |
| Relation | 谁连接谁 | Relationship Engine + relationships_list |
| Causality | 为什么变化 | Reputation Event 时间线 |
| Evolution | 如何成长 | Reputation + Memory + Relationship |
| Connection | 下一步连接谁 | Future Connection Engine |

## 三、Engine API

```text
explain(node_id, node_type, extra_data)
    -> structure / relations / causality / evolution / next_connections

project_graph(node_id, node_type, extra_data)
    -> layers + nodes + edges
```

- `explain()` 是节点驾驶舱的数据基础。
- `project_graph()` 是 C6.10 Universe Home 的结构层输入。

## 四、因果链示例

```text
certification_passed
    ↓
customer_success
    ↓
relationship_strengthened
    ↓
Reputation 提升
    ↓
AI 引用 / 合作机会增加
```

事件缺少时，Universe 明确返回“因果不可投影”，不自动补叙事。

## 五、演化链示例

```text
Entry
    ↓
Evidence 增加
    ↓
Reputation 达到 Active
    ↓
关系强化
    ↓
Trusted / Established
```

当前阶段由 Reputation level / status / evidence count / relationship count 投影。

## 六、验收标准

1. 一个节点可以返回五层解释。
2. Relation Graph 复用 Relationship Engine，不建第二套关系。
3. Causality 由事件时间线投影，缺数据时不虚构。
4. Evolution 能区分 entry / active / trusted。
5. Next Connection 复用 Future Connection Engine。
6. project_graph 只返回 JSON 投影，不触发页面渲染。
7. 不新增图数据库，不自动抓取全行业关系。

## 七、实现状态

- `backend/app/universe/ecosystem_graph.py`：EcosystemGraphEngine 已实现。
- 修复 C5.2 Relationship 数据类缺失字段（purpose / industry / value_exchange），否则关系引擎无法创建关系。
- 测试：`backend/tests/test_c69_ecosystem_graph.py` 4/4 通过；后端全量回归 192 passed。
- Registry、DB 结构均未扩展；本轮无 migration。
