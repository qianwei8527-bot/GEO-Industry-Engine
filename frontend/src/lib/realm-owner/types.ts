export type TruthScope = "verified" | "observed" | "inferred" | "simulation" | "unknown";

export type ReadinessStatus =
  | "unknown"
  | "missing"
  | "partial"
  | "ready"
  | "blocked"
  | "stale";

export type StartupTaskStatus =
  | "locked"
  | "ready"
  | "in_progress"
  | "blocked"
  | "needs_review"
  | "completed";

export type MapMode = "business_flow" | "demand_solution" | "resource_map";

export type ResourceGroupType = "expert" | "channel" | "delivery_partner";

export type InformationCategory =
  | "official"
  | "research"
  | "user_need"
  | "case_method";

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface RealmOwnerHomeViewModel {
  realm: {
    id: string;
    displayName: string;
    worldName: string | null;
    trackName: string | null;
    businessStage: string | null;
    operatingCycleLabel: string | null;
    permissions: string[];
  };
  readiness: {
    realInputs: ReadinessStatus;
    industryKnowledge: ReadinessStatus;
    resourceDemand: ReadinessStatus;
    validConnections: ReadinessStatus;
  };
  startupTasks: Array<{
    id: string;
    title: string;
    status: StartupTaskStatus;
    blockedReason: string | null;
    targetHref: string | null;
  }>;
  map: {
    mode: MapMode;
    nodes: Array<{
      id: string;
      label: string;
      truthScope: TruthScope;
      isTemplate: boolean;
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      truthScope: TruthScope;
    }>;
    ownerPosition: {
      status: "unknown" | "draft" | "confirmed";
      nodeIds: string[];
    };
    dataSourceLabel: string;
    snapshotId: string | null;
  };
  resources: {
    hasDemand: boolean;
    groups: Array<{
      type: ResourceGroupType;
      candidates: Array<{
        id: string;
        name: string;
        reason: string;
        truthScope: TruthScope;
        risk: string | null;
        unknowns: string[];
        connectionStatus: string;
        evidenceCounts: {
          verified: number;
          observed: number;
          synthetic: number;
        };
      }>;
    }>;
  };
  information: Array<{
    id: string;
    category: InformationCategory;
    title: string;
    sourceName: string;
    observedAt: string | null;
    truthScope: TruthScope;
  }>;
  nextAction: {
    title: string;
    reason: string;
    completionCondition: string;
    targetHref: string | null;
    blockedReasons: string[];
  };
  decisions: Array<{
    id: string;
    title: string;
    status: "pending" | "needs_review" | "blocked";
    detail: string;
  }>;
}

export interface RealmWorkspaceResponse {
  identity: {
    id: string;
    name: string;
    entity_type: string;
    description: string | null;
    geo_id: string | null;
    is_verified: boolean;
  };
  realm: {
    id: string | null;
    realm_code: string | null;
    realm_type: string | null;
    lifecycle_state: string;
    claim_status: string;
    owner_id: string | null;
  };
  access: {
    controlled: boolean;
    can_import: boolean;
    can_create_project: boolean;
    can_verify: boolean;
  };
  position: {
    trust: {
      verified_evidence: number;
      observed_evidence: number;
      synthetic_evidence: number;
      verified_claims: number;
    };
  };
  evidence: RealmEvidenceItem[];
  relationships: RealmRelationshipItem[];
  projects: RealmProjectCard[];
  assets: RealmAssetItem[];
  authorizations: RealmAuthorizationItem[];
  timeline: RealmTimelineItem[];
  unknown: string[];
}

export interface RealmEvidenceItem {
  id: string;
  entity_id: string;
  claim: string;
  source_url: string | null;
  source_name: string | null;
  truth_status: string;
  is_synthetic: boolean;
  may_affect_real_metrics: boolean;
  created_at: string | null;
}

export interface RealmRelationshipItem {
  id: string;
  source_id: string | null;
  target_id: string | null;
  relation_type: string;
  weight: number;
  description: string | null;
  created_at: string | null;
}

export interface RealmProjectCard {
  id: string;
  project_code: string;
  name: string;
  status: string;
  lifecycle_state: string;
  truth_status: string;
  created_at: string | null;
}

export interface RealmAssetItem {
  id: string;
  entity_id: string;
  asset_type: string | null;
  asset_key: string | null;
  title: string;
  description: string | null;
  source_ref: string | null;
  truth_status: string;
  may_affect_real_metrics: boolean;
  created_at: string | null;
}

export interface RealmAuthorizationItem {
  id: string;
  authorization_code?: string;
  authorization_code_masked?: string;
  source_name: string | null;
  source_url: string | null;
  use_scope: string;
  truth_status: string;
  status: string;
  created_at: string | null;
}

export interface RealmTimelineItem {
  type: string;
  label: string;
  at: string;
  truth_status: string;
}

export interface RealmClaimItem {
  claim_id: string;
  entity_id: string;
  entity_name: string;
  entity_type: string;
  claimant_id: string;
  status: string;
  reason: string | null;
  created_at: string | null;
}

export interface DemandEventItem {
  id: string;
  event_id: string;
  actor_id: string | null;
  actor_type: string;
  actor_label: string | null;
  scenario: string;
  question_text: string;
  objective: string | null;
  pain: string | null;
  existing_solution: string | null;
  missing_capability: string;
  decision_stage: string;
  involved_nodes: string[];
  mentioned_nodes: string[];
  matched_node_ids: string[];
  outcome: string;
  impact_level: string;
  priority: number;
  source: string;
  truth_status: string;
  is_synthetic: boolean;
  may_affect_real_metrics: boolean;
  captured_at: string | null;
  created_at: string | null;
}

export interface DemandEventCreateInput {
  question_text: string;
  actor_type: string;
  scenario: string;
  objective: string;
  pain: string;
  existing_solution: string;
  missing_capability: string;
  decision_stage: string;
  involved_nodes: string[];
  mentioned_nodes: string[];
  source: string;
  truth_status: "observed" | "pending_review" | "verified" | "synthetic";
}

export interface ConnectionCandidateItem {
  id: string;
  candidate_id: string;
  demand_event_id: string;
  source_node_id: string | null;
  target_node_id: string;
  connection_type: string;
  matched_capabilities: string[];
  evidence_ids: string[];
  verified_evidence_count: number;
  observed_evidence_count: number;
  synthetic_evidence_count: number;
  capability_score: number;
  evidence_score: number;
  reputation_score: number;
  trust_score: number;
  connection_score: number;
  explanation: string | null;
  truth_status: string;
  status: string;
  decision_scope: string;
  may_affect_real_metrics: boolean;
  outcome: string;
  decided_by: string | null;
  decision_reason: string | null;
  decided_at: string | null;
  created_at: string | null;
}

export interface WorldStateSnapshotItem {
  id: string;
  snapshot_id: string;
  world_code: string;
  world_version: string;
  state_scope: string;
  is_stale: boolean;
  generated_at: string | null;
}

export interface AgentDraftResponse {
  agent: string;
  intent: string;
  confidence: number;
  success: boolean;
  data: unknown;
  summary: string;
  tool_calls: unknown[];
  citations: unknown[];
  error: string | null;
}

export interface ResourceNeedFormValues {
  businessGoal: string;
  flowStep: string;
  missingCapability: string;
  serviceRegion: string;
  timeRequirement: string;
  budgetRange: string;
  cooperationMode: string;
  requiredConditions: string;
  excludedConditions: string;
  sharedDataScope: string;
}

export interface ApiErrorPayload {
  status: number;
  message: string;
}

export interface IntakeFileItem {
  file_id: string;
  file_name: string;
  ext: string;
  content_type: string;
  size: number;
  sha256: string;
  parse_status: string;
  parse_error: string | null;
  extracted_text?: string;
  snippet?: string;
}

export interface IntakeField {
  key: string;
  label: string;
  value: string;
  status: 'observed' | 'inferred' | 'unknown';
  confidence: number;
  source_file: string | null;
  source_snippet: string | null;
  notes: string;
}

export interface IntakeAnalysisItem {
  id: string;
  intake_id: string;
  realm_id: string;
  version: number;
  status: string;
  analysis_json: {
    fields: IntakeField[];
    summary?: string;
    suggested_next_steps?: string[];
    generated_at?: string;
  } | null;
  summary: string | null;
  suggested_next_steps: string[];
  analysis_mode: string;
  model_name: string | null;
  created_by: string | null;
  confirmed_by: string | null;
  confirmed_at: string | null;
  created_at: string | null;
}

export interface IntakeItem {
  id: string;
  intake_code: string;
  realm_id: string;
  realm_entity_id: string | null;
  status: string;
  relationship: string | null;
  pasted_text: string | null;
  supplemental_notes: string | null;
  file_manifest: IntakeFileItem[];
  source_truth_status: string;
  created_by: string | null;
  confirmed_by: string | null;
  confirmed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  latest_analysis?: IntakeAnalysisItem | null;
  analyses?: IntakeAnalysisItem[];
}

export interface WorkPlanItem {
  id: string;
  project_id: string;
  work_type: string;
  title: string;
  description: string | null;
  status: string;
  phase: string | null;
  purpose: string | null;
  reason: string | null;
  owner_id: string | null;
  owner_label: string | null;
  start_at: string | null;
  due_at: string | null;
  depends_on: string[];
  acceptance_criteria: string | null;
  required_materials: string[];
  evidence_ids: string[];
  risks: string[];
  reminder_at: string | null;
  execution_mode: string | null;
  progress: number;
  completion_note: string | null;
  last_synced_source: string | null;
  last_synced_at: string | null;
  truth_status: string;
  created_at: string | null;
  reminders?: Array<{
    type: string;
    message: string;
    due_at?: string;
    reminder_at?: string;
  }>;
}

export interface ExecutionPlanView {
  project: {
    id: string;
    project_code: string;
    name: string;
    status: string;
    lifecycle_state: string;
    truth_status: string;
    created_at: string | null;
  };
  work_items: WorkPlanItem[];
  reminders: Array<{
    type: string;
    message: string;
    due_at?: string;
    reminder_at?: string;
  }>;
  message?: string;
  generated_at?: string;
}

export interface GeoProjectSummary {
  id: string;
  project_code: string;
  realm_id: string;
  realm_entity_id: string | null;
  name: string;
  objective: string | null;
  target_brand: string | null;
  target_product: string | null;
  target_audience: string | null;
  scenario: string | null;
  problems: string[];
  ai_platforms: string[];
  question_set: string[];
  competitors: string[];
  expected_outcome: string | null;
  lifecycle_state: string;
  status: string;
  truth_status: string;
  may_affect_real_metrics: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface IssueEventItem {
  id: string;
  issue_id: string;
  event_type: string;
  actor_id: string | null;
  actor_label: string | null;
  content: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string | null;
}

export interface IssueRecordItem {
  id: string;
  issue_code: string;
  realm_id: string;
  project_id: string | null;
  work_item_id: string | null;
  original_text: string;
  title: string | null;
  client_ref: string | null;
  scenario: string | null;
  source: string;
  category: string | null;
  severity: string;
  status: string;
  possible_causes: string | null;
  tried_methods: string[];
  effective_methods: string[];
  ineffective_methods: string[];
  final_solution: string | null;
  evidence_ids: string[];
  applicability_boundary: string | null;
  assignee_id: string | null;
  due_at: string | null;
  recurrence_count: number;
  is_template_candidate: boolean;
  template_status: string;
  ai_classification: {
    category?: string;
    confidence?: number;
    reason?: string;
    classified_by?: string;
    classified_at?: string;
  } | null;
  created_by: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  archived_by: string | null;
  archived_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  events: IssueEventItem[];
}

export interface IssueCreateInput {
  realm_id: string;
  original_text: string;
  title?: string;
  project_id?: string;
  work_item_id?: string;
  scenario?: string;
  source?: string;
  severity?: string;
}
