"use client";

import { ArrowRight, Lock, Target } from "lucide-react";
import type { RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

export default function NextBestActionPanel({
  nextAction,
  onOpenTarget,
}: {
  nextAction: RealmOwnerHomeViewModel["nextAction"];
  onOpenTarget: (targetHref: string | null) => void;
}) {
  const blocked = nextAction.blockedReasons.length > 0;
  return (
    <section className="realm-card flex flex-col p-3.5" aria-labelledby="next-action-title">
      <h2 id="next-action-title" className="text-sm font-semibold text-slate-800">下一步行动</h2>
      <p className="mt-0.5 text-[11px] text-slate-500">完成后解锁90天计划</p>

      <div className="mt-3 flex-1 rounded-lg border border-teal-200 bg-teal-50/50 p-3">
        <div className="flex items-start gap-2">
          <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-700 text-white">
            <Target className="h-4 w-4" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-900">{nextAction.title}</p>
            <p className="mt-1 text-xs leading-5 text-slate-600">{nextAction.reason}</p>
          </div>
        </div>

        <dl className="mt-3 space-y-2 text-xs">
          <div className="rounded-md bg-white px-2.5 py-2 ring-1 ring-slate-200">
            <dt className="text-[11px] font-medium text-slate-400">完成标准</dt>
            <dd className="mt-0.5 leading-4 text-slate-700">{nextAction.completionCondition}</dd>
          </div>
          {blocked && (
            <div className="rounded-md bg-white px-2.5 py-2 ring-1 ring-rose-200">
              <dt className="flex items-center gap-1 text-[11px] font-medium text-rose-600">
                <Lock className="h-3 w-3" aria-hidden="true" />
                阻塞原因
              </dt>
              <dd className="mt-0.5 leading-4 text-rose-700">
                {nextAction.blockedReasons.join("；")}
              </dd>
            </div>
          )}
        </dl>

        <button
          type="button"
          onClick={() => onOpenTarget(nextAction.targetHref)}
          disabled={!nextAction.targetHref}
          className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
        >
          {nextAction.targetHref ? "去完成" : "等待解锁"}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}