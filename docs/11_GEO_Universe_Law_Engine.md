---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.7 Universe Law Engine - implemented (Registry / Evaluation / Conflict / Explanation)
governance_tier: Implemented
precedes:
  - C6.8 Living World Model
interfaces_with:
  - Event Backbone
  - Reputation / Position / Capability / Relationship / Memory
---

# GEO Universe Law Engine — 世界规则引擎

> Law 回答："世界中的事情发生后，会产生什么自然结果？"
> 不是普通规则系统；是治理规则——决定节点如何参与世界，不创造世界。

---

## 一、Law 第一性原理

1. **Law 是治理，不是创造。**
   - Observation 发现新事物；Knowledge 理解它是什么；Law 决定它如何参与世界。
   - Law 永不自动产生新节点、不自动改变分类体系、不修改 Universe Rules 与权重。

2. **Event 是输入，State 是结果。**
   - Law 只消费 UniverseEvent，只产生 State Delta；最终 State 是投影，不是唯一真相。

3. **可解释、可重放。**
   - 每次 State 变化必须能回溯到：触发事件 + Law id + 规则版本 + Evidence。

4. **可配置、可替换。**
   - Law 来自配置（laws.yaml / Law Registry），不是散落的 `if xxx: score += y`。

---

## 二、架构

```
UniverseEvent（Event Backbone 统一事件）
      ↓
Law Registry（laws.yaml：law_id / trigger / effects）
      ↓
Law Evaluation（匹配 trigger → 生成 State Delta）
      ↓
State Mutation（当前落地 Reputation / Position / Memory；Capability / Relationship 列为后续）
      ↓
New Event / Memory Story（因果链延续）
```

## 三、Law Registry

```yaml
version: "1.0.0"
laws:
  - law_id: certification_trust_growth
    trigger:
      event_type:
        - certification.approved
    effects:
      reputation:
        - dimension: governance
          delta: 10
          event_type: certification_passed
          source: government
      position:
        recompute: true
      memory:
        story: "节点获得认证，信任基础建立。"
```

- `trigger.event_type` 匹配 Event Backbone 的 event_type；LawRegistry.candidates 按 priority 排序返回。
- `effects` 声明式描述状态变化，不写引擎代码。
- 修改 Law 必须走治理流程（system_admin + 审计），Event 不得自动改变 Law。

## 四、Law Evaluation

1. 从 Event Backbone 接收事件（含 node_id、actor、source、correlation_id）。
2. LawRegistry.candidates 返回匹配的 Law，按 priority 降序。
3. 生成 State Delta 列表：
   ```json
   [{"engine": "reputation", "dimension": "governance", "delta": 10},
    {"engine": "position", "recompute": true},
    {"engine": "memory", "story": "节点获得认证，信任基础建立。"}]
   ```
4. 未匹配事件 → 记录事件但无 State 变化（Law 不负责一切）。

## 五、State Mutation（安全边界）

- 已实现：ReputationEngine / PositionEngine（经 Context）/ MemoryEngine；Relationship / Capability / Connection 投影列为后续项。
- 不允许：创建节点、修改分类、改 Law、改权重、直接 set 分数。
- 失败必须记录（不静默）；部分失败保留已应用部分并标记。

## 六、安全边界（冻结）

1. Law 不自动修改 World Model / Registry / Future States。
2. Law 不绕过 Reputation 事实边界：只有 verified Evidence 或治理确认的事件可触发信誉变化。
3. synthetic / fake 事件不得触发对真实节点的 Law 效果。
4. 每次 State 变化追加 Memory 与 AuditLog（actor / law_id / correlation_id）。
5. Law 版本化；重放同一事件集 + 同一版本 → 同一 State。

## 七、C6.6.6 验证结果（原型闭环）

`certification.approved` 事件已穿透：

- Event Backbone 记录事件 + correlation_id ✅
- LawRegistry 匹配 certification_trust_growth ✅
- ReputationEngine 记录 `certification_passed`（government 来源）+ 重算 ✅
- PositionEngine 重算（growth_stage / reputation_level）✅
- MemoryEngine 写入"信任基础建立"故事 ✅
- 未匹配事件无副作用 ✅

（测试 test_c666_event_backbone.py，2/2 通过）

## 八、C6.7 已实现（正式版）

C6.7 将 C6.6.6 原型升级为 Universe Law Governance Layer，四个能力全部落地：

1. **Law Registry（A）**：`config/universe/laws.yaml` 现含 3 条治理 Law，每条具备 `law_id / version / status / owner / description / priority / trigger / conditions / effects / constraints / audit`。
2. **Law Evaluation（B）**：`UniverseLawEngine.handle()` 按 Event → Law Candidate → Condition Evaluation → Mutation Plan → Execute 执行；`evidence_status=verified` 才允许信誉变化，`observed / pending_review / self_report` 只写记忆。
3. **Law Conflict（C）**：`ConflictResolver` 按 priority 处理冲突；风险 Law（priority>=100）覆盖增长 Law，被抑制规则返回 `suppressed` 与原因。
4. **Law Explanation（D）**：每次应用返回 event / law / conditions_met / impacts / confidence，可回答“为什么信誉变化”。

当前 4 条 Law：

- `certification_trust_growth`：verified 认证 → governance +10，重算 Position，写入记忆
- `certification_memory_only`：observed 认证 → 仅记忆，不提升信誉
- `complaint_risk_override`：verified 投诉 → delivery -12，重算 Position，写入记忆
- `ontology_adoption_governance`：世界结构提案治理批准，只写记忆与事件，不自动修改 Registry

安全边界保持：Law 不创建节点、不修改分类/权重；synthetic / fake 不进入真实节点效果；未匹配事件只记录到 Backbone。

验证结果：`test_c67_law_governance.py` 6/6 + `test_c666_event_backbone.py` 2/2 = 8/8；后端全量回归 185 passed。

## 九、后续（未完成项）

1. Event Backbone 升级为 `universe_events` 索引表（回填领域事件）
2. 补齐 Memory / Relationship / OpportunityMemory 持久化（P0，见持久化审计）后，Law 可重放恢复 State
3. Law Registry 的治理修改接口（审批、版本对比、下线）
4. State Mutation 扩展 Relationship / Capability / Connection 投影（随 C6.8 / C6.9）

> **冻结声明：** Law 是治理规则，不是创造规则。实现必须可追溯至本文档与 Event Backbone 契约。
