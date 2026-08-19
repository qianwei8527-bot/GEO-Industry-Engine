import {
  DEFAULT_NEXT_ACTION,
  MAP_EDGE_TRUTH_SCOPE,
  MAP_NODE_DEFS,
  STARTUP_TASK_DEFS,
} from "./config";
import type {
  ConnectionCandidateItem,
  DemandEventCreateInput,
  DemandEventItem,
  InformationCategory,
  MapMode,
  RealmOwnerHomeViewModel,
  RealmWorkspaceResponse,
  ReadinessStatus,
  ResourceGroupType,
  ResourceNeedFormValues,
  StartupTaskStatus,
  TruthScope,
  UserProfile,
  WorldStateSnapshotItem,
} from "./types";

const VERIFIED = "verified";
const OBSERVED = "observed";
const SIMULATION = "simulation";
const INFERRED = "inferred";

export function mapTruthScope(
  truthStatus: string | null | undefined,
  isSynthetic = false,
): TruthScope {
  if (isSynthetic) return SIMULATION;
  switch ((truthStatus || "").toLowerCase()) {
    case VERIFIED:
      return VERIFIED;
    case "pending_review":
    case OBSERVED:
      return OBSERVED;
    case INFERRED:
      return INFERRED;
    case "synthetic":
      return SIMULATION;
    default:
      // Unknown status must never be presented as verified or observed.
      return SIMULATION;
  }
}

export function isUnknownTruthStatus(truthStatus: string | null | undefined): boolean {
  const value = (truthStatus || "").toLowerCase();
  return !["verified", "observed", "pending_review", "inferred", "synthetic"].includes(value);
}

export interface ReadinessInput {
  identity: RealmWorkspaceResponse["identity"] | null;
  evidence: RealmWorkspaceResponse["evidence"];
  relationships: RealmWorkspaceResponse["relationships"];
  projects: RealmWorkspaceResponse["projects"];
  assets: RealmWorkspaceResponse["assets"];
  trust: RealmWorkspaceResponse["position"]["trust"];
  realmDemandEvents: DemandEventItem[];
  realmCandidates: ConnectionCandidateItem[];
}

export function computeReadiness(input: ReadinessInput): RealmOwnerHomeViewModel["readiness"] {
  const verifiedEvidence = input.trust.verified_evidence || 0;
  const observedEvidence = input.trust.observed_evidence || 0;
  const verifiedClaims = input.trust.verified_claims || 0;
  const hasIdentity = Boolean(input.identity?.name);
  const hasAnyRecord =
    input.evidence.length > 0 ||
    input.relationships.length > 0 ||
    input.projects.length > 0 ||
    input.assets.length > 0;

  const realInputs: ReadinessStatus = !hasIdentity
    ? "missing"
    : !hasAnyRecord
      ? "missing"
      : verifiedEvidence > 0 && input.relationships.length > 0
        ? "partial"
        : observedEvidence > 0
          ? "partial"
          : "partial";

  const industryKnowledge: ReadinessStatus = !hasAnyRecord
    ? "missing"
    : verifiedClaims > 0
      ? "ready"
      : verifiedEvidence > 0
        ? "partial"
        : observedEvidence > 0
          ? "partial"
          : "missing";

  const hasRealDemand = input.realmDemandEvents.some(
    (event) => !event.is_synthetic && event.truth_status !== "synthetic",
  );
  const completedDemand = input.realmDemandEvents.some(
    (event) =>
      !event.is_synthetic &&
      event.may_affect_real_metrics &&
      ["accepted", "completed", "won"].includes(event.outcome),
  );
  const resourceDemand: ReadinessStatus = !hasRealDemand
    ? "missing"
    : completedDemand
      ? "ready"
      : "partial";

  const realConnections = input.realmCandidates.filter(
    (candidate) =>
      candidate.may_affect_real_metrics &&
      candidate.truth_status !== "synthetic",
  );
  const hasQualified = realConnections.some((c) =>
    ["qualified", "accepted", "completed"].includes(c.status),
  );
  const hasCompleted = realConnections.some(
    (c) => c.status === "completed" && c.may_affect_real_metrics,
  );
  const validConnections: ReadinessStatus = !hasQualified
    ? "missing"
    : hasCompleted
      ? "ready"
      : "partial";

  return { realInputs, industryKnowledge, resourceDemand, validConnections };
}

export interface StartupTaskInput {
  readiness: RealmOwnerHomeViewModel["readiness"];
  realmDemandEvents: DemandEventItem[];
  realmCandidates: ConnectionCandidateItem[];
}

export function computeStartupTasks(input: StartupTaskInput): RealmOwnerHomeViewModel["startupTasks"] {
  const { readiness, realmDemandEvents, realmCandidates } = input;
  const hasRealInput = readiness.realInputs !== "missing";
  const hasIndustryKnowledge = readiness.industryKnowledge !== "missing";
  const hasDemand = readiness.resourceDemand !== "missing";
  const hasCompletedConnection = realmCandidates.some(
    (c) => c.status === "completed" && c.may_affect_real_metrics,
  );
  const hasAcceptedConnection = realmCandidates.some(
    (c) => c.status === "accepted" && c.may_affect_real_metrics,
  );

  return STARTUP_TASK_DEFS.map((definition) => {
    let status: StartupTaskStatus = definition.defaultStatus;
    let blockedReason = definition.blockedReason;
    let targetHref = definition.targetHref;

    if (definition.id === "clarify-track") {
      if (readiness.realInputs === "missing") {
        status = "ready";
        blockedReason = null;
        targetHref = "real-input";
      } else if (readiness.industryKnowledge === "partial") {
        status = "in_progress";
        blockedReason = "已开始记录，仍需补齐关键行业输入";
        targetHref = "real-input";
      } else if (readiness.industryKnowledge === "ready") {
        status = "completed";
        blockedReason = null;
        targetHref = null;
      } else {
        status = "in_progress";
        blockedReason = "需要更多真实输入或研究记录";
        targetHref = "real-input";
      }
    }

    if (definition.id === "confirm-pilot") {
      if (!hasRealInput || !hasIndustryKnowledge) {
        status = "locked";
        blockedReason = "先补齐真实输入并建立行业认知";
      } else if (hasCompletedConnection) {
        status = "completed";
        blockedReason = null;
      } else if (hasAcceptedConnection) {
        status = "needs_review";
        blockedReason = "首个试点连接已接受，待域主核验真实结果";
      } else {
        status = "ready";
        blockedReason = null;
        targetHref = "real-input";
      }
    }

    if (definition.id === "define-product") {
      if (!hasCompletedConnection) {
        status = "locked";
        blockedReason = "需要首个试点与真实结果作为依据";
      } else {
        status = "ready";
        blockedReason = null;
        targetHref = "real-input";
      }
    }

    if (definition.id === "publish-demand") {
      if (!hasRealInput) {
        status = "locked";
        blockedReason = "需要真实业务目标与能力缺口";
      } else if (hasDemand) {
        status = "in_progress";
        blockedReason = "需求已记录，等待候选生成或域主确认";
        targetHref = "resource-demand";
      } else {
        status = "ready";
        blockedReason = null;
        targetHref = "resource-demand";
      }
    }

    return {
      id: definition.id,
      title: definition.title,
      status,
      blockedReason,
      targetHref,
    };
  });
}

export interface MapBuildInput {
  mode: MapMode;
  snapshots: WorldStateSnapshotItem[];
  ownerPosition: RealmOwnerHomeViewModel["map"]["ownerPosition"];
}

export function buildMapView(input: MapBuildInput): RealmOwnerHomeViewModel["map"] {
  const latestSnapshot = input.snapshots
    .filter((snapshot) => !snapshot.is_stale)
    .sort((a, b) => (b.generated_at || "").localeCompare(a.generated_at || ""))[0];

  const nodes = MAP_NODE_DEFS[input.mode].map((node) => ({
    id: node.id,
    label: node.label,
    truthScope: SIMULATION as TruthScope,
    isTemplate: true,
  }));

  const edges = nodes.slice(0, -1).map((node, index) => ({
    id: `${node.id}->${nodes[index + 1].id}`,
    source: node.id,
    target: nodes[index + 1].id,
    truthScope: MAP_EDGE_TRUTH_SCOPE,
  }));

  return {
    mode: input.mode,
    nodes,
    edges,
    ownerPosition: input.ownerPosition,
    dataSourceLabel: latestSnapshot
      ? `World Snapshot ${latestSnapshot.world_version}（${latestSnapshot.state_scope}）`
      : "无 World 投影数据：当前为预演模板",
    snapshotId: latestSnapshot?.id || null,
  };
}

export function buildOwnerPosition(
  workspace: RealmWorkspaceResponse,
): RealmOwnerHomeViewModel["map"]["ownerPosition"] {
  // No dedicated position API exists yet; keep unknown instead of inventing a position.
  return { status: "unknown", nodeIds: [] };
}

export interface ResourceBuildInput {
  realmId: string;
  userId: string | null;
  realmDemandEvents: DemandEventItem[];
  allCandidates: ConnectionCandidateItem[];
  candidateNames: Record<string, string>;
}

export function isRealmScopedDemand(
  event: DemandEventItem,
  realmId: string,
  _userId: string | null,
): boolean {
  return (
    event.involved_nodes.includes(realmId) ||
    event.mentioned_nodes.includes(realmId)
  );
}

export function buildResourceGroups(input: ResourceBuildInput): RealmOwnerHomeViewModel["resources"] {
  const realmDemandIds = new Set(input.realmDemandEvents.map((event) => event.id));
  const candidates = input.allCandidates.filter(
    (candidate) => candidate.demand_event_id && realmDemandIds.has(candidate.demand_event_id),
  );

  const groups: RealmOwnerHomeViewModel["resources"]["groups"] = [
    { type: "expert", candidates: [] },
    { type: "channel", candidates: [] },
    { type: "delivery_partner", candidates: [] },
  ];

  for (const candidate of candidates) {
    const groupType = mapConnectionTypeToGroup(candidate.connection_type);
    const group = groups.find((g) => g.type === groupType) || groups[2];
    const truthScope = mapTruthScope(
      candidate.truth_status,
      candidate.truth_status === "synthetic",
    );
    const unknowns: string[] = [];
    if (candidate.verified_evidence_count === 0) {
      unknowns.push("真实证据未验证");
    }
    if (candidate.observed_evidence_count > 0 && candidate.verified_evidence_count === 0) {
      unknowns.push("记录仅为已观察");
    }
    if (candidate.synthetic_evidence_count > 0) {
      unknowns.push("包含预演数据");
    }
    if (!["accepted", "completed"].includes(candidate.status)) {
      unknowns.push("连接尚未确认");
    }

    group.candidates.push({
      id: candidate.id,
      name: input.candidateNames[candidate.target_node_id] || "主体名称待解析",
      reason: candidate.explanation || "系统按能力缺口生成候选，需域主核验。",
      truthScope,
      risk:
        candidate.verified_evidence_count === 0
          ? candidate.synthetic_evidence_count > 0
            ? "候选以预演证据为主，正式接洽前必须核验真实证据。"
            : "暂无已验证证据，需人工核验身份与交付能力。"
          : "需域主确认后再进入真实连接。",
      unknowns,
      connectionStatus: candidate.status,
      evidenceCounts: {
        verified: candidate.verified_evidence_count,
        observed: candidate.observed_evidence_count,
        synthetic: candidate.synthetic_evidence_count,
      },
    });
  }

  const hasRealDemand = input.realmDemandEvents.some(
    (event) => !event.is_synthetic && event.truth_status !== "synthetic",
  );
  return { hasDemand: hasRealDemand, groups };
}

export function mapConnectionTypeToGroup(type: string): ResourceGroupType {
  const value = (type || "").toLowerCase();
  if (value.includes("expert") || value.includes("专家") || value.includes("consultant")) {
    return "expert";
  }
  if (value.includes("channel") || value.includes("渠道") || value.includes("distribution")) {
    return "channel";
  }
  return "delivery_partner";
}

export interface InformationBuildInput {
  workspace: RealmWorkspaceResponse;
  realmDemandEvents: DemandEventItem[];
  realmId: string;
  userId: string | null;
}

export function buildInformation(input: InformationBuildInput): RealmOwnerHomeViewModel["information"] {
  const items: RealmOwnerHomeViewModel["information"] = [];

  for (const event of input.realmDemandEvents) {
    items.push({
      id: `demand-${event.id}`,
      category: "user_need",
      title: event.question_text,
      sourceName: event.actor_label || event.actor_type || "真实需求记录",
      observedAt: event.captured_at || event.created_at,
      truthScope: mapTruthScope(event.truth_status, event.is_synthetic),
    });
  }

  for (const evidence of input.workspace.evidence) {
    items.push({
      id: `evidence-${evidence.id}`,
      category: classifyEvidenceCategory(evidence.source_name),
      title: evidence.claim,
      sourceName: evidence.source_name || "真实输入记录",
      observedAt: evidence.created_at,
      truthScope: mapTruthScope(evidence.truth_status, evidence.is_synthetic),
    });
  }

  for (const unknown of input.workspace.unknown) {
    items.push({
      id: `unknown-${unknown}`,
      category: "research",
      title: `认知缺口：${unknown}`,
      sourceName: "World 投影",
      observedAt: null,
      truthScope: INFERRED,
    });
  }

  return items.sort((a, b) => (b.observedAt || "").localeCompare(a.observedAt || ""));
}

function classifyEvidenceCategory(sourceName: string | null): InformationCategory {
  const source = (sourceName || "").toLowerCase();
  if (source.includes("规则") || source.includes("official") || source.includes("governance")) {
    return "official";
  }
  if (source.includes("研究") || source.includes("research") || source.includes("报告")) {
    return "research";
  }
  if (source.includes("案例") || source.includes("case")) {
    return "case_method";
  }
  return "user_need";
}

export function selectNextAction(
  readiness: RealmOwnerHomeViewModel["readiness"],
  startupTasks: RealmOwnerHomeViewModel["startupTasks"],
): RealmOwnerHomeViewModel["nextAction"] {
  if (readiness.realInputs === "missing" || readiness.industryKnowledge === "missing") {
    const blockedReasons: string[] = [];
    if (readiness.realInputs === "missing") blockedReasons.push("真实输入待补齐");
    if (readiness.industryKnowledge === "missing") blockedReasons.push("行业认知未建立");
    return {
      title: DEFAULT_NEXT_ACTION.title,
      reason: DEFAULT_NEXT_ACTION.reason,
      completionCondition: DEFAULT_NEXT_ACTION.completionCondition,
      targetHref: DEFAULT_NEXT_ACTION.targetHref,
      blockedReasons,
    };
  }

  if (readiness.resourceDemand === "missing") {
    const publishTask = startupTasks.find((task) => task.id === "publish-demand");
    return {
      title: "发布首个资源需求",
      reason: "真实输入已具备，下一步是把能力缺口发布为结构化 Demand，获得带证据的候选。",
      completionCondition: "Demand Event 已创建且由域主确认",
      targetHref: "resource-demand",
      blockedReasons: publishTask?.blockedReason ? [publishTask.blockedReason] : [],
    };
  }

  if (readiness.validConnections === "missing") {
    return {
      title: "生成并确认首个匹配候选",
      reason: "资源需求已记录，但还没有可用的真实连接候选。",
      completionCondition: "至少一个候选展示理由、证据、风险与未知项",
      targetHref: "resource-demand",
      blockedReasons: [],
    };
  }

  if (readiness.validConnections === "partial") {
    return {
      title: "确认首个候选连接",
      reason: "已有候选进入 qualified/accepted，需要域主核验真实条件后再推进。",
      completionCondition: "候选在 production 范围确认并记录真实结果",
      targetHref: "resource-demand",
      blockedReasons: [],
    };
  }

  return {
    title: "解锁90天计划",
    reason: "首个真实试点与有效连接已具备，需要 SOPRun/StepRun 能力承载90天执行。",
    completionCondition: "SOPTemplate 与 SOPRun 已创建并关联真实试点",
    targetHref: null,
    blockedReasons: ["缺少 SOPRun/StepRun 接口"],
  };
}

export function validateResourceNeed(values: ResourceNeedFormValues): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!values.businessGoal.trim()) errors.businessGoal = "请填写业务目标";
  if (!values.flowStep.trim()) errors.flowStep = "请选择所在流程环节";
  if (!values.missingCapability.trim()) errors.missingCapability = "请填写缺少的能力或资源";
  return errors;
}

export function buildDemandCreateInput(
  values: ResourceNeedFormValues,
  realmId: string,
): DemandEventCreateInput {
  return {
    question_text: `${values.businessGoal.trim()}：缺少${values.missingCapability.trim()}`,
    actor_type: "realm_owner",
    scenario: [values.flowStep.trim(), values.serviceRegion.trim(), values.timeRequirement.trim()]
      .filter(Boolean)
      .join("；") || "行业启动中心",
    objective: values.businessGoal.trim(),
    pain: values.businessGoal.trim(),
    existing_solution: "",
    missing_capability: values.missingCapability.trim(),
    decision_stage: "research",
    involved_nodes: [realmId],
    mentioned_nodes: [],
    source: "realm_owner_form",
    truth_status: "observed",
  };
}

export function buildRealmContext(
  workspace: RealmWorkspaceResponse,
): RealmOwnerHomeViewModel["realm"] {
  const realmType = workspace.realm.realm_type || null;
  const lifecycle = workspace.realm.lifecycle_state || "unknown";
  return {
    id: workspace.identity.id,
    displayName: workspace.identity.name || "Realm 待确认",
    worldName: realmType ? realmTypeLabel(realmType) : null,
    trackName: lifecycleLabel(lifecycle),
    businessStage: workspace.realm.claim_status || null,
    operatingCycleLabel: "90天待解锁",
    permissions: workspace.access.controlled ? ["owner"] : ["member"],
  };
}

export function realmTypeLabel(type: string): string {
  const value = type.toLowerCase();
  if (value.includes("enterprise") || value.includes("company")) return "GEO服务域";
  if (value.includes("brand")) return "品牌域";
  return "行业验证期";
}

export function lifecycleLabel(state: string): string {
  const value = (state || "").toLowerCase();
  if (value.includes("claimed") || value.includes("approved")) return "行业验证期";
  if (value.includes("active")) return "运营期";
  if (value.includes("paused") || value.includes("blocked")) return "暂停";
  return "待确认";
}

export function buildViewModel(input: {
  workspace: RealmWorkspaceResponse;
  user: UserProfile | null;
  realmId: string;
  realmDemandEvents: DemandEventItem[];
  allCandidates: ConnectionCandidateItem[];
  candidateNames: Record<string, string>;
  snapshots: WorldStateSnapshotItem[];
  mode: MapMode;
}): RealmOwnerHomeViewModel {
  const scopedDemandEvents = input.realmDemandEvents.filter((event) =>
    isRealmScopedDemand(event, input.realmId, input.user?.id || null),
  );
  const scopedDemandIds = new Set(scopedDemandEvents.map((event) => event.id));
  const scopedCandidates = input.allCandidates.filter(
    (candidate) => candidate.demand_event_id && scopedDemandIds.has(candidate.demand_event_id),
  );
  const readinessInput: ReadinessInput = {
    identity: input.workspace.identity,
    evidence: input.workspace.evidence,
    relationships: input.workspace.relationships,
    projects: input.workspace.projects,
    assets: input.workspace.assets,
    trust: input.workspace.position.trust,
    realmDemandEvents: scopedDemandEvents,
    realmCandidates: scopedCandidates,
  };
  const readiness = computeReadiness(readinessInput);
  const startupTasks = computeStartupTasks({
    readiness,
    realmDemandEvents: scopedDemandEvents,
    realmCandidates: scopedCandidates,
  });
  const resources = buildResourceGroups({
    realmId: input.realmId,
    userId: input.user?.id || null,
    realmDemandEvents: scopedDemandEvents,
    allCandidates: scopedCandidates,
    candidateNames: input.candidateNames,
  });
  const information = buildInformation({
    workspace: input.workspace,
    realmDemandEvents: scopedDemandEvents,
    realmId: input.realmId,
    userId: input.user?.id || null,
  });

  return {
    realm: buildRealmContext(input.workspace),
    readiness,
    startupTasks,
    map: buildMapView({
      mode: input.mode,
      snapshots: input.snapshots,
      ownerPosition: buildOwnerPosition(input.workspace),
    }),
    resources,
    information,
    nextAction: selectNextAction(readiness, startupTasks),
    decisions: [],
  };
}