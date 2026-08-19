---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C8.1 Trusted World Projection
governance_tier: Implemented (prototype)
precedes:
  - C8.2 (待定)
interfaces_with:
  - WorldModelContract
  - WorldBindingEvidence
  - DemandEvent
  - ConnectionCandidate
  - Evidence
---

# GEO Universe Trusted World Projection

> World Model interprets Facts, but never manufactures Facts.

## 一、Evidence 相关性

verified WorldBinding 必须满足：

- Evidence truth_status = verified
- may_affect_real_metrics = true
- 未过期、未撤销、在有效期内
- Evidence 主体与 Binding 实体一致
- source_type 符合 evidence_requirement 的 allowed_source_types
- claim 符合 evidence_requirement 的 claim_contains

支持关系显式存储在 `world_binding_evidence`，不允许用文本相似度伪造相关性。

## 二、Truth 传播

```text
任一 synthetic -> synthetic
全部 verified -> verified
其他情况 -> observed
```

WorldBinding 不得提高源事实 truth_status。

只有满足以下条件的 Connection 才能进入 production projection：

```text
truth_status=verified
decision_scope=production
may_affect_real_metrics=true
```

proposed/qualified = 候选关系；accepted = 连接意向；completed = 流程完成；completed 不等于需求已解决；outcome 必须有 verified Evidence 才能成为 verified outcome。

## 三、投影输出

每次投影包含：

- world_code / world_version / config_hash
- projection_as_of / generated_at
- source_fact_ids / source_manifest_hash
- truth_status_distribution
- items / excluded（含原因）
- coverage / unknown

投影只引用 Universal Fact ID，不复制或改写事实。

## 四、Coverage 与 Unknown

- concept coverage
- verified binding coverage
- evidence coverage
- demand coverage
- connection coverage
- unmapped facts
- unsupported bindings
- missing required concepts
- unknown items

unknown 全部由规则计算，不使用 LLM 猜测。

## 五、API

```text
GET /api/v1/universe/worlds/{world_code}/versions/{version}/projection
GET .../projection/coverage
GET .../projection/unknown
GET .../projection/excluded
GET .../projection/source-chain
```

`/versions/diff` 已声明在动态 `{version}` 路由之前，不会被吞掉。

## 六、验证

- C8.1 / C8.1-R 定向测试：16/16 通过
- 后端全量回归：235 passed
- Migration：`c6g21a1b2c3d4_binding_evidence_support`
