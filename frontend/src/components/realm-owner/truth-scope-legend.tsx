"use client";

import { TRUTH_SCOPE_META } from "@/lib/realm-owner/config";
import TruthBadge from "./truth-badge";

export default function TruthScopeLegend() {
  return (
    <section
      className="realm-card px-4 py-3"
      aria-label="truth scope 图例"
    >
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
        <span className="text-xs font-semibold text-slate-700">truth scope 图例</span>
        {TRUTH_SCOPE_META.map((meta) => (
          <span key={meta.scope} className="inline-flex items-center gap-2 text-xs text-slate-600">
            <TruthBadge scope={meta.scope} />
            <span className="text-slate-500">{meta.meaning}</span>
          </span>
        ))}
      </div>
    </section>
  );
}