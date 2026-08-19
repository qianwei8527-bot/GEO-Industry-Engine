"use client";

import { TRUTH_SCOPE_META } from "@/lib/realm-owner/config";
import { getIcon } from "./icon-map";
import type { TruthScope } from "@/lib/realm-owner/types";

const SCOPE_CLASSES: Record<TruthScope, { badge: string; ring: string; icon: string }> = {
  verified: {
    badge: "bg-emerald-50 text-emerald-700 border-emerald-300",
    ring: "border-emerald-500",
    icon: "text-emerald-600",
  },
  observed: {
    badge: "bg-blue-50 text-blue-700 border-blue-300",
    ring: "border-blue-400",
    icon: "text-blue-600",
  },
  inferred: {
    badge: "bg-violet-50 text-violet-700 border-violet-300",
    ring: "border-dashed border-violet-400",
    icon: "text-violet-600",
  },
  simulation: {
    badge: "bg-slate-100 text-slate-600 border-slate-300",
    ring: "border-dotted border-slate-400",
    icon: "text-slate-500",
  },
  unknown: {
    badge: 'bg-amber-50 text-amber-700 border-amber-300',
    ring: 'border-dashed border-amber-400',
    icon: 'text-amber-600',
  },
};

export default function TruthBadge({ scope, showMeaning = false }: { scope: TruthScope; showMeaning?: boolean }) {
  const meta = TRUTH_SCOPE_META.find((item) => item.scope === scope) || TRUTH_SCOPE_META[3];
  const Icon = getIcon(meta.iconKey);
  const classes = SCOPE_CLASSES[scope];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] font-medium ${classes.badge}`}
      title={meta.meaning}
    >
      <Icon className={`w-3 h-3 ${classes.icon}`} aria-hidden="true" />
      {meta.label}
      {showMeaning && <span className="sr-only">：{meta.meaning}</span>}
    </span>
  );
}

export function TruthScopeClasses(scope: TruthScope): string {
  return SCOPE_CLASSES[scope].ring;
}
