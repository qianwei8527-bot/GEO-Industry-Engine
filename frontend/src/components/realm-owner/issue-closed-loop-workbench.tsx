"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  FilePlus2,
  Loader2,
  Plus,
  RefreshCw,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import {
  canShowSkillButton,
  addIssueAttempt,
  classifyIssue,
  confirmClassification,
  confirmSkillDraft,
  createIssue,
  fetchIssue,
  fetchIssues,
  fetchSkillDrafts,
  fetchSkillDraft,
  fetchRealmMembers,
  generateIssueSkill,
  resolveIssue,
  updateIssue,
  updateSkillDraft,
  verifyIssue,
  type IssueItem,
  type SkillDraftItem,
} from "@/lib/realm-owner/r4-issue";
import ModuleState from "./module-state";

export default function IssueClosedLoopWorkbench({
  realmId,
  canWrite,
  projects,
}: {
  realmId: string;
  canWrite: boolean;
  projects: Array<{ id: string; name: string }>;
}) {
  const [issues, setIssues] = useState<IssueItem[]>([]);
  const [selected, setSelected] = useState<IssueItem | null>(null);
  const [skills, setSkills] = useState<SkillDraftItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [originalText, setOriginalText] = useState("");
  const [scenario, setScenario] = useState("");
  const [projectId, setProjectId] = useState("");
  const [attemptText, setAttemptText] = useState("");
  const [category, setCategory] = useState("");
  const [severity, setSeverity] = useState("normal");
  const [impact, setImpact] = useState("");
  const [urgency, setUrgency] = useState("normal");
  const [assignee, setAssignee] = useState("");
  const [attemptResult, setAttemptResult] = useState("failed");
  const [attemptTool, setAttemptTool] = useState("");
  const [attemptFailure, setAttemptFailure] = useState("");
  const [attemptEvidence, setAttemptEvidence] = useState("");
  const [skillEdit, setSkillEdit] = useState("");
  const [skillName, setSkillName] = useState("");
  const [skillProhibited, setSkillProhibited] = useState("");
  const [skillValidation, setSkillValidation] = useState("");
  const [members, setMembers] = useState<Array<{ id: string; name: string; email: string }>>([]);
  const [finalSolution, setFinalSolution] = useState("");
  const [applicabilityBoundary, setApplicabilityBoundary] = useState("");
  const [attemptAction, setAttemptAction] = useState("");
  const [attemptStartedAt, setAttemptStartedAt] = useState("");
  const [attemptEndedAt, setAttemptEndedAt] = useState("");

  async function load() {
    setLoading(true);
    try {
      const next = await fetchIssues(realmId);
      setIssues(next);
      setSkills(await fetchSkillDrafts(realmId));
      setMembers(await fetchRealmMembers(realmId));
      const params = new URLSearchParams(window.location.search);
      const workItemId = params.get("work_item_id");
      if (workItemId) {
        const match = next.find((issue) => issue.work_item_id === workItemId);
        if (match) setSelected(await fetchIssue(match.id));
      }
      if (selected) {
        const detail = await fetchIssue(selected.id);
        setSelected(detail);
      }
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "问题加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [realmId]);

  async function selectIssue(issue: IssueItem) {
    setBusy(true);
    try {
      setSelected(await fetchIssue(issue.id));
      setCategory(issue.category || "");
      setSeverity(issue.severity || "normal");
      setImpact(issue.impact || "");
      setUrgency(issue.urgency || "normal");
      setAssignee(issue.assignee_id || "");
      setFinalSolution(issue.final_solution || "");
      setApplicabilityBoundary(issue.applicability_boundary || "");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "详情加载失败");
    } finally {
      setBusy(false);
    }
  }

  async function submitCreate() {
    if (!originalText.trim()) {
      setMessage("请输入问题描述");
      return;
    }
    setBusy(true);
    try {
      await createIssue({
        realm_id: realmId,
        title: title.trim() || undefined,
        original_text: originalText.trim(),
        scenario: scenario.trim() || undefined,
        project_id: projectId || undefined,
        source_type: "owner_manual",
        idempotency_key: `issue-${Date.now()}`,
      });
      setTitle("");
      setOriginalText("");
      setScenario("");
      setProjectId("");
      setFormOpen(false);
      await load();
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "创建失败");
    } finally {
      setBusy(false);
    }
  }

  async function run(method: () => Promise<IssueItem>, success: string) {
    if (!selected) return;
    setBusy(true);
    setMessage(null);
    try {
      const next = await method();
      setSelected(next);
      setIssues(await fetchIssues(realmId));
      setMessage(success);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "操作失败");
    } finally {
      setBusy(false);
    }
  }

  async function addAttempt() {
    if (!selected || !attemptText.trim()) return;
    const method = attemptText.trim();
    setAttemptText("");
    await run(
      () => addIssueAttempt(selected.id, method, selected.version, {
        result: attemptResult,
        tool: attemptTool || undefined,
        action: attemptAction || undefined,
        started_at: attemptStartedAt || undefined,
        ended_at: attemptEndedAt || undefined,
        failure_reason: attemptFailure || undefined,
        evidence_refs: attemptEvidence ? attemptEvidence.split(",").map((v) => v.trim()).filter(Boolean) : [],
      }),
      "处理尝试已追加",
    );
    setAttemptResult("failed");
    setAttemptTool("");
    setAttemptFailure("");
    setAttemptEvidence("");
    setAttemptAction("");
    setAttemptStartedAt("");
    setAttemptEndedAt("");
  }

  async function saveFields() {
    if (!selected) return;
    await run(
      () => updateIssue(selected.id, {
        category: category || undefined,
        severity,
        impact: impact || undefined,
        urgency,
        assignee_id: assignee || undefined,
        final_solution: finalSolution || undefined,
        applicability_boundary: applicabilityBoundary || undefined,
      }, selected.version),
      "问题字段已保存",
    );
  }

  async function confirmClassificationNow() {
    if (!selected) return;
    await run(() => confirmClassification(selected.id, selected.version), "分类已确认");
  }

  async function generateSkill() {
    if (!selected) return;
    setBusy(true);
    try {
      const skill = await generateIssueSkill([selected.id]);
      setSkills([skill, ...skills]);
      setMessage("Skill 草稿已生成，等待域主确认");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "Skill 生成失败");
    } finally {
      setBusy(false);
    }
  }

  async function confirmSkill(skill: SkillDraftItem, confirmed: boolean) {
    setBusy(true);
    try {
      const next = await confirmSkillDraft(skill.id, confirmed);
      setSkills((prev) => prev.map((item) => (item.id === next.id ? next : item)));
      setMessage(confirmed ? "Skill 草稿已确认沉淀" : "Skill 草稿已拒绝");
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || "Skill 确认失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="v106-panel p-4" aria-labelledby="issue-closed-loop-title">
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 id="issue-closed-loop-title" className="text-base font-semibold text-slate-900">执行与问题闭环</h2>
          <p className="mt-0.5 text-xs leading-5 text-slate-500">AI/规则只给分类建议；处理、验证和 Skill 沉淀必须由域主确认。</p>
        </div>
        {canWrite && (
          <button
            type="button"
            onClick={() => setFormOpen((open) => !open)}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700"
          >
            {formOpen ? <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" /> : <FilePlus2 className="h-3.5 w-3.5" aria-hidden="true" />}
            {formOpen ? "收起录入" : "录入问题"}
          </button>
        )}
      </header>

      {message && (
        <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">{message}</div>
      )}

      {formOpen && canWrite && (
        <div className="mt-3 rounded-md border border-slate-200 bg-white p-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="标题" className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm" />
            <select value={projectId} onChange={(event) => setProjectId(event.target.value)} className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm">
              <option value="">不关联项目</option>
              {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
            </select>
          </div>
          <textarea
            value={originalText}
            onChange={(event) => setOriginalText(event.target.value)}
            rows={3}
            placeholder="问题描述（必填）"
            className="mt-2 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"
          />
          <input value={scenario} onChange={(event) => setScenario(event.target.value)} placeholder="发生场景" className="mt-2 w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm" />
          <button
            type="button"
            onClick={() => void submitCreate()}
            disabled={busy}
            className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-teal-700 px-3 py-2 text-xs font-semibold text-white"
          >
            {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : <Plus className="h-3.5 w-3.5" aria-hidden="true" />}
            保存问题
          </button>
        </div>
      )}

      {loading ? (
        <ModuleState variant="loading" title="正在加载问题" compact />
      ) : (
        <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
          <div className="space-y-2">
            <div className="mb-1 text-xs font-semibold text-slate-600">问题列表</div>
            {issues.length === 0 && <ModuleState variant="empty" title="尚无问题" description="从执行计划任务或本页录入问题。" compact />}
            {issues.map((issue) => (
              <button
                key={issue.id}
                type="button"
                onClick={() => void selectIssue(issue)}
                className={`w-full rounded-md border p-3 text-left ${selected?.id === issue.id ? "border-teal-600 bg-teal-50" : "border-slate-200 bg-white"}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="min-w-0 truncate text-sm font-medium text-slate-800">{issue.title || issue.original_text}</span>
                  <span className="shrink-0 rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-600">{issue.status} v{issue.version}</span>
                </div>
                <div className="mt-1 text-[11px] text-slate-500">{issue.category || "待分类"} · {issue.issue_code}</div>
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {!selected ? (
              <ModuleState variant="empty" title="选择问题查看详情" description="分类建议、处理尝试和 Skill 草稿会显示在这里。" compact />
            ) : (
              <>
                <div className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <div className="text-sm font-semibold text-slate-800">{selected.title || selected.original_text}</div>
                      <div className="mt-0.5 text-[11px] text-slate-500">{selected.issue_code} · {selected.status} · v{selected.version}</div>
                    </div>
                    {selected.permissions.can_resolve && (
                      <button type="button" onClick={() => void run(() => resolveIssue(selected.id, selected.version), "问题已解决")} className="rounded-md bg-emerald-700 px-2 py-1 text-[11px] font-semibold text-white">
                        解决
                      </button>
                    )}
                    {selected.permissions.can_verify && (
                      <button type="button" onClick={() => void run(() => verifyIssue(selected.id, selected.version), "问题已验证")} className="rounded-md bg-blue-700 px-2 py-1 text-[11px] font-semibold text-white">
                        验证
                      </button>
                    )}
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-600">{selected.original_text}</p>
                  {selected.permissions.can_update_issue && (
                    <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                      <input value={category} onChange={(event) => setCategory(event.target.value)} placeholder="分类" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                      <select value={severity} onChange={(event) => setSeverity(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]">
                        <option value="low">low</option><option value="normal">normal</option><option value="high">high</option><option value="critical">critical</option>
                      </select>
                      <input value={impact} onChange={(event) => setImpact(event.target.value)} placeholder="影响" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                      <select value={urgency} onChange={(event) => setUrgency(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]">
                        <option value="low">low</option><option value="normal">normal</option><option value="high">high</option>
                      </select>
                      <select value={assignee} onChange={(event) => setAssignee(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]">
                        <option value="">不指定负责人</option>
                        {members.map((member) => <option key={member.id} value={member.id}>{member.name}（{member.email}）</option>)}
                      </select>
                      <input value={finalSolution} onChange={(event) => setFinalSolution(event.target.value)} placeholder="最终方案" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                      <input value={applicabilityBoundary} onChange={(event) => setApplicabilityBoundary(event.target.value)} placeholder="适用边界" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                    </div>
                  )}
                  {selected.ai_classification && (
                    <div className="mt-2 rounded-md bg-amber-50 px-2 py-1.5 text-[11px] text-amber-800">
                      规则建议：{(selected.ai_classification as { category?: string }).category || "其他"} · engine=rule_based · truth_scope=inferred
                      {selected.classification_status !== "confirmed" && selected.permissions.can_update_issue && (
                        <button type="button" onClick={() => void confirmClassificationNow()} className="ml-2 rounded bg-teal-600 px-1.5 py-0.5 text-white">确认分类</button>
                      )}
                    </div>
                  )}
                  {selected.permissions.can_update_issue && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      <button type="button" onClick={() => void run(() => updateIssue(selected.id, { status: "triaged" }, selected.version), "已进入 triaged")} disabled={busy || !selected.permissions.can_triage} className="rounded-md border border-slate-300 px-2 py-1 text-[11px] disabled:opacity-40">triaged</button>
                      <button type="button" onClick={() => void run(() => updateIssue(selected.id, { status: "in_progress" }, selected.version), "已进入 in_progress")} disabled={busy} className="rounded-md border border-slate-300 px-2 py-1 text-[11px] disabled:opacity-40">in_progress</button>
                      <button type="button" onClick={() => void saveFields()} disabled={busy} className="rounded-md border border-slate-300 px-2 py-1 text-[11px] disabled:opacity-40">保存字段</button>
                      <button type="button" onClick={() => void run(() => classifyIssue(selected.id, selected.version), "已重新生成规则建议")} disabled={busy} className="rounded-md border border-slate-300 px-2 py-1 text-[11px] disabled:opacity-40">重新分类</button>
                    </div>
                  )}
                  {canShowSkillButton(selected.status, selected.permissions.can_generate_skill) && (
                    <button type="button" onClick={() => void generateSkill()} disabled={busy} className="mt-2 inline-flex items-center gap-1 rounded-md bg-purple-700 px-2 py-1 text-[11px] font-semibold text-white disabled:opacity-40">
                      <Sparkles className="h-3 w-3" aria-hidden="true" />
                      生成 Skill 草稿
                    </button>
                  )}
                </div>

                <div className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="mb-2 text-xs font-semibold text-slate-600">处理尝试与历史</div>
                  {selected.events.length === 0 && <div className="text-[11px] text-slate-500">暂无历史</div>}
                  <div className="space-y-1.5">
                    {selected.events.map((event) => (
                      <div key={event.id} className="rounded-md bg-slate-50 px-2 py-1.5 text-[11px] text-slate-600">
                        #{event.event_version} {event.event_type} · {event.actor_label || "system"} · {event.content || ""}
                      </div>
                    ))}
                  </div>
                  {selected.permissions.can_add_attempt && (
                    <div className="mt-2 space-y-1.5">
                      <div className="flex gap-2">
                      <input
                        value={attemptText}
                        onChange={(event) => setAttemptText(event.target.value)}
                        placeholder="处理尝试方法"
                        className="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]"
                      />
                      <button type="button" onClick={() => void addAttempt()} disabled={busy} className="rounded-md border border-slate-300 px-2 py-1 text-[11px] disabled:opacity-40">追加尝试</button>
                      </div>
                      <div className="grid grid-cols-2 gap-1.5">
                        <select value={attemptResult} onChange={(event) => setAttemptResult(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]">
                          <option value="success">success</option><option value="partial">partial</option><option value="failed">failed</option>
                        </select>
                        <input value={attemptTool} onChange={(event) => setAttemptTool(event.target.value)} placeholder="工具" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                        <input value={attemptAction} onChange={(event) => setAttemptAction(event.target.value)} placeholder="执行动作" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                        <input type="datetime-local" value={attemptStartedAt} onChange={(event) => setAttemptStartedAt(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                        <input type="datetime-local" value={attemptEndedAt} onChange={(event) => setAttemptEndedAt(event.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                        <input value={attemptFailure} onChange={(event) => setAttemptFailure(event.target.value)} placeholder="失败原因" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                        <input value={attemptEvidence} onChange={(event) => setAttemptEvidence(event.target.value)} placeholder="证据/产物引用，逗号分隔" className="rounded-md border border-slate-300 px-2 py-1 text-[11px]" />
                      </div>
                    </div>
                  )}
                </div>

                <div className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="mb-2 text-xs font-semibold text-slate-600">业务 Skill 草稿</div>
                  {skills.length === 0 && <div className="text-[11px] text-slate-500">暂无草稿</div>}
                  <div className="space-y-1.5">
                    {skills.map((skill) => (
                      <div key={skill.id} className="rounded-md bg-slate-50 px-2 py-1.5 text-[11px] text-slate-600">
                        {skill.title} · {skill.status}
                        {skill.status === "draft" && selected.permissions.can_confirm_skill && (
                          <div className="mt-1 grid grid-cols-1 gap-1">
                            <input value={skillName} onChange={(event) => setSkillName(event.target.value)} placeholder="Skill 名称" className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]" />
                            <input value={skillEdit} onChange={(event) => setSkillEdit(event.target.value)} placeholder="预期输出" className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]" />
                            <input value={skillValidation} onChange={(event) => setSkillValidation(event.target.value)} placeholder="验证标准" className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]" />
                            <input value={skillProhibited} onChange={(event) => setSkillProhibited(event.target.value)} placeholder="禁止使用条件" className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[11px]" />
                            <button type="button" onClick={() => void updateSkillDraft(skill.id, { name: skillName || undefined, expected_output: skillEdit || undefined, validation_criteria: skillValidation || undefined, prohibited_usage: skillProhibited || undefined }, Number(skill.metadata_json.version || 1)).then((next) => { setSkills((prev) => prev.map((item) => item.id === next.id ? next : item)); setMessage("Skill 草稿已保存为新版本"); }).catch((err) => setMessage((err as { message?: string }).message || "Skill 编辑失败"))} className="rounded-md border border-slate-300 px-2 py-1">保存</button>
                          </div>
                        )}
                        {skill.status === "draft" && selected.permissions.can_confirm_skill && (
                          <span className="ml-2">
                            <button type="button" onClick={() => void confirmSkill(skill, true)} className="rounded bg-emerald-600 px-1.5 py-0.5 text-white">确认</button>
                            <button type="button" onClick={() => void confirmSkill(skill, false)} className="ml-1 rounded bg-slate-300 px-1.5 py-0.5">拒绝</button>
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
