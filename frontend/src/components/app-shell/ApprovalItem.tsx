import { Check, ShieldAlert, X } from "lucide-react";

export type ApprovalRisk = "low" | "medium" | "high" | "forbidden";

interface ApprovalItemProps {
  title: string;
  source: string;
  risk: ApprovalRisk;
  actionLabel: string;
  disabled?: boolean;
  onApprove?: () => void;
  onReject?: () => void;
}

const RISK_LABEL: Record<ApprovalRisk, { label: string; className: string }> = {
  low: { label: "低风险", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  medium: { label: "中风险", className: "bg-amber-50 text-amber-700 border-amber-200" },
  high: { label: "高风险", className: "bg-rose-50 text-rose-700 border-rose-200" },
  forbidden: { label: "禁止动作", className: "bg-slate-100 text-slate-600 border-slate-300" },
};

export default function ApprovalItem({
  title,
  source,
  risk,
  actionLabel,
  disabled = false,
  onApprove,
  onReject,
}: ApprovalItemProps) {
  const riskMeta = RISK_LABEL[risk];
  return (
    <li className="v106-panel p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-900">{title}</p>
          <p className="mt-1 truncate text-xs text-slate-500">{source}</p>
        </div>
        <span className={`inline-flex shrink-0 items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] font-medium ${riskMeta.className}`}>
          <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" />
          {riskMeta.label}
        </span>
      </div>
      <div className="mt-3 flex items-center gap-2">
        {onApprove && (
          <button
            type="button"
            onClick={onApprove}
            disabled={disabled}
            className="inline-flex items-center gap-1.5 rounded-md bg-[color:var(--v106-primary)] px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
          >
            <Check className="h-3.5 w-3.5" aria-hidden="true" />
            {actionLabel}
          </button>
        )}
        {onReject && (
          <button
            type="button"
            onClick={onReject}
            disabled={disabled}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-60"
          >
            <X className="h-3.5 w-3.5" aria-hidden="true" />
            拒绝
          </button>
        )}
      </div>
    </li>
  );
}
