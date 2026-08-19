import { authedFetch } from "@/lib/authFetch";

export interface AuditLogItem {
  id: string;
  actor_label: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  result: string;
  reason: string | null;
  occurred_at: string | null;
}

export interface ApprovalItem {
  id: string;
  entity_id: string;
  claim_type: string;
  status: string;
  reason: string | null;
  created_at: string | null;
}

async function request<T>(path: string): Promise<T> {
  const res = await authedFetch(path);
  if (!res.ok) {
    throw new Error(`请求失败 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function fetchAuditLogs(): Promise<{ logs: AuditLogItem[] }> {
  return request<{ logs: AuditLogItem[] }>("/admin/audit-logs?limit=50");
}

export function fetchApprovals(): Promise<{ approvals: ApprovalItem[] }> {
  return request<{ approvals: ApprovalItem[] }>("/admin/approvals?limit=50");
}
