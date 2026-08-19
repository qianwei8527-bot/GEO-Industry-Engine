"use client";

import { CheckCircle2, Clock, ShieldCheck } from "lucide-react";
import RealmDrawer from "./drawer";

export interface DecisionApprovalItem {
  id: string;
  title: string;
  status: "pending" | "needs_review" | "blocked";
  detail: string;
}

interface RealmDecisionApprovalDrawerProps {
  open: boolean;
  onClose: () => void;
  items: DecisionApprovalItem[];
  loading: boolean;
  error: string | null;
}

export default function RealmDecisionApprovalDrawer({
  open,
  onClose,
  items,
  loading,
  error,
}: RealmDecisionApprovalDrawerProps) {
  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="决策与审批"
      description="权限与审批由后端 node_memberships 判定；本页只展示可读审批项。"
    >
      {loading && <div className="py-8 text-center text-sm text-slate-500" role="status">加载审批项…</div>}

      {!loading && error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-3 text-xs leading-5 text-rose-700">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-8 text-center">
          <CheckCircle2 className="mx-auto h-6 w-6 text-slate-400" aria-hidden="true" />
          <p className="mt-2 text-sm font-medium text-slate-600">暂无待审批事项</p>
          <p className="mt-1 text-xs text-slate-500">领域认领、授权和连接决策会出现在这里。</p>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id} className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
              <div className="flex items-start gap-2">
                <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-amber-50 text-amber-600">
                  <Clock className="h-3.5 w-3.5" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="text-[13px] font-medium text-slate-800">{item.title}</p>
                  <p className="mt-1 text-[11px] leading-4 text-slate-500">{item.detail}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal-700" aria-hidden="true" />
        <p className="text-[11px] leading-5 text-slate-500">
          前端不自行判断域主身份；审批操作需调用现有后端权限链，本期只实现入口与只读状态。
        </p>
      </div>
    </RealmDrawer>
  );
}