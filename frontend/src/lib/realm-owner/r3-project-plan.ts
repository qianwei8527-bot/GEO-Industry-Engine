import { authedFetch } from "../authFetch";

interface ApiErrorPayload {
  status: number;
  message: string;
}

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

export interface PlanTaskDraft {
  task_key: string;
  phase: string;
  title: string;
  purpose: string;
  description: string;
  expected_output: string;
  acceptance_criteria: string;
  required_materials: string[];
  owner_id: string | null;
  start_at: string | null;
  due_at: string | null;
  reminder_at: string | null;
  depends_on: string[];
  risks: string[];
  execution_mode: string;
  progress: number;
  status: string;
  truth_scope: string;
}

export interface PlanVersion {
  id: string;
  title: string;
  artifact_type: string;
  status: string;
  truth_status: string;
  version: number;
  plan_hash: string;
  content_json: {
    phases?: Array<{ phase: string; title: string }>;
    tasks?: PlanTaskDraft[];
    unknown_items?: string[];
    truth_scope?: string;
  };
  created_at: string | null;
}

export interface PlanTask extends PlanTaskDraft {
  id: string;
  task_version: number;
  reminders?: Array<{ type: string; message: string; due_at?: string; reminder_at?: string }>;
}

export interface ProjectPlanView {
  project: {
    id: string;
    project_code: string;
    name: string;
    objective: string | null;
    target_brand: string | null;
    target_audience: string | null;
    metadata_json: Record<string, unknown>;
  };
  plan_status: string;
  plan_version: number | null;
  plan_hash: string | null;
  source_type: string | null;
  source_id: string | null;
  source_version: string | null;
  positioning_version: number | null;
  positioning_hash: string | null;
  profile_version: number | null;
  config_hash: string | null;
  versions: PlanVersion[];
  draft_plan: PlanVersion["content_json"] | null;
  tasks: PlanTask[];
  reminders: Array<{ type: string; message: string; due_at?: string; reminder_at?: string }>;
  workflow_sources: Array<{
    source_id: string;
    source_type: string;
    name: string;
    description: string;
    owner_confirmed: boolean;
    truth_scope: string;
    source_version: string;
  }>;
  unknown_items: string[];
  can_edit: boolean;
  can_confirm: boolean;
  can_update_task: boolean;
  generated_at: string;
}

export async function fetchProjectPlan(projectId: string): Promise<ProjectPlanView> {
  return request<ProjectPlanView>(`/project-plans/${encodeURIComponent(projectId)}`);
}

export async function fetchPlanSources(): Promise<ProjectPlanView["workflow_sources"]> {
  const data = await request<{ workflow_sources: ProjectPlanView["workflow_sources"] }>("/project-plans/sources");
  return data.workflow_sources;
}

export async function generateProjectPlan(
  projectId: string,
  sourceType: string,
  sourceId?: string,
  template?: Record<string, unknown>,
): Promise<ProjectPlanView> {
  return request<ProjectPlanView>(`/project-plans/${encodeURIComponent(projectId)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_type: sourceType, source_id: sourceId, template }),
  });
}

export async function updateProjectPlanDraft(
  projectId: string,
  expectedVersion: number,
  plan: { tasks: PlanTaskDraft[]; phases?: Array<{ phase: string; title: string }> },
): Promise<ProjectPlanView> {
  return request<ProjectPlanView>(`/project-plans/${encodeURIComponent(projectId)}/draft`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_version: expectedVersion, plan }),
  });
}

export async function confirmProjectPlan(
  projectId: string,
  expectedVersion: number,
): Promise<ProjectPlanView> {
  return request<ProjectPlanView>(`/project-plans/${encodeURIComponent(projectId)}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed: true, expected_version: expectedVersion }),
  });
}

export async function updateProjectPlanTask(
  projectId: string,
  taskId: string,
  data: { status?: string; progress?: number; expected_version?: number; expected_task_version?: number },
): Promise<ProjectPlanView> {
  return request<ProjectPlanView>(
    `/project-plans/${encodeURIComponent(projectId)}/tasks/${encodeURIComponent(taskId)}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    },
  );
}

export async function exportProjectPlanCsv(projectId: string): Promise<string> {
  const res = await authedFetch(`/project-plans/${encodeURIComponent(projectId)}/export.csv`);
  if (!res.ok) {
    throw { status: res.status, message: "导出失败" } as ApiErrorPayload;
  }
  return res.text();
}

export function taskCanTransition(current: string, next: string): boolean {
  const allowed: Record<string, string[]> = {
    planned: ["in_progress"],
    in_progress: ["blocked", "completed"],
    blocked: ["in_progress"],
    completed: [],
  };
  return (allowed[current] || []).includes(next);
}

export function taskStatusOptions(current: string): string[] {
  return ["planned", "in_progress", "blocked", "completed"].filter(
    (option) => option === current || taskCanTransition(current, option),
  );
}

export function resolveSourceType(
  sources: Array<{ source_id: string; source_type: string }>,
  sourceId: string,
): string {
  return sources.find((source) => source.source_id === sourceId)?.source_type || "platform_seed";
}

export function planCanUpdateTask(
  canUpdate: boolean,
  planStatus: string,
  taskStatus: string,
): boolean {
  return canUpdate && planStatus !== "plan_completed" && taskStatus !== "completed";
}

export interface TaskUpdatePatch {
  status?: string;
  progress?: number;
}

export function buildTaskUpdatePayload(
  task: { status: string; progress: number; task_version: number },
  patch: TaskUpdatePatch,
  planVersion: number,
): { status?: string; progress?: number; expected_version: number; expected_task_version: number } {
  const base = { expected_version: planVersion, expected_task_version: task.task_version };
  if (patch.status === "completed") {
    return { ...base, status: "completed", progress: 100 };
  }
  if (patch.status) {
    return { ...base, status: patch.status, progress: patch.progress ?? task.progress };
  }
  if (patch.progress !== undefined) {
    return { ...base, progress: patch.progress };
  }
  return base;
}

export function canSubmitTaskUpdate(busyTaskId: string | null, taskId: string): boolean {
  return busyTaskId !== taskId;
}

export function isPlanCompleted(tasks: Array<{ status: string }>): boolean {
  return tasks.length > 0 && tasks.every((task) => task.status === "completed");
}

export function ownerDefinedTemplateValid(template: unknown): boolean {
  if (!template || typeof template !== "object") return false;
  const value = template as { phases?: unknown };
  return Array.isArray(value.phases) && value.phases.length > 0;
}
