import { authedFetch } from "@/lib/authFetch";
import type {
  AgentDraftResponse,
  ApiErrorPayload,
  ConnectionCandidateItem,
  DemandEventCreateInput,
  DemandEventItem,
  RealmAuthorizationItem,
  RealmClaimItem,
  RealmWorkspaceResponse,
  UserProfile,
  WorldStateSnapshotItem,
} from "./types";

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `请求失败 (${res.status})`;
    try {
      const data = (await res.json()) as { detail?: string; message?: string };
      message = data.detail || data.message || message;
    } catch {
      // keep fallback message
    }
    throw { status: res.status, message } as ApiErrorPayload;
  }
  return res.json() as Promise<T>;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  return parseJson<T>(await authedFetch(path, options));
}

export async function fetchCurrentUser(): Promise<UserProfile> {
  return request<UserProfile>("/auth/me");
}

export async function fetchRealmWorkspace(realmId: string): Promise<RealmWorkspaceResponse> {
  return request<RealmWorkspaceResponse>(`/realm/${encodeURIComponent(realmId)}`);
}

export async function fetchDemandEvents(limit = 200): Promise<DemandEventItem[]> {
  const data = await request<{ events?: DemandEventItem[] }>(
    `/universe/demand/events?limit=${Math.max(1, Math.min(200, limit))}`,
  );
  return data.events || [];
}

export async function fetchConnectionCandidates(limit = 500): Promise<ConnectionCandidateItem[]> {
  const data = await request<{ candidates?: ConnectionCandidateItem[] }>(
    `/universe/demand/candidates?limit=${Math.max(1, Math.min(500, limit))}`,
  );
  return data.candidates || [];
}

export async function fetchWorldSnapshots(limit = 20): Promise<WorldStateSnapshotItem[]> {
  const data = await request<{ snapshots?: WorldStateSnapshotItem[] }>(
    `/universe/world-state/snapshots?limit=${Math.max(1, Math.min(200, limit))}`,
  );
  return data.snapshots || [];
}

export async function fetchEntityName(entityId: string): Promise<string | null> {
  const id = encodeURIComponent(entityId);
  try {
    const entity = await request<{ name?: string; id?: string }>(`/entities/${id}`);
    return entity.name || entity.id || null;
  } catch {
    try {
      const company = await request<{ name?: string; id?: string }>(`/companies/${id}`);
      return company.name || company.id || null;
    } catch {
      return null;
    }
  }
}

export async function fetchRealmClaims(status = "pending"): Promise<RealmClaimItem[]> {
  const data = await request<{ claims?: RealmClaimItem[] }>(
    `/realm/claims?status=${encodeURIComponent(status)}`,
  );
  return data.claims || [];
}

export async function createDemandEvent(input: DemandEventCreateInput): Promise<DemandEventItem> {
  return request<DemandEventItem>("/universe/demand/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function generateConnectionCandidates(
  demandEventId: string,
): Promise<ConnectionCandidateItem[]> {
  const data = await request<{ candidates?: ConnectionCandidateItem[] }>(
    "/universe/demand/candidates/generate",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ demand_event_id: demandEventId }),
    },
  );
  return data.candidates || [];
}

export async function submitRealmEvidence(
  realmId: string,
  input: {
    claim: string;
    source_url: string;
    source_name?: string;
    source_type?: string;
    truth_status: "observed" | "synthetic";
  },
): Promise<unknown> {
  return request<unknown>(`/realm/${encodeURIComponent(realmId)}/evidence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function createRealmAuthorization(
  realmId: string,
  input: {
    source_name: string;
    source_type: string;
    use_scope: string;
    grantee_type: string;
    grantee_id?: string;
    valid_until?: string;
    sensitive_level?: string;
    data_scope?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
  },
): Promise<RealmAuthorizationItem> {
  return request<RealmAuthorizationItem>(`/realm/${encodeURIComponent(realmId)}/authorizations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function revokeRealmAuthorization(
  realmId: string,
  authorizationId: string,
  reason: string,
): Promise<RealmAuthorizationItem> {
  return request<RealmAuthorizationItem>(
    `/realm/${encodeURIComponent(realmId)}/authorizations/${encodeURIComponent(authorizationId)}/revoke`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    },
  );
}
export async function fetchAgentDraft(
  query: string,
  params: Record<string, string> = {},
): Promise<AgentDraftResponse> {
  return request<AgentDraftResponse>("/agent/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, params }),
  });
}
