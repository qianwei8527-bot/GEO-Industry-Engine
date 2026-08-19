import { CheckCircle2, CircleDashed, Info, TriangleAlert } from "lucide-react";

export type StatusStripTone = "neutral" | "success" | "warning" | "danger" | "inferred";

export interface StatusStripItem {
  label: string;
  value: string;
  tone?: StatusStripTone;
}

const TONE_CLASS: Record<StatusStripTone, { text: string; bg: string; icon: typeof Info }> = {
  neutral: { text: "text-slate-600", bg: "bg-slate-100", icon: CircleDashed },
  success: { text: "text-emerald-700", bg: "bg-emerald-50", icon: CheckCircle2 },
  warning: { text: "text-amber-700", bg: "bg-amber-50", icon: TriangleAlert },
  danger: { text: "text-rose-700", bg: "bg-rose-50", icon: TriangleAlert },
  inferred: { text: "text-violet-700", bg: "bg-violet-50", icon: Info },
};

export default function StatusStrip({ items }: { items: StatusStripItem[] }) {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
      {items.map((item) => {
        const tone = TONE_CLASS[item.tone || "neutral"];
        const Icon = tone.icon;
        return (
          <div key={item.label} className="flex min-w-0 items-center gap-1.5 text-xs">
            <span className="shrink-0 text-slate-500">{item.label}</span>
            <span className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 font-medium ${tone.text} ${tone.bg}`}>
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="truncate">{item.value}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}
