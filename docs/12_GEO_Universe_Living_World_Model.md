---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-01
role: C6.8 Living World Model - implemented prototype
governance_tier: Implemented (prototype)
precedes:
  - C6.9 Ecosystem Graph
interfaces_with:
  - Event Backbone
  - Law Engine
  - KnowledgeCandidate
  - Universe Registry
---

# GEO Universe Living World Model - 世界结构演化引擎

> World Model 不是 Universe 的输入，而是 Universe 对世界变化的理解结果。
> 它回答的不是“世界有什么分类”，而是“世界正在形成什么新的结构”。

---

## 一、第一原则

1. **World Model 是理解结果，不是静态分类库。**
   - Observation 发现变化；Evidence 提供可信事实；Knowledge 形成认知；Law 决定如何治理。

2. **世界结构只通过治理采纳。**
   - 不自动创建行业、不自动修改节点类型、不自动改写 Registry。
   - 概念必须先成为 Proposal，经 reviewer/system_admin 与 Law 检查后，才能进入 Adoption。

3. **概念生命周期不可逆跳级。**
   - `observed -> emerging -> recognized -> proposed -> adopted`
   - 任意一步被治理拒绝，可回到 `recognized` 或标记 `rejected`。

4. **合成与真实隔离。**
   - synthetic 信号只能停留在观察层，不能触发真实节点或真实世界结构采纳。

---

## 二、最小闭环

```text
Observation
    ↓
Evidence（来源、时间、领域、证据 ID）
    ↓
KnowledgeCandidate（概念涌现）
    ↓
WorldModelProposal（世界结构提案）
    ↓
Law Governance（verified + reviewer + Law 检查）
    ↓
Universe Adoption（状态采纳；Registry 更新保持人工治理）
```

## 三、概念生命周期

| 状态 | 含义 | 进入条件 |
|---|---|---|
| observed | 世界已观察到该概念 | 首次观测 |
| emerging | 概念持续出现 | confidence >= 0.3 |
| recognized | 已形成稳定认知 | evidence_count >= 3、来源 >= 2、evidence_status = verified、非 synthetic |
| proposed | 已生成 Ontology Proposal | recognized 后由治理提议 |
| adopted | 世界采纳 | Proposal approved 后显式 adopt |
| rejected | 治理拒绝 | reviewer 拒绝并填写原因 |

## 四、WorldModelProposal

```yaml
proposal_id: string
candidate_key: string
concept_name: string
concept_type: role | capability | organization | product | relationship_type
status: pending | approved | rejected | adopted
ontology_suggestion: {}
evidence_ids: []
source_ids: []
confidence: float
emergence_score: float
proposed_by: string
reviewed_by: string
reviewed_at: datetime
reason: string
law_ids: []
law_explanation: []
correlation_id: string
registry_update_pending: true
```

- `proposed_by` 必须来自治理主体，不能是 `system` / `auto` / `client`。
- `approved` 必须通过 Law Engine 检查，并保留 explanation。
- `adopted` 不自动修改 `registry.yaml`，只标记 `registry_update_pending=true`。

## 五、Industry Context Model

每个产业维护一份轻量上下文：

```yaml
industry_id: string
updated_at: datetime
emerging_concepts: []
proposals: []
evidence_ids: []
summary: string
```

它表示 Universe 当前对产业“正在形成什么”的理解，不生成完整产业地图。

## 六、Law 治理

新增一条治理 Law：

```yaml
law_id: ontology_adoption_governance
trigger: ontology.proposal_approved
conditions:
  evidence_status: verified
  source_type: governance
effects:
  memory: 世界结构提案经治理批准，概念进入 Universe 采纳流程。
```

- 只有 `evidence_status=verified` 且 `source_type=governance` 才能通过。
- synthetic 事件被 `synthetic_block` 拦截。
- Law 只写记忆与事件，不改变 Registry，不创建节点。

## 七、Registry 边界

- `LivingWorldModel.adopt()` 只改变候选状态与提案状态。
- Registry 变更保持人工治理：返回 `registry_update_pending=true`，后续由治理接口合并。
- 任何自动 `registry.yaml` 写入都不允许。

## 八、示例：AI Employee

1. Observation 多次发现 `AI Employee` / `AI Agent 运营` 概念。
2. Evidence 记录来源、时间、领域、证据 ID。
3. KnowledgeCandidate 从 observed 升至 recognized。
4. reviewer 提出 WorldModelProposal，建议 concept_type=role。
5. Law 检查通过（verified + governance）。
6. Universe 标记 adopted，Event Backbone 记录 `ontology.concept_adopted`。
7. Registry 保持原状，等待人工治理合并。

## 九、验收标准

1. 未预定义概念可完整走通 Observation → Evidence → Knowledge → Proposal → Governance → Adoption。
2. 无 verified 证据不能进入 recognized/proposal。
3. synthetic 信号不能进入提案。
4. 非治理 actor 不能批准提案。
5. approval 必须经过 Law Engine，返回 law_ids 与 explanation。
6. adopted 后 Registry 不被自动修改。
7. Event Backbone 可查询 proposal_created / proposal_approved / concept_adopted 三类事件。

## 十、后续（C6.8.5 Persistence Hardening）

- KnowledgeCandidate / WorldModelProposal / IndustryContext 落库。
- Law Registry 治理接口。
- Registry 人工合并接口。
- Event Backbone 升级为 `universe_events` 索引表。

## 十一、实现状态

- `backend/app/universe/world_model.py`：KnowledgeCandidate 生命周期、WorldModelProposal、IndustryContextModel、Law 检查、Event Backbone 事件均已实现。
- `config/universe/laws.yaml`：新增 `ontology_adoption_governance` 治理 Law，总数 4 条。
- Registry 保持只读：adoption 只返回 `registry_update_pending=true`，不自动写入 `registry.yaml`。
- 测试：`backend/tests/test_c68_living_world_model.py` 7/7 通过；C6.7/C6.6.6 定向测试继续通过；后端全量回归 185 passed。
