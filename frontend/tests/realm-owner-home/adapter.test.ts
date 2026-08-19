import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildDemandCreateInput,
  buildInformation,
  buildMapView,
  buildResourceGroups,
  buildViewModel,
  computeReadiness,
  computeStartupTasks,
  mapTruthScope,
  selectNextAction,
  validateResourceNeed,
} from "../../src/lib/realm-owner/adapter";
import type {
  ConnectionCandidateItem,
  DemandEventItem,
  RealmOwnerHomeViewModel,
  RealmWorkspaceResponse,
  WorldStateSnapshotItem,
} from "../../src/lib/realm-owner/types";

function makeWorkspace(overrides: Partial<RealmWorkspaceResponse> = {}): RealmWorkspaceResponse {
  return {
    identity: { id: "entity-a", name: "真实主体", entity_type: "company", description: null, geo_id: null, is_verified: false },
    realm: { id: "registry-a", realm_code: "R-1", realm_type: "enterprise", lifecycle_state: "claimed", claim_status: "approved", owner_id: "user-1" },
    access: { controlled: true, can_import: true, can_create_project: true, can_verify: false },
    position: { trust: { verified_evidence: 0, observed_evidence: 0, synthetic_evidence: 0, verified_claims: 0 } },
    evidence: [],
    relationships: [],
    projects: [],
    assets: [],
    authorizations: [],
    timeline: [],
    unknown: [],
    ...overrides,
  };
}

function makeDemand(overrides: Partial<DemandEventItem> = {}): DemandEventItem {
  return {
    id: "demand-1",
    event_id: "EV-1",
    actor_id: "user-1",
    actor_type: "realm_owner",
    actor_label: "域主",
    scenario: "启动期",
    question_text: "需要行业专家",
    objective: "建立认知",
    pain: "缺少专家",
    existing_solution: "",
    missing_capability: "行业专家访谈",
    decision_stage: "research",
    involved_nodes: ["entity-a"],
    mentioned_nodes: [],
    matched_node_ids: [],
    outcome: "pending",
    impact_level: "medium",
    priority: 1,
    source: "realm_owner_form",
    truth_status: "observed",
    is_synthetic: false,
    may_affect_real_metrics: true,
    captured_at: "2026-08-01T00:00:00Z",
    created_at: "2026-08-01T00:00:00Z",
    ...overrides,
  };
}

function makeCandidate(overrides: Partial<ConnectionCandidateItem> = {}): ConnectionCandidateItem {
  return {
    id: "candidate-1",
    candidate_id: "C-1",
    demand_event_id: "demand-1",
    source_node_id: "entity-a",
    target_node_id: "company-x",
    connection_type: "expert",
    matched_capabilities: ["行业专家"],
    evidence_ids: [],
    verified_evidence_count: 0,
    observed_evidence_count: 1,
    synthetic_evidence_count: 0,
    capability_score: 0.8,
    evidence_score: 0,
    reputation_score: 0.5,
    trust_score: 0.4,
    connection_score: 0.6,
    explanation: "能力缺口匹配",
    truth_status: "observed",
    status: "proposed",
    decision_scope: "internal",
    may_affect_real_metrics: true,
    outcome: "pending",
    decided_by: null,
    decision_reason: null,
    decided_at: null,
    created_at: "2026-08-02T00:00:00Z",
    ...overrides,
  };
}

function makeSnapshot(overrides: Partial<WorldStateSnapshotItem> = {}): WorldStateSnapshotItem {
  return {
    id: "snap-1",
    snapshot_id: "SNAP-1",
    world_code: "GEO",
    world_version: "0.9",
    state_scope: "production",
    is_stale: false,
    generated_at: "2026-08-01T00:00:00Z",
    ...overrides,
  };
}

test("truth scope mapping never upgrades unknown to verified/observed", () => {
  assert.equal(mapTruthScope("verified"), "verified");
  assert.equal(mapTruthScope("observed"), "observed");
  assert.equal(mapTruthScope("pending_review"), "observed");
  assert.equal(mapTruthScope("inferred"), "inferred");
  assert.equal(mapTruthScope("synthetic"), "simulation");
  assert.equal(mapTruthScope("verified", true), "simulation");
  assert.equal(mapTruthScope("unknown-status"), "simulation");
});

test("readiness stays missing when only unknown records exist", () => {
  const workspace = makeWorkspace({
    evidence: [
      { id: "e1", entity_id: "entity-a", claim: "未知记录", source_url: null, source_name: null, truth_status: "unknown", is_synthetic: false, may_affect_real_metrics: false, created_at: null },
    ],
  });
  const readiness = computeReadiness({
    identity: workspace.identity,
    evidence: workspace.evidence,
    relationships: workspace.relationships,
    projects: workspace.projects,
    assets: workspace.assets,
    trust: workspace.position.trust,
    realmDemandEvents: [],
    realmCandidates: [],
  });
  assert.equal(readiness.realInputs, "partial");
  assert.equal(readiness.industryKnowledge, "missing");
  assert.notEqual(readiness.industryKnowledge, "ready");
});

test("readiness maps real demand and completed connection", () => {
  const workspace = makeWorkspace({
    evidence: [
      { id: "e1", entity_id: "entity-a", claim: "真实记录", source_url: null, source_name: null, truth_status: "verified", is_synthetic: false, may_affect_real_metrics: true, created_at: null },
    ],
    relationships: [{ id: "r1", source_id: "entity-a", target_id: "company-x", relation_type: "partner", weight: 1, description: null, created_at: null }],
  });
  const readiness = computeReadiness({
    identity: workspace.identity,
    evidence: workspace.evidence,
    relationships: workspace.relationships,
    projects: workspace.projects,
    assets: workspace.assets,
    trust: { verified_evidence: 2, observed_evidence: 1, synthetic_evidence: 0, verified_claims: 1 },
    realmDemandEvents: [makeDemand()],
    realmCandidates: [makeCandidate({ status: "completed", may_affect_real_metrics: true })],
  });
  assert.equal(readiness.realInputs, "partial");
  assert.equal(readiness.resourceDemand, "partial");
  assert.equal(readiness.validConnections, "ready");
});

test("startup tasks keep expected order and default locks", () => {
  const readiness = computeReadiness({
    identity: makeWorkspace().identity,
    evidence: [],
    relationships: [],
    projects: [],
    assets: [],
    trust: { verified_evidence: 0, observed_evidence: 0, synthetic_evidence: 0, verified_claims: 0 },
    realmDemandEvents: [],
    realmCandidates: [],
  });
  const tasks = computeStartupTasks({ readiness, realmDemandEvents: [], realmCandidates: [] });
  assert.deepEqual(
    tasks.map((task) => task.title),
    ["明确行业与赛道", "确认首个试点关系", "定义标准GEO产品", "发布首个资源需求"],
  );
  assert.equal(tasks[0].status, "ready");
  assert.equal(tasks[1].status, "locked");
});

test("next action defaults to real pilot until inputs are available", () => {
  const readiness: RealmOwnerHomeViewModel["readiness"] = {
    realInputs: "missing",
    industryKnowledge: "missing",
    resourceDemand: "missing",
    validConnections: "missing",
  };
  const action = selectNextAction(readiness, []);
  assert.equal(action.title, "确定首个真实试点与品牌关系");
  assert.ok(action.blockedReasons.includes("真实输入待补齐"));
});

test("next action moves to publish demand after inputs", () => {
  const readiness: RealmOwnerHomeViewModel["readiness"] = {
    realInputs: "partial",
    industryKnowledge: "partial",
    resourceDemand: "missing",
    validConnections: "missing",
  };
  const action = selectNextAction(readiness, []);
  assert.equal(action.title, "发布首个资源需求");
  assert.equal(action.targetHref, "resource-demand");
});

test("resource need validation and demand payload scope to realm", () => {
  const errors = validateResourceNeed({
    businessGoal: "",
    flowStep: "",
    missingCapability: "",
    serviceRegion: "",
    timeRequirement: "",
    budgetRange: "",
    cooperationMode: "",
    requiredConditions: "",
    excludedConditions: "",
    sharedDataScope: "",
  });
  assert.ok(errors.businessGoal);
  assert.ok(errors.flowStep);
  assert.ok(errors.missingCapability);

  const input = buildDemandCreateInput(
    {
      businessGoal: "让品牌在AI搜索中被看见",
      flowStep: "需求出现",
      missingCapability: "渠道分发",
      serviceRegion: "华东",
      timeRequirement: "30天",
      budgetRange: "",
      cooperationMode: "",
      requiredConditions: "",
      excludedConditions: "",
      sharedDataScope: "",
    },
    "entity-a",
  );
  assert.ok(input.question_text.includes("让品牌在AI搜索中被看见"));
  assert.ok(input.involved_nodes.includes("entity-a"));
  assert.equal(input.truth_status, "observed");
});

test("map view is template simulation until real projection exists", () => {
  const map = buildMapView({
    mode: "business_flow",
    snapshots: [makeSnapshot()],
    ownerPosition: { status: "unknown", nodeIds: [] },
  });
  assert.equal(map.nodes.length, 6);
  assert.equal(map.edges.length, 5);
  assert.ok(map.nodes.every((node) => node.isTemplate && node.truthScope === "simulation"));
  assert.equal(map.dataSourceLabel.includes("World Snapshot"), true);
});

test("resource groups show reason risk unknowns and never fabricate names", () => {
  const groups = buildResourceGroups({
    realmId: "entity-a",
    userId: "user-1",
    realmDemandEvents: [makeDemand()],
    allCandidates: [makeCandidate()],
    candidateNames: { "company-x": "真实公司" },
  });
  const expert = groups.groups.find((group) => group.type === "expert");
  assert.ok(expert);
  assert.equal(expert.candidates.length, 1);
  assert.equal(expert.candidates[0].name, "真实公司");
  assert.ok(expert.candidates[0].reason.length > 0);
  assert.ok(expert.candidates[0].risk);
  assert.ok(expert.candidates[0].unknowns.includes("真实证据未验证"));
  assert.equal(expert.candidates[0].connectionStatus, "proposed");
});

test("synthetic-only demand does not count as real demand", () => {
  const groups = buildResourceGroups({
    realmId: "entity-a",
    userId: "user-1",
    realmDemandEvents: [makeDemand({ is_synthetic: true, truth_status: "synthetic", may_affect_real_metrics: false })],
    allCandidates: [],
    candidateNames: {},
  });
  assert.equal(groups.hasDemand, false);
});

test("realm switch clears old candidates and information", () => {
  const workspaceA = makeWorkspace({ identity: { ...makeWorkspace().identity, id: "entity-a", name: "Realm A" } });
  const workspaceB = makeWorkspace({ identity: { ...makeWorkspace().identity, id: "entity-b", name: "Realm B" } });
  const demandA = makeDemand({ involved_nodes: ["entity-a"], actor_id: "user-1" });
  const candidateA = makeCandidate({ demand_event_id: demandA.id });

  const vmB = buildViewModel({
    workspace: workspaceB,
    user: { id: "user-1", email: "u@example.com", name: "域主", role: "user" },
    realmId: "entity-b",
    realmDemandEvents: [demandA],
    allCandidates: [candidateA],
    candidateNames: { "company-x": "旧公司" },
    snapshots: [],
    mode: "business_flow",
  });
  assert.equal(vmB.resources.hasDemand, false);
  assert.equal(vmB.resources.groups.every((group) => group.candidates.length === 0), true);
  assert.equal(vmB.information.length, 0);
});

test("information feed keeps observed distinct from verified", () => {
  const info = buildInformation({
    workspace: makeWorkspace({
      evidence: [
        { id: "e1", entity_id: "entity-a", claim: "已观察记录", source_url: null, source_name: null, truth_status: "observed", is_synthetic: false, may_affect_real_metrics: true, created_at: "2026-08-01T00:00:00Z" },
      ],
    }),
    realmDemandEvents: [],
    realmId: "entity-a",
    userId: "user-1",
  });
  assert.equal(info.length, 1);
  assert.equal(info[0].truthScope, "observed");
  assert.notEqual(info[0].truthScope, "verified");
});