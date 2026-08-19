"use client";

import { useState } from "react";
import { Bot, ChevronRight, Search, ShieldCheck } from "lucide-react";
import type { RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

interface RealmContextHeaderProps {
  realm: RealmOwnerHomeViewModel["realm"];
  onSearch: (query: string) => void;
  onOpenAssistant: () => void;
  onOpenDecisions: () => void;
}

export default function RealmContextHeader({
  realm,
  onSearch,
  onOpenAssistant,
  onOpenDecisions,
}: RealmContextHeaderProps) {
  const [query, setQuery] = useState("");

  const crumbs = [
    "恒域世界-GEO",
    realm.displayName || "Realm 待确认",
    realm.worldName || "行业验证期",
    realm.trackName || "90天待解锁",
    realm.operatingCycleLabel || "90天待解锁",
  ].filter(Boolean);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:px-6">
      <div className="flex min-w-0 flex-1 items-center gap-1 overflow-hidden text-xs text-slate-500">
        {crumbs.map((crumb, index) => (
          <span key={`${crumb}-${index}`} className="flex min-w-0 items-center gap-1">
            {index > 0 && <ChevronRight className="h-3.5 w-3.5 shrink-0 text-slate-300" aria-hidden="true" />}
            <span className="truncate">{crumb}</span>
          </span>
        ))}
      </div>

      <div className="relative hidden sm:block w-56 lg:w-72 shrink-0">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <input
          type="search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            onSearch(event.target.value);
          }}
          placeholder="搜索可信信息流"
          aria-label="搜索可信信息流"
          className="h-9 w-full rounded-lg border border-slate-300 bg-slate-50 pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-100"
        />
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={onOpenAssistant}
          className="inline-flex h-9 items-center gap-1.5 rounded-lg bg-violet-50 px-2.5 text-xs font-medium text-violet-700 hover:bg-violet-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-600"
        >
          <Bot className="h-4 w-4" aria-hidden="true" />
          <span className="hidden xl:inline">AI域主助手</span>
          <span className="xl:hidden">AI助手</span>
        </button>
        <button
          type="button"
          onClick={onOpenDecisions}
          className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 text-xs font-medium text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
        >
          <ShieldCheck className="h-4 w-4 text-teal-700" aria-hidden="true" />
          <span className="hidden xl:inline">决策与审批</span>
          <span className="xl:hidden">审批</span>
        </button>
      </div>
    </header>
  );
}