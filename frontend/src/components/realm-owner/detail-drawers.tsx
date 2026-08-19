"use client";

import { AlertTriangle, Database, Lock, MapPin, RefreshCw } from "lucide-react";
import RealmDrawer from "./drawer";
import TruthBadge from "./truth-badge";
import { STARTUP_STATUS_LABELS } from "@/lib/realm-owner/config";
import type { MapNodeDefinition } from "@/lib/realm-owner/config";
import type { RealmOwnerHomeViewModel, TruthScope } from "@/lib/realm-owner/types";

export function TaskDetailDrawer({
  open,
  onClose,
  task,
  onStartRealInput,
}: {
  open: boolean;
  onClose: () => void;
  task: RealmOwnerHomeViewModel["startupTasks"][number] | null;
  onStartRealInput: () => void;
}) {
  return (
    <RealmDrawer
      open={open && Boolean(task)}
      onClose={onClose}
      title={task?.title || "启动任务"}
      description="任务状态由阶段门与后端对象决定，前端表单不会直接标记完成。"
    >
      {task && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
              {STARTUP_STATUS_LABELS[task.status]}
            </span>
            {task.blockedReason && (
              <span className="inline-flex items-center gap-1 text-xs text-amber-700">
                <Lock className="h-3.5 w-3.5" aria-hidden="true" />
                {task.blockedReason}
              </span>
            )}
          </div>
          <p className="text-xs leading-5 text-slate-600">
            当前步骤需要真实输入、Evidence、Demand 或连接状态作为依据。缺少对应接口时页面保持阻塞状态。
          </p>
          {task.targetHref && (
            <button
              type="button"
              onClick={() => {
                onClose();
                onStartRealInput();
              }}
              className="inline-flex w-full items-center justify-center rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800"
            >
              开始补齐真实输入
            </button>
          )}
        </div>
      )}
    </RealmDrawer>
  );
}

export function NodeDetailDrawer({
  open,
  onClose,
  definition,
  truthScope,
  onDraftPosition,
}: {
  open: boolean;
  onClose: () => void;
  definition: MapNodeDefinition | null;
  truthScope: TruthScope | null;
  onDraftPosition: (nodeId: string) => void;
}) {
  return (
    <RealmDrawer
      open={open && Boolean(definition)}
      onClose={onClose}
      title={definition?.label || "地图节点"}
      description="节点为流程预演模板；真实投影数据缺失时不会写回 World。"
    >
      {definition && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <TruthBadge scope={truthScope || "simulation"} />
            <span className="text-[11px] text-slate-500">预演模板</span>
          </div>
          <p className="text-sm leading-6 text-slate-700">{definition.description}</p>
          <button
            type="button"
            onClick={() => {
              onDraftPosition(definition.id);
              onClose();
            }}
            className="inline-flex items-center gap-2 rounded-lg border border-blue-300 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
          >
            <MapPin className="h-4 w-4" aria-hidden="true" />
            将我的位置设为草稿
          </button>
          <p className="text-[11px] leading-5 text-slate-500">
            位置草稿只保存在当前会话，不会写入生产状态；确认需要现有位置 API 与域主审批。
          </p>
        </div>
      )}
    </RealmDrawer>
  );
}

export function MapConfigDrawer({
  open,
  onClose,
  dataSourceLabel,
  snapshotId,
  onRefresh,
  refreshing,
}: {
  open: boolean;
  onClose: () => void;
  dataSourceLabel: string;
  snapshotId: string | null;
  onRefresh: () => void;
  refreshing: boolean;
}) {
  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="地图配置"
      description="当前六节点为流程模板，不写入真实 World。"
      footer={
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onRefresh}
            disabled={refreshing}
            className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} aria-hidden="true" />
            重新拉取
          </button>
        </div>
      }
    >
      <div className="space-y-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-700">当前数据源</p>
          <p className="mt-1 text-sm text-slate-800">{dataSourceLabel}</p>
          {snapshotId && <p className="mt-1 text-[11px] text-slate-500">Snapshot：{snapshotId}</p>}
        </div>
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-[11px] leading-5 text-amber-800">
          <AlertTriangle className="mr-1 inline h-3.5 w-3.5" aria-hidden="true" />
          没有 World 投影数据时，地图只作为配置模板。拖拽、组合和位置草稿仅形成 draft/simulation，不能自动发布。
        </div>
      </div>
    </RealmDrawer>
  );
}

export function LockedNavDrawer({
  open,
  onClose,
  label,
}: {
  open: boolean;
  onClose: () => void;
  label: string;
}) {
  return (
    <RealmDrawer open={open} onClose={onClose} title={label || "工作面"} description="本期只开放探索主页。">
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <Database className="h-5 w-5 text-slate-400" aria-hidden="true" />
        <p className="mt-2 text-sm font-medium text-slate-700">{label}工作面待后续开放</p>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          一级导航保持完整，不隐藏；进入后会展示未开放状态，不创建空白页面。
        </p>
      </div>
    </RealmDrawer>
  );
}