import { authedFetch } from "@/lib/authFetch";
import type {
  AgentSummary,
  CapabilitySummary,
  McpToolSummary,
  OperationsDbStats,
  OperationsHealth,
  ProviderSummary,
  RunSummary,
  WorldSnapshotSummary,
} from "./types";

export class OperationsApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "OperationsApiError";
    this.status = status;
  }
}

async function request<T>(path: string): Promise<T> {
  const res = await authedFetch(path);
  if (res.status === 401 || res.status === 403) {
    throw new OperationsApiError(res.status, res.status === 403 ? "当前账号无权访问运营后台" : "登录状态无效");
  }
  if (!res.ok) {
    let message = `请求失败 (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: string; message?: string };
      message = body.detail || body.message || message;
    } catch {
      // keep fallback message
    }
    throw new OperationsApiError(res.status, message);
  }
  return res.json() as Promise<T>;
}

export function fetchOperationsHealth(): Promise<OperationsHealth> {
  return request<OperationsHealth>("/admin/health");
}

export function fetchOperationsDbStats(): Promise<OperationsDbStats> {
  return request<OperationsDbStats>("/admin/db-stats");
}

export function fetchOperationsConfigs(): Promise<Record<string, string[]>> {
  return request<Record<string, string[]>>("/admin/configs");
}

export async function fetchOperationsAgents(): Promise<AgentSummary[]> {
  const body = await request<{ agents: AgentSummary[] }>("/agent/list");
  return body.agents || [];
}

export async function fetchOperationsTools(): Promise<McpToolSummary[]> {
  const body = await request<{ tools: McpToolSummary[] }>("/mcp/tools");
  return body.tools || [];
}

export async function fetchOperationsProviders(): Promise<ProviderSummary[]> {
  return request<ProviderSummary[]>("/providers");
}

export async function fetchOperationsCapabilities(): Promise<CapabilitySummary[]> {
  const body = await request<{ capabilities: CapabilitySummary[] }>("/capabilities");
  return body.capabilities || [];
}

export async function fetchOperationsRuns(): Promise<RunSummary[]> {
  const body = await request<{ runs: RunSummary[] }>("/capabilities/runs");
  return body.runs || [];
}

export async function fetchOperationsSnapshots(): Promise<WorldSnapshotSummary[]> {
  const body = await request<{ snapshots: WorldSnapshotSummary[] }>("/universe/world-state/snapshots");
  return body.snapshots || [];
}
