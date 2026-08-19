"use client";

import { useEffect, useState } from "react";
import { FlaskConical, Loader2, Play } from "lucide-react";
import ModuleState from "./module-state";
import TruthBadge from "./truth-badge";
import {
  fetchSimulationLoopLatest,
  runSimulationLoop,
  type SimulationLoopLatest,
  type SimulationLoopResult,
} from "@/lib/realm-owner/simulation-loop";

export default function SimulationLoopPanel({
  realmId,
  canWrite,
}: {
  realmId: string;
  canWrite: boolean;
}) {
  const [latest, setLatest] = useState<SimulationLoopLatest | null>(null);
  const [result, setResult] = useState<SimulationLoopResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetchSimulationLoopLatest(realmId)
      .then((data) => {
        if (!cancelled) setLatest(data);
      })
      .catch(() => {
        if (!cancelled) setError("模拟闭环状态读取失败");
      });
    return () => {
      cancelled = true;
    };
  }, [realmId]);

  async function run() {
    if (!canWrite) return;
    setBusy(true);
    setError("");
    try {
      const next = await runSimulationLoop(realmId);
      setResult(next);
      setLatest(await fetchSimulationLoopLatest(realmId));
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "模拟闭环运行失败");
    } finally {
      setBusy(false);
    }
  }

  const steps = [
    { label: "资料提交", value: result?.intake.intake_code || latest?.latest?.intake_code || "未运行", ready: Boolean(result || latest?.latest) },
    { label: "本地提取", value: result ? `${result.analysis.field_count} 字段` : "未运行", ready: Boolean(result) },
    { label: "定位结论", value: result ? result.position_conclusion.truth_scope : "未运行", ready: Boolean(result) },
    { label: "项目与计划", value: result ? `${result.plan.work_item_count} 个任务` : "未运行", ready: Boolean(result) },
  ];

  return (
    <section className="v106-panel p-4" aria-labelledby="simulation-loop-title">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-600">
            <FlaskConical className="h-4 w-4" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <h2 id="simulation-loop-title" className="flex items-center gap-2 text-base font-semibold text-slate-900">
              基础架构模拟闭环
              <TruthBadge scope="simulation" />
            </h2>
            <p className="mt-0.5 text-xs leading-5 text-slate-500">
              模拟数据只用于打通基础设施链路，不会影响真实指标、关系或 Reputation。
            </p>
          </div>
        </div>
        {canWrite && (
          <button
            type="button"
            onClick={run}
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-md bg-[color:var(--v106-primary)] px-3 py-2 text-sm font-semibold text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
          >
            {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Play className="h-4 w-4" aria-hidden="true" />}
            {busy ? "运行中" : "运行模拟闭环"}
          </button>
        )}
      </header>

      {!canWrite && (
        <div className="mt-3">
          <ModuleState variant="blocked" title="只读视图" description="运行模拟闭环需要域主或编辑权限。" compact />
        </div>
      )}

      {error && (
        <p className="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
          {error}
        </p>
      )}

      <div className="mt-4 grid grid-cols-2 gap-2 lg:grid-cols-4">
        {steps.map((step) => (
          <div key={step.label} className="rounded-md border border-[color:var(--v106-border)] bg-[color:var(--v106-surface-muted)] p-3">
            <div className="text-[11px] font-medium text-slate-500">{step.label}</div>
            <div className="mt-1 truncate text-sm font-semibold text-slate-800">{step.value}</div>
            <div className={`mt-1 text-[11px] ${step.ready ? "text-emerald-600" : "text-slate-400"}`}>
              {step.ready ? "已打通" : "未运行"}
            </div>
          </div>
        ))}
      </div>

      {result && (
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-medium text-slate-700">定位结论</span>
            <TruthBadge scope="simulation" />
            <span className="text-slate-500">{result.position_conclusion.claim}</span>
          </div>
          {result.position_conclusion.unknowns.length > 0 && (
            <p className="mt-2 text-[11px] text-amber-700">
              待补充：{result.position_conclusion.unknowns.join("、")}
            </p>
          )}
          <p className="mt-2 text-[11px] text-slate-500">
            证据 {result.evidence.truth_status} · 项目 {result.project.truth_status} · 计划 {result.plan.work_item_count} 个任务
          </p>
        </div>
      )}
    </section>
  );
}
