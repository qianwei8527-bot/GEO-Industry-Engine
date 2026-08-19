---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C8.1-R Structured Claim & Projection Integrity
governance_tier: Implemented (prototype)
precedes:
  - C8.2 World State Engine
interfaces_with:
  - EvidenceClaim
  - WorldBindingEvidence
  - WorldProjectionService
---

# GEO Universe Structured Claim Integrity

> Evidence verified != Claim verified != Binding verified

## 一、三层分离

```text
Evidence Authenticity  -> 证据来源与内容可信
Claim Support          -> 证据支持某项结构化主张
World Binding Validity -> 主张映射到指定 World Concept
```

## 二、EvidenceClaim

- evidence_id
- subject_type / subject_id
- predicate_code / object_type / object_code / object_value
- claim_text（仅审计展示）
- source_locator / extraction_method
- truth_status / verification_method / verification_result / verified_by / verified_at
- valid_from / valid_until / may_affect_real_metrics / claim_hash

一条 Evidence 可支持多个 Claim；一个 Claim 可参与多个语义兼容 Binding。

## 三、Binding 校验

production verified Binding 必须：

- Evidence verified
- EvidenceClaim verified
- Claim subject 与 Binding entity 精确一致
- predicate 在 evidence_requirement.allowed_predicates 中
- object code 与目标 concept 精确匹配
- source type / 有效期 / 真实指标边界全部满足

`claim_contains` 仅用于发现 Claim Candidate，不再参与 production verified。

## 四、Manifest 与 Source Drift

每个 source ref：

```text
fact_type
fact_id
fact_revision 或 updated_at
canonical_fact_hash
truth_status
```

`source_manifest_hash` 由排序后的规范化引用计算，输入顺序不影响结果。

Fact 内容变化但 ID 不变时，传入 `expected_source_manifest` 会检测并报告 `source_drift`；系统不得静默声称旧 Projection 可完整复现。

## 五、Legacy 审计

对旧 `claim_contains` 建立的 verified Binding：

- 能结构化转换的保留并建立 Claim
- 无法确定的降为 observed
- synthetic 保持 synthetic
- 禁止伪造 predicate/object 保留 verified

## 六、API

```text
POST /api/v1/universe/claims
POST /api/v1/universe/claims/{claim_id}/verify
GET  /api/v1/universe/claims?evidence_id=...
```

source-chain 展示：World Concept <- World Binding <- EvidenceClaim <- Evidence <- Verification。

## 七、验证

- C8.0 + C8.1 + C8.1-R 定向测试：22/22 通过
- 后端全量回归：235 passed
- Migration：`c6g22a1b2c3d4_evidence_claim`
- Legacy 审计：downgraded=6，kept=1
