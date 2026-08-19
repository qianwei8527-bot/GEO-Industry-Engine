"use client";

import { ArrowRight, CheckCircle2, ChevronRight, Circle, Lock, PlayCircle } from "lucide-react";
import { STARTUP_STATUS_LABELS } from "@/lib/realm-owner/config";
import type { RealmOwnerHomeViewModel, StartupTaskStatus } from "@/lib/realm-owner/types";

const STATUS_CLASSES: Record<StartupTaskStatus, string> = {
  locked: "bg-slate-100 text-slate-500",
  ready: "bg-teal-50 text-teal-700",
  in_progress: "bg-blue-50 text-blue-700",
  blocked: "bg-rose-50 text-rose-700",
  needs_review: "bg-amber-50 text-amber-700",
  completed: "bg-emerald-50 text-emerald-700",
};

function StatusIcon({ status }: { status: StartupTaskStatus }) {
  if (status === "completed") return <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />;
  if (status === "locked") return <Lock className="h-3.5 w-3.5" aria-hidden="true" />;
  if (status === "ready") return <PlayCircle className="h-3.5 w-3.5" aria-hidden="true" />;
  return <Circle className="h-3.5 w-3.5" aria-hidden="true" />;
}

export default function StartupTaskRail({
  tasks,
  onOpenTask,
  onStartRealInput,
  canWrite = true,
}: {
  tasks: RealmOwnerHomeViewModel["startupTasks"];
  onOpenTask: (taskId: string) => void;
  onStartRealInput: () => void;
  canWrite?: boolean;
}) {
  return (
    <section className="realm-card flex flex-col p-3.5" aria-labelledby="startup-tasks-title">
      <h2 id="startup-tasks-title" className="text-sm font-semibold text-slate-800">本周启动任务</h2>
      <p className="mt-0.5 text-[11px] text-slate-500">按阶段门解锁，前端表单不会直接标记完成</p>

      <ol className="mt-3 space-y-2">
        {tasks.map((task, index) => (
          <li key={task.id}>
            <button
              type="button"
              onClick={() => onOpenTask(task.id)}
              className="group w-full rounded-lg border border-slate-200 bg-slate-50/60 px-2.5 py-2 text-left hover:border-teal-300 hover:bg-teal-50/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
            >
              <span className="flex items-center gap-2">
                <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-white text-[11px] font-bold text-slate-500 ring-1 ring-slate-200">
                  {index + 1}
                </span>
                <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-slate-800">{task.title}</span>
                <span className={`inline-flex shrink-0 items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium ${STATUS_CLASSES[task.status]}`}>
                  <StatusIcon status={task.status} />
                  {STARTUP_STATUS_LABELS[task.status]}
                </span>
              </span>
              {task.blockedReason && (
                <span className="mt-1.5 block pl-7 text-[11px] leading-4 text-slate-500">{task.blockedReason}</span>
              )}
            </button>
          </li>
        ))}
      </ol>

      <button
        type="button"
        onClick={onStartRealInput}
        disabled={!canWrite}
        title={canWrite ? undefined : "需要域主或编辑权限"}
        className={`mt-3 inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${canWrite ? "bg-teal-700 text-white hover:bg-teal-800" : "bg-slate-200 text-slate-500 cursor-not-allowed"}`}
      >
        开始补齐真实输入
        <ArrowRight className="h-4 w-4" aria-hidden="true" />
      </button>

      <button
        type="button"
        className="mt-2 inline-flex items-center justify-center gap-1 text-xs font-medium text-slate-500 hover:text-teal-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
      >
        查看90天计划解锁条件
        <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
    </section>
  );
}