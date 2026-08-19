import { authedFetch } from "@/lib/authFetch";

export type R2FlowStatus =
  | "awaiting_review"
  | "under_review"
  | "needs_supplement"
  | "profile_confirmed"
  | "positioning_draft"
  | "positioning_confirmed"
  | "project_created";

export interface R2Field {
  key: string;
  label: string;
  value: string;
  status: string;
  confidence: number;
  source_file?: string | null;
  notes?: string;
}

export interface R2IntakeItem {
  id: string;
  intake_code: string;
  status: string;
  flow_status: R2FlowStatus;
  profile_version?: number;
  positioning_status?: string;
  positioning_version?: number;
  project_id?: string | null;
  created_at: string | null;
  latest_analysis?: {
    analysis_json?: { fields?: R2Field[] };
  } | null;
}

export interface R2Analysis {
  id: string;
  version: number;
  status: string;
  analysis_json: {
    fields?: R2Field[];
    positioning?: {
      industry_position: Record<string, unknown>;
      business_position: Record<string, unknown>;
      conclusion: Record<string, unknown>;
      rule_version: string;
      config_hash: string;
      positioning_hash: string;
    };
  };
  summary: string | null;
  suggested_next_steps: string[];
  analysis_mode: string;
  confirmed_by?: string | null;
  confirmed_at?: string | null;
  created_at?: string | null;
  metadata_json: Record<string, unknown>;
}

export interface R2Workbench {
  id: string;
  intake_code: string;
  status: string;
  flow_status: R2FlowStatus;
  profile_version?: number;
  positioning_status?: string;
  positioning_version?: number;
  project_id?: string | null;
  created_at: string | null;
  latest_analysis?: R2Analysis | null;
  analyses: R2Analysis[];
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

export async function fetchR2Intakes(realmId: string): Promise<R2IntakeItem[]> {
  const data = await request<{ intakes?: R2IntakeItem[] }>(
    `/intakes?realm_id=${encodeURIComponent(realmId)}`,
  );
  return data.intakes || [];
}

export async function fetchR2Workbench(intakeId: string): Promise<R2Workbench> {
  return request<R2Workbench>(`/intakes/${encodeURIComponent(intakeId)}/workbench`);
}

export async function startR2Review(intakeId: string): Promise<R2Workbench> {
  return request<R2Workbench>(`/intakes/${encodeURIComponent(intakeId)}/review/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
}

export async function updateR2Profile(
  intakeId: string,
  edits: Record<string, string>,
  expectedVersion: number,
): Promise<R2Analysis> {
  return request<R2Analysis>(`/intakes/${encodeURIComponent(intakeId)}/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ edits, expected_version: expectedVersion }),
  });
}

export async function confirmR2Profile(
  intakeId: string,
  edits: Record<string, string>,
  expectedVersion: number,
): Promise<R2Workbench> {
  return request<R2Workbench>(`/intakes/${encodeURIComponent(intakeId)}/profile/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ edits, expected_version: expectedVersion }),
  });
}

export async function requestR2Supplement(intakeId: string, reason: string): Promise<R2Workbench> {
  return request<R2Workbench>(`/intakes/${encodeURIComponent(intakeId)}/supplement`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
}

export async function generateR2Positioning(intakeId: string): Promise<R2Analysis> {
  return request<R2Analysis>(`/intakes/${encodeURIComponent(intakeId)}/positioning/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
}

export async function confirmR2Positioning(
  intakeId: string,
  edits: Record<string, string>,
  expectedVersion: number,
): Promise<R2Analysis> {
  return request<R2Analysis>(`/intakes/${encodeURIComponent(intakeId)}/positioning/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ edits, expected_version: expectedVersion }),
  });
}

export async function createR2Project(
  intakeId: string,
  expectedPositionVersion: number,
): Promise<{ id: string; name: string; status: string }> {
  return request<{ id: string; name: string; status: string }>(
    `/intakes/${encodeURIComponent(intakeId)}/project`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        confirmed: true,
        expected_position_version: expectedPositionVersion,
      }),
    },
  );
}
