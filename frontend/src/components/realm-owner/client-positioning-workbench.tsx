"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Loader2, Play, Send, Sparkles, Target } from "lucide-react";
import ModuleState from "./module-state";
import TruthBadge from "./truth-badge";
import {
  confirmR2Positioning,
  confirmR2Profile,
  createR2Project,
  fetchR2Intakes,
  fetchR2Workbench,
  generateR2Positioning,
  requestR2Supplement,
  startR2Review,
  updateR2Profile,
  type R2Field,
  type R2FlowStatus,
  type R2IntakeItem,
  type R2Workbench,
} from "@/lib/realm-owner/r2-client-positioning";

const FLOW_LABELS: Record<R2FlowStatus, string> = {
  awaiting_review: "待审核",
  under_review: "审核中",
  needs_supplement: "待补充",
  profile_confirmed: "档案已确认",
  positioning_draft: "定位草稿",
  positioning_confirmed: "定位已确认",
  project_created: "项目已创建",
};

export default function ClientPositioningWorkbench({
  realmId,
  canWrite,
}: {
  realmId: string;
  canWrite: boolean;
}) {
  const [intakes, setIntakes] = useState<R2IntakeItem[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [workbench, setWorkbench] = useState<R2Workbench | null>(null);
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");
  const [phaseMessage, setPhaseMessage] = useState("");
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [supplementReason, setSupplementReason] = useState("");
  const [confirmProject, setConfirmProject] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setPhase("loading");
    fetchR2Intakes(realmId)
      .then((data) => {
        if (cancelled) return;
        setIntakes(data);
        if (data.length > 0) {
          setSelectedId(data[0].id);
          return fetchR2Workbench(data[0].id);
        }
        setPhase("ready");
        return null;
      })
      .then((wb) => {
        if (cancelled) return;
        if (wb) setWorkbench(wb);
        setPhase("ready");
      })
      .catch(() => {
        if (!cancelled) {
          setPhase("error");
          setPhaseMessage("客户与定位数据加载失败");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [realmId]);

  const latest = workbench?.analyses?.[0] ?? workbench?.latest_analysis ?? null;
  const fields: R2Field[] = useMemo(() => latest?.analysis_json?.fields || [], [latest]);
  const unknownCount = useMemo(
    () => fields.filter((field) => field.status === "unknown" || field.value === "待补充").length,
    [fields],
  );
  const positioning = latest?.analysis_json?.positioning;
  const flow = workbench?.flow_status || "awaiting_review";
  const editable = canWrite && ["awaiting_review", "under_review", "needs_supplement", "profile_confirmed"].includes(flow);

  async function run(action: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await action();
      await refreshWorkbench();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "操作失败");
    } finally {
      setBusy(false);
    }
  }

  async function refreshWorkbench() {
    if (!selectedId) return;
    const wb = await fetchR2Workbench(selectedId);
    setWorkbench(wb);
  }

  async function selectIntake(id: string) {
    setSelectedId(id);
    setEdits({});
    setError("");
    setConfirmProject(false);
    try {
      const wb = await fetchR2Workbench(id);
      setWorkbench(wb);
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "客户加载失败");
    }
  }

  async function saveEdits() {
    if (!workbench || !latest) return;
    const nonEmpty = Object.fromEntries(
      Object.entries(edits).filter(([, value]) => value !== undefined),
    );
    await run(() => updateR2Profile(workbench.id, nonEmpty, latest.version));
    setEdits({});
  }

  async function confirmProfile() {
    if (!workbench || !latest) return;
    await run(() => confirmR2Profile(workbench.id, edits, latest.version));
    setEdits({});
  }

  async function confirmPositioning() {
    if (!workbench || !latest) return;
    await run(() => confirmR2Positioning(workbench.id, {}, latest.version));
  }

  async function createProject() {
    if (!workbench || !latest) return;
    await run(() => createR2Project(workbench.id, latest.version));
    setConfirmProject(false);
  }

  if (phase === "loading") {
    return <ModuleState variant="loading" title="正在加载客户与定位" />;
  }
  if (phase === "error") {
    return (
      <ModuleState
        variant="error"
        title="客户与定位加载失败"
        description={phaseMessage}
        actionLabel="重试"
        onAction={() => window.location.reload()}
      />
    );
  }
  if (intakes.length === 0) {
    return (
      <ModuleState
        variant="empty"
        title="尚无客户提交"
        description="客户通过公共资料提交入口提交后，会出现在这里。"
      />
    );
  }
  if (!canWrite) {
    return (
      <ModuleState
        variant="no-permission"
        title="无权限查看客户内容"
        description="需要域主或编辑权限。"
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 xl:grid-cols-[300px_minmax(0,1fr)]">
      <section className="v106-panel p-3">
        <h2 className="mb-2 text-sm font-semibold text-slate-800">客户列表</h2>
        <div className="space-y-2">
          {intakes.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => selectIntake(item.id)}
              className={`w-full rounded-md border p-3 text-left ${
                selectedId === item.id
                  ? "border-[color:var(--v106-primary)] bg-[color:var(--v106-primary-weak)]"
                  : "border-[color:var(--v106-border)] bg-white hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-slate-800">{item.intake_code}</span>
                <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-600">
                  {FLOW_LABELS[item.flow_status] || item.flow_status}
                </span>
              </div>
              <div className="mt-1 text-[11px] text-slate-500">
                {item.created_at || "--"} · 版本 {item.profile_version || 1}
              </div>
              {item.project_id && (
                <div className="mt-1 text-[11px] text-emerald-700">项目已创建</div>
              )}
            </button>
          ))}
        </div>
      </section>

      <div className="space-y-3">
        {error && (
          <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
            {error}
          </p>
        )}

        <section className="v106-panel p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-sm font-semibold text-slate-800">当前客户档案</h2>
              <p className="mt-0.5 text-xs text-slate-500">
                {workbench?.intake_code} · {FLOW_LABELS[flow]} · 版本 {latest?.version || 1}
              </p>
            </div>
            <span className="rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-700">
              待补充 {unknownCount} 项
            </span>
          </div>

          {unknownCount > 0 && (
            <div className="mt-3">
              <ModuleState
                variant="partial"
                title={`客户档案不完整：${unknownCount} 项待补充`}
                description="待补充字段不得自动补造，需由客户或域主提供。"
                compact
              />
            </div>
          )}

          <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2">
            {fields.map((field) => (
              <div key={field.key} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-slate-700">{field.label}</span>
                  <TruthBadge scope={field.status as never} />
                </div>
                {editable ? (
                  <input
                    value={edits[field.key] ?? field.value}
                    onChange={(event) =>
                      setEdits((prev) => ({ ...prev, [field.key]: event.target.value }))
                    }
                    className="v106-control mt-1.5 w-full px-2.5 py-1.5 text-sm"
                  />
                ) : (
                  <p className="mt-1.5 text-sm text-slate-800">{field.value || "待补充"}</p>
                )}
                <p className="mt-1 text-[10px] text-slate-400">
                  置信度 {Math.round((field.confidence || 0) * 100)}% · 来源 {field.source_file || "域主输入"}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {canWrite && flow === "awaiting_review" && (
              <ActionButton icon={<Play className="h-4 w-4" />} label="开始审核" busy={busy} onClick={() => run(() => startR2Review(workbench!.id))} />
            )}
            {editable && (
              <ActionButton icon={<CheckCircle2 className="h-4 w-4" />} label="保存修改" busy={busy} onClick={saveEdits} />
            )}
            {editable && (
              <ActionButton icon={<Send className="h-4 w-4" />} label="确认档案" busy={busy} onClick={confirmProfile} />
            )}
            {canWrite && ["under_review", "needs_supplement"].includes(flow) && (
              <div className="flex items-center gap-2">
                <input
                  value={supplementReason}
                  onChange={(event) => setSupplementReason(event.target.value)}
                  placeholder="补充资料说明"
                  className="v106-control w-48 px-2.5 py-1.5 text-xs"
                />
                <ActionButton
                  icon={<Send className="h-4 w-4" />}
                  label="请求补充"
                  busy={busy}
                  onClick={() => run(() => requestR2Supplement(workbench!.id, supplementReason || "请补充缺失字段"))}
                />
              </div>
            )}
          </div>
        </section>

        <section className="v106-panel p-4">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold text-slate-800">定位结论</h2>
            {workbench?.positioning_status && (
              <TruthBadge scope={workbench.positioning_status === "confirmed" ? "observed" : "inferred"} />
            )}
          </div>
          {positioning ? (
            <div className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-3">
              <PositionCard title="行业位置" data={positioning.industry_position} />
              <PositionCard title="经营位置" data={positioning.business_position} />
              <PositionCard title="定位结论" data={positioning.conclusion} />
            </div>
          ) : (
            <ModuleState
              variant="empty"
              title="尚未生成定位草稿"
              description="确认客户档案后可生成本地可解释定位草稿。"
              compact
            />
          )}

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {canWrite && flow === "profile_confirmed" && (
              <ActionButton
                icon={<Sparkles className="h-4 w-4" />}
                label="生成定位草稿"
                busy={busy}
                onClick={() => run(() => generateR2Positioning(workbench!.id))}
              />
            )}
            {canWrite && flow === "positioning_draft" && (
              <ActionButton
                icon={<Target className="h-4 w-4" />}
                label="确认定位"
                busy={busy}
                onClick={confirmPositioning}
              />
            )}
            {canWrite && flow === "positioning_confirmed" && !workbench?.project_id && !confirmProject && (
              <ActionButton
                icon={<Target className="h-4 w-4" />}
                label="基于此定位创建项目"
                busy={busy}
                onClick={() => setConfirmProject(true)}
              />
            )}
            {confirmProject && (
              <div className="flex items-center gap-2 rounded-md border border-amber-300 bg-amber-50 px-3 py-2">
                <span className="text-xs text-amber-800">确认创建项目草稿？不会自动生成任务或计划。</span>
                <button
                  type="button"
                  onClick={createProject}
                  disabled={busy}
                  className="rounded-md bg-amber-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-800"
                >
                  {busy ? "创建中" : "确认创建"}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmProject(false)}
                  className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-600"
                >
                  取消
                </button>
              </div>
            )}
            {workbench?.project_id && (
              <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                项目已建立，执行计划将在“项目与计划”阶段生成。
              </p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

function ActionButton({
  icon,
  label,
  busy,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  busy: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center gap-1.5 rounded-md bg-[color:var(--v106-primary)] px-3 py-2 text-xs font-semibold text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
    >
      {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : icon}
      {label}
    </button>
  );
}

function PositionCard({ title, data }: { title: string; data: Record<string, unknown> }) {
  const entries = Object.entries(data || {}).filter(
    ([key, value]) =>
      !["rule_version", "config_hash", "positioning_hash", "generated_at", "owner_edits", "basis"].includes(key) &&
      typeof value !== "object",
  );
  return (
    <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
      <h3 className="text-xs font-semibold text-slate-700">{title}</h3>
      <dl className="mt-2 space-y-1.5">
        {entries.map(([key, value]) => (
          <div key={key} className="flex justify-between gap-2 text-[11px]">
            <dt className="text-slate-500">{key}</dt>
            <dd className="truncate text-slate-800">{String(value ?? "待补充")}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
