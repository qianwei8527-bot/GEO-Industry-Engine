import { authedFetch } from "../authFetch";

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `请求失败 (${res.status})`;
    try {
      const data = (await res.json()) as { detail?: string; message?: string };
      message = data.detail || data.message || message;
    } catch {
      // keep fallback
    }
    throw { status: res.status, message } as { status: number; message: string };
  }
  return res.json() as Promise<T>;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  return parseJson<T>(await authedFetch(path, options));
}

export interface IssuePermissions {
  can_create_issue: boolean;
  can_triage: boolean;
  can_update_issue: boolean;
  can_add_attempt: boolean;
  can_resolve: boolean;
  can_verify: boolean;
  can_generate_skill: boolean;
  can_confirm_skill: boolean;
}

export interface IssueEventItem {
  id: string;
  event_version: number;
  event_type: string;
  actor_id: string | null;
  actor_label: string | null;
  content: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string | null;
}

export interface IssueItem {
  id: string;
  issue_code: string;
  realm_id: string;
  project_id: string | null;
  work_item_id: string | null;
  idempotency_key: string | null;
  original_text: string;
  title: string | null;
  scenario: string | null;
  impact: string | null;
  urgency: string | null;
  final_solution: string | null;
  applicability_boundary: string | null;
  source_type: string;
  truth_scope: string;
  category: string | null;
  severity: string;
  assignee_id: string | null;
  status: string;
  version: number;
  classification_status: string;
  ai_classification: Record<string, unknown> | null;
  events: IssueEventItem[];
  permissions: IssuePermissions;
  created_at: string | null;
  updated_at: string | null;
}

export interface SkillDraftItem {
  id: string;
  project_id: string;
  artifact_type: string;
  title: string;
  status: string;
  content_json: Record<string, unknown>;
  metadata_json: Record<string, unknown>;
  created_at: string | null;
}

export async function fetchIssues(realmId: string, projectId?: string): Promise<IssueItem[]> {
  const q = new URLSearchParams({ realm_id: realmId });
  if (projectId) q.set("project_id", projectId);
  const data = await request<{ issues: IssueItem[] }>(`/issues?${q.toString()}`);
  return data.issues;
}

export async function fetchIssue(issueId: string): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}`);
}

export async function createIssue(input: Record<string, unknown>): Promise<IssueItem> {
  return request<IssueItem>("/issues", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function updateIssue(
  issueId: string,
  data: Record<string, unknown>,
  expectedVersion: number,
): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...data, expected_version: expectedVersion }),
  });
}

export async function classifyIssue(issueId: string, expectedVersion: number): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_version: expectedVersion }),
  });
}

export async function confirmClassification(issueId: string, expectedVersion: number): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}/classification/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_version: expectedVersion }),
  });
}

export async function addIssueAttempt(
  issueId: string,
  method: string,
  expectedVersion: number,
  extra: Record<string, unknown> = {},
): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ method, expected_version: expectedVersion, ...extra }),
  });
}

export async function resolveIssue(issueId: string, expectedVersion: number): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_version: expectedVersion }),
  });
}

export async function verifyIssue(issueId: string, expectedVersion: number): Promise<IssueItem> {
  return request<IssueItem>(`/issues/${encodeURIComponent(issueId)}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_version: expectedVersion }),
  });
}

export async function generateIssueSkill(issueIds: string[]): Promise<SkillDraftItem> {
  return request<SkillDraftItem>(`/issues/${encodeURIComponent(issueIds[0])}/skills/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ issue_ids: issueIds }),
  });
}

export async function fetchSkillDrafts(realmId: string, projectId?: string): Promise<SkillDraftItem[]> {
  const q = new URLSearchParams({ realm_id: realmId });
  if (projectId) q.set("project_id", projectId);
  const data = await request<{ skills: SkillDraftItem[] }>(`/issues/skills?${q.toString()}`);
  return data.skills;
}

export async function fetchRealmMembers(realmId: string): Promise<Array<{ id: string; name: string; email: string }>> {
  const data = await request<{ members: Array<{ id: string; name: string; email: string }> }>(
    `/issues/members/${encodeURIComponent(realmId)}`,
  );
  return data.members;
}

export async function fetchSkillDraft(artifactId: string): Promise<SkillDraftItem> {
  return request<SkillDraftItem>(`/issues/skills/${encodeURIComponent(artifactId)}`);
}

export async function updateSkillDraft(
  artifactId: string,
  edits: Record<string, unknown>,
  expectedVersion: number,
): Promise<SkillDraftItem> {
  return request<SkillDraftItem>(`/issues/skills/${encodeURIComponent(artifactId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ edits, expected_version: expectedVersion }),
  });
}

export async function confirmSkillDraft(artifactId: string, confirmed: boolean): Promise<SkillDraftItem> {
  return request<SkillDraftItem>(`/issues/skills/${encodeURIComponent(artifactId)}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed }),
  });
}

export function canShowSkillButton(status: string, canGenerateSkill: boolean): boolean {
  return status === "verified" && canGenerateSkill;
}

export function isTerminalIssue(status: string): boolean {
  return status === "verified" || status === "cancelled";
}

export function classificationNeedsConfirm(status: string): boolean {
  return status === "suggested";
}
