import { CheckCircle2, CircleDashed, CloudOff, TriangleAlert } from "lucide-react";

export type DataSourceState = "connected" | "pending" | "missing" | "blocked";

const STATE_META: Record<DataSourceState, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  connected: {
    label: "已连接",
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
    icon: CheckCircle2,
  },
  pending: {
    label: "待配置",
    className: "bg-amber-50 text-amber-700 border-amber-200",
    icon: CircleDashed,
  },
  missing: {
    label: "缺失",
    className: "bg-slate-100 text-slate-600 border-slate-200",
    icon: CloudOff,
  },
  blocked: {
    label: "受阻",
    className: "bg-rose-50 text-rose-700 border-rose-200",
    icon: TriangleAlert,
  },
};

export default function DataSourceBadge({
  name,
  state,
}: {
  name: string;
  state: DataSourceState;
}) {
  const meta = STATE_META[state];
  const Icon = meta.icon;
  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] font-medium ${meta.className}`}>
      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
      <span className="truncate">{name}</span>
      <span aria-hidden="true">·</span>
      {meta.label}
    </span>
  );
}
