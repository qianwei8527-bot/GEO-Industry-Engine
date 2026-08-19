"use client";

import { useState } from "react";
import { FileQuestion } from "lucide-react";
import { INFORMATION_CATEGORY_DEFS } from "@/lib/realm-owner/config";
import TruthBadge from "./truth-badge";
import type { InformationCategory, RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

type CategoryFilter = InformationCategory | "all";

interface TrustedInformationFeedProps {
  information: RealmOwnerHomeViewModel["information"];
  searchQuery: string;
}

export default function TrustedInformationFeed({ information, searchQuery }: TrustedInformationFeedProps) {
  const [active, setActive] = useState<CategoryFilter>("all");

  const filtered = information.filter((item) => {
    const categoryMatch = active === "all" || item.category === active;
    const query = searchQuery.trim().toLowerCase();
    const textMatch =
      !query ||
      item.title.toLowerCase().includes(query) ||
      (item.sourceName || "").toLowerCase().includes(query);
    return categoryMatch && textMatch;
  });

  return (
    <section className="realm-card flex flex-col p-3.5" aria-labelledby="information-feed-title">
      <header className="flex items-center justify-between gap-2">
        <h2 id="information-feed-title" className="text-sm font-semibold text-slate-800">可信信息流</h2>
        <span className="text-[11px] text-slate-500">{filtered.length} 条</span>
      </header>

      <div role="tablist" aria-label="可信信息来源类型" className="mt-3 flex flex-wrap gap-1.5">
        <button
          type="button"
          role="tab"
          aria-selected={active === "all"}
          onClick={() => setActive("all")}
          className={`rounded-lg px-2.5 py-1.5 text-xs font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${
            active === "all" ? "bg-slate-800 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          全部
        </button>
        {INFORMATION_CATEGORY_DEFS.map((category) => {
          const count = information.filter((item) => item.category === category.id).length;
          return (
            <button
              key={category.id}
              type="button"
              role="tab"
              aria-selected={active === category.id}
              onClick={() => setActive(category.id)}
              className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${
                active === category.id ? "bg-teal-700 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {category.label}
              <span className="rounded bg-white/20 px-1 text-[10px]">{count}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-3 flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-6 text-center">
            <FileQuestion className="mx-auto h-5 w-5 text-slate-400" aria-hidden="true" />
            <p className="mt-2 text-sm font-medium text-slate-600">暂无信息</p>
            <p className="mt-1 text-xs text-slate-500">选择上方来源类型，获取可信内容</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {filtered.map((item) => (
              <li key={item.id} className="rounded-lg border border-slate-200 bg-slate-50/60 p-2.5">
                <div className="flex items-start gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-medium leading-5 text-slate-800">{item.title}</p>
                    <p className="mt-1 text-[11px] text-slate-500">
                      {item.sourceName}
                      {item.observedAt ? ` · ${formatTime(item.observedAt)}` : ""}
                    </p>
                  </div>
                  <TruthBadge scope={item.truthScope} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("zh-CN", { month: "2-digit", day: "2-digit" });
}