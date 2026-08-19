"use client";

import { Bot, FilePlus2, Loader2, RefreshCw } from "lucide-react";
import { RESOURCE_GROUP_DEFS } from "@/lib/realm-owner/config";
import ModuleState from "./module-state";
import TruthBadge from "./truth-badge";
import type { ModuleStateVariant } from "./module-state";
import type { RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

interface ResourceConnectionPanelProps {
  resources: RealmOwnerHomeViewModel["resources"];
  onOpenDemandForm: () => void;
  onGenerateCandidates: () => void;
  generating: boolean;
  onDraftContact: (candidateId: string) => void;
  canWrite?: boolean;
  state?: ModuleStateVariant | "ready";
  stateTitle?: string;
  stateDescription?: string;
  onRetry?: () => void;
}

function ConnectionStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    proposed: "已提议",
    qualified: "已筛选",
    accepted: "已接受",
    completed: "已完成",
    rejected: "已拒绝",
  };
  return labels[status] || status || "未确认";
}

export default function ResourceConnectionPanel({
  resources,
  onOpenDemandForm,
  onGenerateCandidates,
  generating,
  onDraftContact,
  canWrite = true,
  state = "ready",
  stateTitle,
  stateDescription,
  onRetry,
}: ResourceConnectionPanelProps) {
  const totalCandidates = resources.groups.reduce((sum, group) => sum + group.candidates.length, 0);

  return (
    <section className="realm-card flex flex-col p-3.5" aria-labelledby="resource-connection-title">
      <header className="flex items-center gap-2">
        <h2 id="resource-connection-title" className="text-sm font-semibold text-slate-800">优先资源与连接</h2>
        {totalCandidates > 0 && (
          <span className="rounded-md bg-teal-50 px-1.5 py-0.5 text-[11px] font-semibold text-teal-700">
            {totalCandidates} 个候选
          </span>
        )}
      </header>

      {state !== "ready" ? (
        <div className="mt-3">
          <ModuleState
            variant={state}
            title={stateTitle || (state === "error" ? "资源数据不可用" : "资源数据加载中")}
            description={stateDescription || "该模块已隔离，不影响其他模块。"}
            actionLabel={state === "error" ? "重试" : undefined}
            onAction={onRetry}
          />
        </div>
      ) : (
        <>
          {!resources.hasDemand && (
            <div className="mt-3 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-3 text-xs leading-5 text-slate-600">
              先发布真实需求，系统再提供带证据的匹配。当前不生成任何候选名称。
            </div>
          )}
          {resources.hasDemand && totalCandidates === 0 && (
            <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-3 text-xs leading-5 text-amber-800">
              资源需求已记录，但还没有匹配候选。可生成候选；所有候选都必须展示理由、证据、风险与未知项。
            </div>
          )}

          <div className="mt-3 space-y-3">
            {RESOURCE_GROUP_DEFS.map((group) => {
              const data = resources.groups.find((item) => item.type === group.type);
              return (
                <section key={group.type} className="rounded-lg border border-slate-200 bg-slate-50/50 p-2.5">
                  <h3 className="text-xs font-semibold text-slate-700">{group.label}</h3>
                  {data && data.candidates.length > 0 ? (
                    <ul className="mt-2 space-y-2">
                      {data.candidates.map((candidate) => (
                        <CandidateCard key={candidate.id} candidate={candidate} onDraftContact={onDraftContact} />
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-1.5 text-[11px] leading-4 text-slate-500">{group.emptyHint}</p>
                  )}
                </section>
              );
            })}
          </div>

          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={onOpenDemandForm}
              disabled={!canWrite}
              title={canWrite ? undefined : "需要域主或编辑权限"}
              className={`inline-flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${canWrite ? "bg-teal-700 text-white hover:bg-teal-800" : "bg-slate-200 text-slate-500 cursor-not-allowed"}`}
            >
              <FilePlus2 className="h-4 w-4" aria-hidden="true" />
              发布资源需求
            </button>
            {resources.hasDemand && totalCandidates === 0 && (
              <button
                type="button"
                onClick={onGenerateCandidates}
                disabled={generating || !canWrite}
                title={canWrite ? undefined : "需要域主或编辑权限"}
                className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
              >
                {generating ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="h-4 w-4" aria-hidden="true" />}
                生成候选
              </button>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function CandidateCard({
  candidate,
  onDraftContact,
}: {
  candidate: RealmOwnerHomeViewModel["resources"]["groups"][number]["candidates"][number];
  onDraftContact: (candidateId: string) => void;
}) {
  return (
    <li className="rounded-lg border border-slate-200 bg-white p-2.5">
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[13px] font-semibold text-slate-800">{candidate.name}</span>
            <TruthBadge scope={candidate.truthScope} />
            <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">
              {ConnectionStatusLabel(candidate.connectionStatus)}
            </span>
          </div>
          <p className="mt-1 text-[11px] leading-4 text-slate-600">{candidate.reason}</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5 text-[11px] text-slate-500">
            <span>证据：已验证 {candidate.evidenceCounts.verified}</span>
            <span>已观察 {candidate.evidenceCounts.observed}</span>
            <span>预演 {candidate.evidenceCounts.synthetic}</span>
          </div>
          {candidate.risk && (
            <p className="mt-1.5 rounded bg-rose-50 px-2 py-1 text-[11px] leading-4 text-rose-700">风险：{candidate.risk}</p>
          )}
          {candidate.unknowns.length > 0 && (
            <ul className="mt-1.5 space-y-0.5">
              {candidate.unknowns.map((item) => (
                <li key={item} className="text-[11px] text-slate-500">未知项：{item}</li>
              ))}
            </ul>
          )}
        </div>
        <button
          type="button"
          onClick={() => onDraftContact(candidate.id)}
          className="inline-flex h-7 shrink-0 items-center gap-1 rounded-md border border-slate-200 px-2 text-[11px] font-medium text-slate-600 hover:bg-violet-50 hover:text-violet-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-600"
          title="AI 仅起草，不自动发送"
        >
          <Bot className="h-3 w-3" aria-hidden="true" />
          AI起草
        </button>
      </div>
    </li>
  );
}