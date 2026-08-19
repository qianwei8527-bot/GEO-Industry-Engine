import { authedFetch } from "@/lib/authFetch";

export interface SimulationLoopLatest {
  simulation: true;
  latest: {
    id: string;
    intake_code: string;
    status: string;
    source_truth_status: string;
    project_id: string | null;
    evidence_id: string | null;
    created_at: string | null;
  } | null;
}

export interface SimulationLoopResult {
  simulation: true;
  simulation_level: string;
  loop_version: string;
  intake: {
    id: string;
    intake_code: string;
    status: string;
    source_truth_status: string;
  };
  analysis: {
    id: string;
    status: string;
    field_count: number;
    unknown_count: number;
  };
  evidence: {
    id: string;
    truth_status: string;
  };
  project: {
    id: string;
    name: string;
    status: string;
    truth_status: string;
  };
  plan: {
    project_id: string;
    work_item_count: number;
    simulation: boolean;
  };
  position_conclusion: {
    claim: string;
    truth_scope: string;
    unknowns: string[];
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await authedFetch(path, init);
  if (!res.ok) {
    let message = `请求失败 (${res.status})`;
    try {
      const data = (await res.json()) as { detail?: string; message?: string };
      message = data.detail || data.message || message;
    } catch {
      // keep fallback message
    }
    throw { status: res.status, message } as { status: number; message: string };
  }
  return res.json() as Promise<T>;
}

export async function runSimulationLoop(realmId: string): Promise<SimulationLoopResult> {
  return request<SimulationLoopResult>("/simulation/loops/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ realm_id: realmId }),
  });
}

export async function fetchSimulationLoopLatest(realmId: string): Promise<SimulationLoopLatest> {
  return request<SimulationLoopLatest>(
    `/simulation/loops/latest?realm_id=${encodeURIComponent(realmId)}`,
  );
}
