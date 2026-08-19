"use client";

import { FilePlus2, FileText, Handshake, Lightbulb } from "lucide-react";
import { READINESS_LABELS } from "@/lib/realm-owner/config";
import type { ReadinessStatus, RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

const STRIP_ITEMS: Array<{
  key: keyof RealmOwnerHomeViewModel["readiness"];
  label: string;
  icon: typeof FileText;
  missingText: string;
}> = [
  { key: "realInputs", label: "真实输入", icon: FileText, missingText: "待补齐" },
  { key: "industryKnowledge", label: "行业认知", icon: Lightbulb, missingText: "未建立" },
  { key: "resourceDemand", label: "资源需求", icon: FilePlus2, missingText: "未发布" },
  { key: "validConnections", label: "有效连接", icon: Handshake, missingText: "无记录" },
];

const STATUS_CLASSES: Record<ReadinessStatus, string> = {
  unknown: "text-slate-500 bg-slate-100",
  missing: "text-amber-700 bg-amber-50",
  partial: "text-blue-700 bg-blue-50",
  ready: "text-emerald-700 bg-emerald-50",
  blocked: "text-rose-700 bg-rose-50",
  stale: "text-amber-700 bg-amber-50",
};

export default function StartupTruthStrip({ readiness }: { readiness: RealmOwnerHomeViewModel["readiness"] }) {
  return (
    <section className="grid grid-cols-2 gap-2 xl:grid-cols-4" aria-label="四项真实状态">
      {STRIP_ITEMS.map((item) => {
        const Icon = item.icon;
        const status = readiness[item.key];
        const text = status === "missing" ? item.missingText : READINESS_LABELS[status] || "未知";
        return (
          <div
            key={item.key}
            className="realm-card flex items-center gap-3 px-3 py-2.5 min-w-0"
          >
            <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
              <Icon className="h-4 w-4" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="block text-xs text-slate-500">{item.label}</span>
              <span className={`mt-0.5 inline-flex rounded-md px-1.5 py-0.5 text-xs font-semibold ${STATUS_CLASSES[status]}`}>
                {text}
              </span>
            </span>
          </div>
        );
      })}
    </section>
  );
}