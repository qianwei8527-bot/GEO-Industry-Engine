import { authedFetch } from '@/lib/authFetch';
import type {
  ApiErrorPayload,
  ExecutionPlanView,
  GeoProjectSummary,
  IntakeItem,
  IssueCreateInput,
  IssueRecordItem,
  WorkPlanItem,
} from './types';

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

export async function fetchIntakes(realmId: string): Promise<IntakeItem[]> {
  const data = await request<{ intakes?: IntakeItem[] }>(
    `/intakes?realm_id=${encodeURIComponent(realmId)}`,
  );
  return data.intakes || [];
}

export async function createIntake(form: FormData): Promise<IntakeItem> {
  return request<IntakeItem>('/intakes', {
    method: 'POST',
    body: form,
  });
}

export async function fetchIntake(intakeId: string): Promise<IntakeItem> {
  return request<IntakeItem>(`/intakes/${encodeURIComponent(intakeId)}`);
}

export async function analyzeIntake(intakeId: string): Promise<IntakeItem> {
  return request<IntakeItem>(`/intakes/${encodeURIComponent(intakeId)}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
}

export async function confirmIntake(
  intakeId: string,
  edits: Record<string, string>,
): Promise<IntakeItem> {
  return request<IntakeItem>(`/intakes/${encodeURIComponent(intakeId)}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edits }),
  });
}

export async function requestIntakeChanges(
  intakeId: string,
  reason: string,
): Promise<IntakeItem> {
  return request<IntakeItem>(`/intakes/${encodeURIComponent(intakeId)}/request-changes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
}

export async function fetchExecutionPlan(projectId: string): Promise<ExecutionPlanView> {
  return request<ExecutionPlanView>(
    `/execution/projects/${encodeURIComponent(projectId)}/plan`,
  );
}

export async function createGeoProject(
  realmId: string,
  input: {
    name: string;
    objective?: string;
    target_brand?: string;
    target_product?: string;
    target_audience?: string;
  },
): Promise<{ id: string; name: string; status: string }> {
  return request<{ id: string; name: string; status: string }>('/geo-projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ realm_id: realmId, ...input }),
  });
}

export async function fetchGeoProjects(realmId: string): Promise<GeoProjectSummary[]> {
  const data = await request<{ projects?: GeoProjectSummary[] }>(
    `/geo-projects?realm_id=${encodeURIComponent(realmId)}`,
  );
  return data.projects || [];
}

export async function generateExecutionPlan(
  projectId: string,
  replaceExisting = false,
): Promise<ExecutionPlanView> {
  return request<ExecutionPlanView>(
    `/execution/projects/${encodeURIComponent(projectId)}/plan/generate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ replace_existing: replaceExisting }),
    },
  );
}

export async function updateWorkItem(
  projectId: string,
  workItemId: string,
  data: Record<string, unknown>,
): Promise<WorkPlanItem> {
  return request<WorkPlanItem>(
    `/execution/projects/${encodeURIComponent(projectId)}/work-items/${encodeURIComponent(workItemId)}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    },
  );
}

export async function syncWorkItem(
  projectId: string,
  workItemId: string,
  data: Record<string, unknown>,
): Promise<WorkPlanItem> {
  return request<WorkPlanItem>(
    `/execution/projects/${encodeURIComponent(projectId)}/work-items/${encodeURIComponent(workItemId)}/sync`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    },
  );
}

export async function exportExecutionPlan(projectId: string): Promise<string> {
  const res = await authedFetch(
    `/execution/projects/${encodeURIComponent(projectId)}/plan/export`,
  );
  if (!res.ok) {
    let message = `导出失败 (${res.status})`;
    try {
      const data = (await res.json()) as { detail?: string; message?: string };
      message = data.detail || data.message || message;
    } catch {
      // keep fallback message
    }
    throw { status: res.status, message } as ApiErrorPayload;
  }
  return res.text();
}

export async function fetchIssues(
  realmId: string,
  params: { project_id?: string; status?: string } = {},
): Promise<IssueRecordItem[]> {
  const query = new URLSearchParams({ realm_id: realmId });
  if (params.project_id) query.set('project_id', params.project_id);
  if (params.status) query.set('status', params.status);
  const data = await request<{ issues?: IssueRecordItem[] }>(`/issues?${query.toString()}`);
  return data.issues || [];
}

export async function createIssue(input: IssueCreateInput): Promise<IssueRecordItem> {
  return request<IssueRecordItem>('/issues', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
}

export async function fetchIssue(issueId: string): Promise<IssueRecordItem> {
  return request<IssueRecordItem>(`/issues/${encodeURIComponent(issueId)}`);
}

export async function updateIssue(
  issueId: string,
  data: Record<string, unknown>,
): Promise<IssueRecordItem> {
  return request<IssueRecordItem>(`/issues/${encodeURIComponent(issueId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function classifyIssue(issueId: string): Promise<IssueRecordItem> {
  return request<IssueRecordItem>(`/issues/${encodeURIComponent(issueId)}/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
}

export async function confirmIssueTemplate(
  issueId: string,
  confirmed: boolean,
): Promise<IssueRecordItem> {
  return request<IssueRecordItem>(`/issues/${encodeURIComponent(issueId)}/template`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirmed }),
  });
}

export async function linkIssueEvidence(
  issueId: string,
  evidenceIds: string[],
): Promise<IssueRecordItem> {
  return request<IssueRecordItem>(`/issues/${encodeURIComponent(issueId)}/evidence`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ evidence_ids: evidenceIds }),
  });
}
