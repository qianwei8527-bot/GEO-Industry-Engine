---
status: implemented
authority: architecture
version: v1.0
last_review: 2026-08-02
role: C8.0 Vertical World Model Contract
governance_tier: Implemented (prototype)
precedes:
  - C8.1 Trusted World Projection
interfaces_with:
  - VerticalWorld / VerticalWorldVersion / WorldConcept / WorldConceptRelation / WorldBinding
  - Universal Fact Layer
  - World Package Validator
---

# GEO Universe World Model Contract

> 垂直世界模型是语义投影，不是行业数据库；不复制 Universal Facts，不新增垂直行业专属表。

## 一、分层

```text
Universal Fact Layer
  Node / Evidence / Reputation / Demand / Connection
              ↓
Vertical Semantic Layer
  role / scenario / objective / pain / capability / outcome / evidence_requirement
              ↓
World Projection
  节点在某个垂直赛道中的角色、供需结构与可信缺口
```

## 二、模型

- `vertical_worlds`：世界身份与生命周期
- `vertical_world_versions`：版本、schema、config_hash、发布者、发布状态、不可变
- `world_concepts`：垂直语义概念
- `world_concept_relations`：requires / provides / solves / validates / precedes / belongs_to
- `world_bindings`：Universal Entity -> 世界概念映射，保存 Evidence IDs、truth_status、规则版本

同一节点可绑定多个 World 的不同角色。

## 三、版本化

- 编辑源：`config/universe/worlds/{world_code}/{version}.yaml`
- 发布后版本不可修改
- 修改必须生成新版本
- 每个版本保存 `config_hash`，相同 YAML 生成确定性一致的哈希

## 四、Validator

- world code / concept code 唯一
- 概念类型合法
- 无悬空关系
- precedes / belongs_to 无循环
- relation 起止类型符合约束
- verified binding 必须有 verified Evidence
- 发布版本不可修改

## 五、Connection 投影语义

- proposed / qualified：候选关系
- accepted：双方接受连接意向
- completed：连接流程完成，不代表需求已解决
- outcome 只有生成并通过验证的 Evidence 后，才可投影为 verified outcome

## 六、API

```text
POST /api/v1/universe/worlds
POST /api/v1/universe/worlds/{world_code}/versions
POST /api/v1/universe/worlds/{world_code}/versions/{version}/validate
POST /api/v1/universe/worlds/{world_code}/versions/{version}/publish
GET  /api/v1/universe/worlds/{world_code}/versions/{version}
GET  /api/v1/universe/worlds/{world_code}/versions/{version}/compiled
GET  /api/v1/universe/worlds/{world_code}/versions/diff
POST /api/v1/universe/worlds/{world_code}/versions/{version}/bindings
```

## 七、试验世界

`edu_tech_admission` 作为 draft/synthetic fixture，仅验证通用模型表达能力，不构成真实行业事实。

## 八、验证

- C8.0 定向测试：6/6 通过
- 后端全量回归：219 passed
- Migration：`c6g19a1b2c3d4_world_model_contract` + `c6g20a1b2c3d4_world_version_snapshot`
- 未新增任何垂直行业专属表
