"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CalendarRange,
  CheckCircle2,
  Download,
  FilePlus2,
  Loader2,
  Plus,
  RefreshCw,
  TriangleAlert,
  X,
} from "lucide-react";
import {
  confirmProjectPlan,
  exportProjectPlanCsv,
  fetchPlanSources,
  fetchProjectPlan,
  generateProjectPlan,
  updateProjectPlanDraft,
  updateProjectPlanTask,
  taskStatusOptions,
  planCanUpdateTask,
  resolveSourceType,
  buildTaskUpdatePayload,
  canSubmitTaskUpdate,
  ownerDefinedTemplateValid,
  type PlanTaskDraft,
  type ProjectPlanView,
} from "@/lib/realm-owner/r3-project-plan";
import { createIssue, fetchIssues } from "@/lib/realm-owner/r4-issue";
import ModuleState from "./module-state";
import TruthBadge from "./truth-badge";

function formatDate(iso?: string | null): string {
  if (!iso) return "未排期";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso.slice(0, 10);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export default function ProjectPlanWorkbench({
  realmId,
  projects,
}: {
  realmId: string;
  projects: Array<{ id: string; name: string; status: string }>;
}) {
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [plan, setPlan] = useState<ProjectPlanView | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [sources, setSources] = useState<ProjectPlanView["workflow_sources"]>([]);
  const [selectedSource, setSelectedSource] = useState("platform-seed-blank");
  const [generating, setGenerating] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmChecked, setConfirmChecked] = useState(false);
  const [issueTask, setIssueTask] = useState<PlanTaskDraft & { id?: string } | null>(null);
  const [issueTitle, setIssueTitle] = useState("");
  const [issueText, setIssueText] = useState("");
  const [issueScenario, setIssueScenario] = useState("");
  const [issueCounts, setIssueCounts] = useState<Record<string, number>>({});
  const [savingDraft, setSavingDraft] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);
  const [draftTasks, setDraftTasks] = useState<PlanTaskDraft[]>([]);
  const [customTemplate, setCustomTemplate] = useState("");
  const [customTemplateError, setCustomTemplateError] = useState<string | null>(null);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId) || null,
    [projects, selectedProjectId],
  );

  useEffect(() => {
    if (projects.length === 0) {
      setSelectedProjectId("");
      setPlan(null);
      return;
    }
    if (selectedProjectId && projects.some((project) => project.id === selectedProjectId)) return;
    setSelectedProjectId(projects[0].id);
  }, [projects, selectedProjectId]);

  useEffect(() => {
    void fetchPlanSources().then(setSources).catch(() => setSources([]));
  }, []);

  async function loadPlan(projectId: string) {
    if (!projectId) {
      setPlan(null);
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const next = await fetchProjectPlan(projectId);
      setPlan(next);
      setDraftTasks((next.draft_plan?.tasks as PlanTaskDraft[]) || []);
      const issues = await fetchIssues(realmId, next.project.id);
      const counts: Record<string, number> = {};
      for (const issue of issues) {
        if (issue.work_item_id) counts[issue.work_item_id] = (counts[issue.work_item_id] || 0) + 1;
      }
      setIssueCounts(counts);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "计划读取失败");
      setPlan(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPlan(selectedProjectId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId]);

  async function generate() {
    if (!selectedProject) return;
    setGenerating(true);
    setMessage(null);
    try {
      let template: Record<string, unknown> | undefined;
      const source = sources.find((item) => item.source_id === selectedSource);
      const sourceType = resolveSourceType(sources, selectedSource);
      if (selectedSource === "owner-defined") {
        if (!customTemplate.trim()) {
          setCustomTemplateError("请填写自定义模板 JSON");
          return;
        }
        try {
          template = JSON.parse(customTemplate) as Record<string, unknown>;
        } catch {
          setCustomTemplateError("自定义模板不是合法 JSON");
          return;
        }
        if (!ownerDefinedTemplateValid(template)) {
          setCustomTemplateError("自定义模板缺少非空 phases 或合法 task 结构");
          return;
        }
      }
      const next = await generateProjectPlan(selectedProject.id, sourceType, selectedSource, template);
      setPlan(next);
      setDraftTasks((next.draft_plan?.tasks as PlanTaskDraft[]) || []);
      setMessage(`${source?.name || sourceType} 草稿已生成。`);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "生成失败");
    } finally {
      setGenerating(false);
    }
  }

  function updateDraftTask(index: number, patch: Partial<PlanTaskDraft>) {
    setDraftTasks((prev) => prev.map((task, i) => (i === index ? { ...task, ...patch } : task)));
  }

  function addDraftTask() {
    setDraftTasks((prev) => [
      ...prev,
      {
        task_key: `task-${Date.now()}`,
        phase: "新阶段",
        title: "新任务",
        purpose: "",
        description: "",
        expected_output: "",
        acceptance_criteria: "",
        required_materials: [],
        owner_id: null,
        start_at: null,
        due_at: null,
        reminder_at: null,
        depends_on: [],
        risks: [],
        execution_mode: "owner_review",
        progress: 0,
        status: "planned",
        truth_scope: "inferred",
      },
    ]);
  }

  function removeDraftTask(index: number) {
    setDraftTasks((prev) => prev.filter((_, i) => i !== index));
  }

  function moveDraftTask(index: number, direction: -1 | 1) {
    setDraftTasks((prev) => {
      const next = [...prev];
      const target = index + direction;
      if (target < 0 || target >= next.length) return prev;
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  }

  async function saveDraft() {
    if (!plan) return;
    setSavingDraft(true);
    setMessage(null);
    try {
        const next = await updateProjectPlanDraft(
        plan.project.id,
        plan.plan_version || 1,
        { tasks: draftTasks, phases: plan.draft_plan?.phases || [] },
      );
      setPlan(next);
      setDraftTasks((next.draft_plan?.tasks as PlanTaskDraft[]) || []);
      setMessage("计划草稿已保存为新版本。");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "保存失败");
    } finally {
      setSavingDraft(false);
    }
  }

  async function confirmPlan() {
    if (!plan) return;
    setMessage(null);
    try {
      const next = await confirmProjectPlan(plan.project.id, plan.plan_version || 1);
      setPlan(next);
      setDraftTasks([]);
      setConfirmOpen(false);
      setConfirmChecked(false);
      setMessage("计划已确认，正式任务已生成；确认不代表 verified。");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "确认失败");
    }
  }

  async function updateTask(taskId: string, data: { status?: string; progress?: number }) {
    if (!plan) return;
    const current = plan.tasks.find((task) => task.id === taskId);
    if (!current || !canSubmitTaskUpdate(busyTaskId, taskId)) return;
    setBusyTaskId(taskId);
    setMessage(null);
    try {
      const next = await updateProjectPlanTask(
        plan.project.id,
        taskId,
        buildTaskUpdatePayload(current, data, plan.plan_version || 1),
      );
      setPlan(next);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "任务更新失败");
    } finally {
      setBusyTaskId(null);
    }
  }

  async function exportCsv() {
    if (!plan) return;
    try {
      const csv = await exportProjectPlanCsv(plan.project.id);
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${plan.project.project_code || plan.project.name}-执行计划.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "导出失败");
    }
  }

  async function recordIssue(task: PlanTaskDraft & { id?: string }) {
    if (!plan) return;
    setIssueTask(task);
    setIssueTitle("");
    setIssueText("");
    setIssueScenario("");
  }

  async function submitIssueFromTask() {
    if (!plan || !issueTask) return;
    if (!issueText.trim()) {
      setMessage("请输入问题描述");
      return;
    }
    setMessage(null);
    try {
      await createIssue({
        realm_id: realmId,
        project_id: plan.project.id,
        work_item_id: issueTask.id,
        title: issueTitle.trim() || undefined,
        original_text: issueText.trim(),
        scenario: issueScenario.trim() || undefined,
        source_type: "plan_task",
        idempotency_key: `issue-${Date.now()}`,
      });
      setIssueTask(null);
      setMessage("问题已记录，可在执行与问题页查看。");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "记录问题失败");
    }
  }

  if (projects.length === 0) {
    return (
      <section className="v106-panel p-4" aria-labelledby="project-plan-title">
        <h2 id="project-plan-title" className="text-base font-semibold text-slate-900">项目与执行计划</h2>
        <div className="mt-3">
          <ModuleState variant="empty" title="尚无真实项目" description="R2 定位确认后显式创建项目，才会出现在这里。" compact />
        </div>
      </section>
    );
  }

  return (
    <section className="v106-panel p-4" aria-labelledby="project-plan-title">
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 id="project-plan-title" className="text-base font-semibold text-slate-900">项目与执行计划</h2>
          <p className="mt-0.5 text-xs leading-5 text-slate-500">
            工作流来源由域主选择；平台只提供草稿、版本、任务和日程能力。
          </p>
        </div>
        {plan && plan.reminders.length > 0 && (
          <span className="inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-2 py-1 text-[11px] font-medium text-amber-700">
            <TriangleAlert className="h-3.5 w-3.5" aria-hidden="true" />
            {plan.reminders.length} 个提醒
          </span>
        )}
      </header>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <label className="flex min-w-0 flex-1 items-center gap-2">
          <span className="shrink-0 text-xs font-medium text-slate-600">项目</span>
          <select
            value={selectedProjectId}
            onChange={(event) => setSelectedProjectId(event.target.value)}
            className="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800"
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}（{project.status}）
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => selectedProject && void loadPlan(selectedProject.id)}
          className="inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700"
        >
          <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
          刷新
        </button>
        {plan && (
          <button
            type="button"
            onClick={() => void exportCsv()}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700"
          >
            <Download className="h-3.5 w-3.5" aria-hidden="true" />
            CSV 导出
          </button>
        )}
      </div>

      {loading && <ModuleState variant="loading" title="正在加载计划" compact />}
      {message && (
        <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">{message}</div>
      )}

      {plan && (
        <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
          <div className="space-y-3">
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="text-sm font-semibold text-slate-800">{plan.project.name}</div>
                  <div className="mt-0.5 text-[11px] text-slate-500">
                    {plan.project.project_code} · 计划 v{plan.plan_version ?? "-"} · {plan.plan_status}
                  </div>
                </div>
                <TruthBadge scope={(plan.draft_plan?.truth_scope as "inferred") || "observed"} />
              </div>
              <div className="mt-2 text-xs leading-5 text-slate-600">
                定位：{(plan.project.metadata_json?.positioning_summary as { who_we_are?: string })?.who_we_are || plan.project.target_brand || "待补充"}
              </div>
              {plan.unknown_items.length > 0 && (
                <div className="mt-2 rounded-md bg-amber-50 px-2.5 py-1.5 text-[11px] text-amber-800">
                  待补充：{plan.unknown_items.join("、")}
                </div>
              )}
            </div>

            {plan.plan_status === "project_created" && (
              <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="text-sm font-semibold text-slate-800">选择工作流来源</div>
                <select
                  value={selectedSource}
                  onChange={(event) => setSelectedSource(event.target.value)}
                  disabled={!plan.can_edit}
                  className="mt-2 w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm"
                >
                  {sources.map((source) => (
                    <option key={source.source_id} value={source.source_id}>
                      {source.name}（{source.source_type}）
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-[11px] text-slate-500">平台模板仅作草稿，truth_scope=inferred，owner_confirmed=false。</p>
                {selectedSource === "owner-defined" && (
                  <div className="mt-2">
                    <label className="block text-[11px] font-medium text-slate-500">自定义模板 JSON</label>
                    <textarea
                      value={customTemplate}
                      onChange={(event) => { setCustomTemplate(event.target.value); setCustomTemplateError(null); }}
                      disabled={!plan.can_edit}
                      rows={6}
                      placeholder='{"phases":[{"phase":"阶段一","tasks":[{"task_key":"t1","title":"任务一"}]}]}'
                      className="mt-1 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 font-mono text-[11px]"
                    />
                    {customTemplateError && <div className="mt-1 text-[11px] text-red-600">{customTemplateError}</div>}
                  </div>
                )}
                {plan.can_edit && (
                  <button
                    type="button"
                    onClick={() => void generate()}
                    disabled={generating}
                    className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-[color:var(--v106-primary)] px-3 py-2 text-xs font-semibold text-white"
                  >
                    {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : <FilePlus2 className="h-3.5 w-3.5" aria-hidden="true" />}
                    生成计划草稿
                  </button>
                )}
              </div>
            )}

            {plan.plan_status === "plan_draft" && (
              <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <div className="text-sm font-semibold text-slate-800">阶段与任务编辑器（v{plan.plan_version}）</div>
                  {plan.can_edit && (
                    <button type="button" onClick={addDraftTask} className="inline-flex items-center gap-1 rounded-md border border-slate-300 px-2 py-1 text-[11px] text-slate-600">
                      <Plus className="h-3 w-3" aria-hidden="true" />
                      新增任务
                    </button>
                  )}
                </div>
                <div className="space-y-2">
                  {draftTasks.map((task, index) => (
                    <div key={task.task_key} className="rounded-md border border-[color:var(--v106-border)] bg-slate-50 p-2">
                      <div className="flex items-center gap-2">
                        <input
                          value={task.title}
                          onChange={(event) => updateDraftTask(index, { title: event.target.value })}
                          disabled={!plan.can_edit}
                          className="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs"
                        />
                        {plan.can_edit && (
                          <>
                            <button type="button" onClick={() => moveDraftTask(index, -1)} className="rounded-md p-1 text-slate-400 hover:text-slate-700">↑</button>
                            <button type="button" onClick={() => moveDraftTask(index, 1)} className="rounded-md p-1 text-slate-400 hover:text-slate-700">↓</button>
                            <button type="button" onClick={() => removeDraftTask(index)} className="rounded-md p-1 text-slate-400 hover:text-red-600">
                              <X className="h-3.5 w-3.5" aria-hidden="true" />
                            </button>
                          </>
                        )}
                      </div>
                      <div className="mt-1.5 grid grid-cols-2 gap-2">
                        <input
                          type="date"
                          value={task.start_at ? task.start_at.slice(0, 10) : ""}
                          onChange={(event) => updateDraftTask(index, { start_at: event.target.value ? new Date(event.target.value).toISOString() : null })}
                          disabled={!plan.can_edit}
                          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                        />
                        <input
                          type="date"
                          value={task.due_at ? task.due_at.slice(0, 10) : ""}
                          onChange={(event) => updateDraftTask(index, { due_at: event.target.value ? new Date(event.target.value).toISOString() : null })}
                          disabled={!plan.can_edit}
                          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                        />
                        <input
                          type="date"
                          value={task.reminder_at ? task.reminder_at.slice(0, 10) : ""}
                          onChange={(event) => updateDraftTask(index, { reminder_at: event.target.value ? new Date(event.target.value).toISOString() : null })}
                          disabled={!plan.can_edit}
                          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                        />
                        <input
                          value={task.owner_id || ""}
                          onChange={(event) => updateDraftTask(index, { owner_id: event.target.value || null })}
                          placeholder="负责人 user id"
                          disabled={!plan.can_edit}
                          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                        />
                      </div>
                      <input
                        value={task.purpose || ""}
                        onChange={(event) => updateDraftTask(index, { purpose: event.target.value })}
                        placeholder="目的"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={task.description || ""}
                        onChange={(event) => updateDraftTask(index, { description: event.target.value })}
                        placeholder="说明"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={task.expected_output || ""}
                        onChange={(event) => updateDraftTask(index, { expected_output: event.target.value })}
                        placeholder="预期产出"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={task.acceptance_criteria || ""}
                        onChange={(event) => updateDraftTask(index, { acceptance_criteria: event.target.value })}
                        placeholder="验收标准"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={(task.depends_on || []).join(",")}
                        onChange={(event) => updateDraftTask(index, { depends_on: event.target.value.split(",").map((v) => v.trim()).filter(Boolean) })}
                        placeholder="依赖 task_key，逗号分隔"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={(task.required_materials || []).join(",")}
                        onChange={(event) => updateDraftTask(index, { required_materials: event.target.value.split(",").map((v) => v.trim()).filter(Boolean) })}
                        placeholder="所需材料，逗号分隔"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={(task.risks || []).join(",")}
                        onChange={(event) => updateDraftTask(index, { risks: event.target.value.split(",").map((v) => v.trim()).filter(Boolean) })}
                        placeholder="风险，逗号分隔"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <input
                        value={task.execution_mode || ""}
                        onChange={(event) => updateDraftTask(index, { execution_mode: event.target.value })}
                        placeholder="执行模式"
                        disabled={!plan.can_edit}
                        className="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                    </div>
                  ))}
                </div>
                {plan.can_edit && (
                  <button
                    type="button"
                    onClick={() => void saveDraft()}
                    disabled={savingDraft}
                    className="mt-2 inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700"
                  >
                    {savingDraft ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : null}
                    保存新版本
                  </button>
                )}
                {plan.can_confirm && (
                  <button
                    type="button"
                    onClick={() => setConfirmOpen(true)}
                    className="ml-2 inline-flex items-center gap-1.5 rounded-md bg-emerald-700 px-3 py-2 text-xs font-semibold text-white"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                    确认计划
                  </button>
                )}
              </div>
            )}

            {["plan_confirmed", "plan_active", "plan_completed"].includes(plan.plan_status) && (
              <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <div className="text-sm font-semibold text-slate-800">正式任务与日程</div>
                  <span className="text-[11px] text-slate-500">{plan.tasks.length} 个任务</span>
                </div>
                <div className="space-y-2">
                  {plan.tasks.map((task) => (
                    <div key={task.id} className="rounded-md border border-[color:var(--v106-border)] bg-slate-50 p-2">
                      <div className="flex items-center justify-between gap-2">
                        <div className="min-w-0">
                          <div className="truncate text-xs font-medium text-slate-800">{task.title}</div>
                          <div className="mt-0.5 text-[10px] text-slate-500">
                            {task.phase} · {formatDate(task.start_at)} → {formatDate(task.due_at)}
                          </div>
                        </div>
                        <select
                          value={task.status}
                          onChange={(event) => void updateTask(task.id, { status: event.target.value })}
                          disabled={!planCanUpdateTask(plan.can_update_task, plan.plan_status, task.status)}
                          className="rounded-md border border-slate-300 bg-white px-1.5 py-1 text-[11px]"
                        >
                          {taskStatusOptions(task.status).map((option) => <option key={option} value={option}>{option}</option>)}
                        </select>
                      </div>
                      <div className="mt-1.5 flex items-center gap-2">
                        <input
                          type="range"
                          min={0}
                          max={100}
                          value={task.progress}
                          onChange={(event) => void updateTask(task.id, { progress: Number(event.target.value) })}
                          disabled={!planCanUpdateTask(plan.can_update_task, plan.plan_status, task.status)}
                          className="min-w-0 flex-1"
                        />
                        <span className="w-10 text-right text-[11px] text-slate-600">{task.progress}%</span>
                        <span className="text-[10px] text-slate-400">v{task.task_version}</span>
                        {busyTaskId === task.id && <Loader2 className="h-3 w-3 animate-spin text-slate-400" aria-hidden="true" />}
                      </div>
                      {plan.can_update_task && (
                        <div className="mt-1.5 flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => void recordIssue(task)}
                            className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[10px] text-slate-600"
                          >
                            {task.status === "blocked" ? "记录/关联问题" : "记录问题"}
                          </button>
                          <span className="text-[10px] text-slate-500">{issueCounts[task.id] || 0} 个问题</span>
                          <a href={`/realm/${realmId}/execution?project_id=${plan.project.id}&work_item_id=${task.id}`} className="text-[10px] text-teal-700">查看问题</a>
                        </div>
                      )}
                      {task.reminders && task.reminders.length > 0 && (
                        <div className="mt-1 text-[10px] text-amber-700">
                          {task.reminders.map((reminder) => reminder.message).join("；")}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3">
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800">
                <CalendarRange className="h-4 w-4" aria-hidden="true" />
                计划版本与来源
              </div>
              <div className="space-y-1 text-[11px] leading-5 text-slate-600">
                <div>来源：{plan.source_type || "未生成"} · {plan.source_id || "-"}</div>
                <div>定位版本：{plan.positioning_version ?? "-"} · 档案版本：{plan.profile_version ?? "-"}</div>
                <div>config hash：{plan.config_hash || "-"}</div>
                <div className="break-all">plan hash：{plan.plan_hash || "-"}</div>
              </div>
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <div className="mb-2 text-sm font-semibold text-slate-800">版本历史</div>
              <div className="space-y-1.5">
                {plan.versions.length === 0 && <div className="text-[11px] text-slate-500">尚无版本</div>}
                {plan.versions.map((version) => (
                  <div key={version.id} className="rounded-md bg-slate-50 px-2 py-1.5 text-[11px] text-slate-600">
                    v{version.version ?? "-"} · {version.status} · {version.truth_status}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-4 shadow-xl">
            <h3 className="text-sm font-semibold text-slate-900">确认采用该计划？</h3>
            <p className="mt-1 text-xs leading-5 text-slate-600">
              确认后生成正式任务与日程。确认是域主的可观察决策，不自动升级为 verified。
            </p>
            <label className="mt-3 flex items-center gap-2 text-xs text-slate-700">
              <input type="checkbox" checked={confirmChecked} onChange={(event) => setConfirmChecked(event.target.checked)} />
              我已确认采用当前计划版本
            </label>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" onClick={() => { setConfirmOpen(false); setConfirmChecked(false); }} className="rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-600">
                取消
              </button>
              <button
                type="button"
                disabled={!confirmChecked}
                onClick={() => void confirmPlan()}
                className="rounded-md bg-emerald-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40"
              >
                确认计划
              </button>
            </div>
          </div>
        </div>
      )}

      {issueTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
          <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-4 shadow-xl">
            <h3 className="text-sm font-semibold text-slate-900">记录问题（{issueTask.title}）</h3>
            <input value={issueTitle} onChange={(event) => setIssueTitle(event.target.value)} placeholder="标题" className="mt-3 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
            <textarea value={issueText} onChange={(event) => setIssueText(event.target.value)} rows={4} placeholder="问题描述（必填）" className="mt-2 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
            <input value={issueScenario} onChange={(event) => setIssueScenario(event.target.value)} placeholder="发生场景" className="mt-2 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" onClick={() => setIssueTask(null)} className="rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-600">取消</button>
              <button type="button" onClick={() => void submitIssueFromTask()} className="rounded-md bg-teal-700 px-3 py-2 text-xs font-semibold text-white">保存问题</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
