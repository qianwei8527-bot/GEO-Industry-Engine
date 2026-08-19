export type OperationsView =
  | "overview"
  | "runtime"
  | "connectors"
  | "capabilities"
  | "workflows"
  | "reports"
  | "intelligence"
  | "system";

export type AsyncStatus = "loading" | "ready" | "ok" | "empty" | "error" | "no-permission";

export interface AsyncValue<T> {
  status: AsyncStatus;
  data: T | null;
  message?: string;
}

export interface OperationsHealth {
  status: string;
  backend?: string;
  db?: string;
  version?: string;
  timestamp?: string;
}

export interface OperationsDbStats {
  counts: Record<string, number>;
  total: number;
  timestamp: string;
}

export interface AgentSummary {
  name: string;
  description: string;
}

export interface McpToolSummary {
  name: string;
  description: string;
  params: string[];
}

export interface ProviderSummary {
  id: string;
  entity_id: string;
  provider_type: string;
  trust_score: number;
  geo_score: number;
  verification_status: string;
  is_verified: boolean;
  is_active: boolean;
  completed_orders: number;
  avg_rating: number;
  created_at: string;
}

export interface CapabilitySummary {
  capability_id: string;
  name: string;
  capability_type: string;
  source_mode: string;
  status: string;
  publisher: string | null;
  provider: string;
  tool_name: string;
  description: string | null;
  available: boolean;
  created_at: string | null;
}

export interface RunSummary {
  id: string;
  execution_code: string;
  project_id: string | null;
  realm_entity_id: string | null;
  provider: string;
  tool_name: string;
  capability_id: string;
  capability_type: string;
  source_mode: string;
  model_name: string | null;
  model_version: string | null;
  truth_status: string;
  execution_source: string;
  execution_status: string;
  cost: number | null;
  created_at: string | null;
}

export interface WorldSnapshotSummary {
  snapshot_id: string;
  world_code: string;
  world_version: string;
  state_scope: string;
  projection_as_of: string | null;
  snapshot_hash: string;
  created_at: string | null;
}

export interface OperationsDataState {
  phase: AsyncStatus;
  health: AsyncValue<OperationsHealth>;
  dbStats: AsyncValue<OperationsDbStats>;
  configs: AsyncValue<Record<string, string[]>>;
  agents: AsyncValue<AgentSummary[]>;
  tools: AsyncValue<McpToolSummary[]>;
  providers: AsyncValue<ProviderSummary[]>;
  capabilities: AsyncValue<CapabilitySummary[]>;
  runs: AsyncValue<RunSummary[]>;
  snapshots: AsyncValue<WorldSnapshotSummary[]>;
}
