"use client";

import Link from "next/link";
import { Compass, Lock } from "lucide-react";
import { PRIMARY_NAV_DEFS } from "@/lib/realm-owner/config";
import { getIcon } from "./icon-map";

interface PrimarySidebarProps {
  realmId: string;
  activeId?: string;
  onOpenLocked: (label: string) => void;
}

export default function PrimarySidebar({ realmId, activeId = "explore", onOpenLocked }: PrimarySidebarProps) {
  return (
    <aside className="hidden md:flex md:w-[76px] lg:w-[184px] shrink-0 flex-col border-r border-slate-200 bg-white">
      <Link
        href={`/realm/${realmId}/explore`}
        className="flex h-16 items-center gap-2.5 border-b border-slate-200 px-3 lg:px-4 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-teal-600"
        aria-label="恒域世界-GEO 域主工作台"
      >
        <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-700 text-white">
          <Compass className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="hidden lg:block text-sm font-bold text-slate-900 leading-tight">恒域世界-GEO</span>
      </Link>

      <nav className="flex-1 overflow-y-auto py-3" aria-label="一级工作面">
        <ul className="space-y-1 px-2 lg:px-3">
          {PRIMARY_NAV_DEFS.map((item) => {
            const Icon = getIcon(item.iconKey);
            const active = item.id === activeId;
            if (item.enabled) {
              return (
                <li key={item.id}>
                  <Link
                    href={item.href(realmId)}
                    aria-current={active ? "page" : undefined}
                    className={`group flex items-center gap-2.5 rounded-lg px-2.5 py-2.5 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${
                      active
                        ? "bg-teal-50 text-teal-800"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <Icon className={`h-[18px] w-[18px] shrink-0 ${active ? "text-teal-700" : "text-slate-400 group-hover:text-slate-600"}`} aria-hidden="true" />
                    <span className="hidden lg:block truncate">{item.label}</span>
                    {active && <span className="hidden lg:block ml-auto h-1.5 w-1.5 rounded-full bg-teal-600" aria-hidden="true" />}
                  </Link>
                </li>
              );
            }
            return (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => onOpenLocked(item.label)}
                  className="group flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2.5 text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
                  title={`${item.label}（本期未开放）`}
                >
                  <Icon className="h-[18px] w-[18px] shrink-0 text-slate-400 group-hover:text-slate-500" aria-hidden="true" />
                  <span className="hidden lg:block truncate">{item.label}</span>
                  <Lock className="hidden lg:block ml-auto h-3.5 w-3.5 text-slate-300" aria-hidden="true" />
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="hidden lg:block border-t border-slate-200 px-4 py-3 text-[11px] leading-4 text-slate-400">
        域主工作台；今日工作为当前视图
      </div>
    </aside>
  );
}

export function MobileRealmNav({
  realmId,
  activeId = "explore",
  onOpenLocked,
}: PrimarySidebarProps) {
  return (
    <nav
      className="md:hidden flex items-center gap-1 overflow-x-auto border-b border-slate-200 bg-white px-2 py-2"
      aria-label="一级工作面"
    >
      {PRIMARY_NAV_DEFS.map((item) => {
        const Icon = getIcon(item.iconKey);
        const active = item.id === activeId;
        if (item.enabled) {
          return (
            <Link
              key={item.id}
              href={item.href(realmId)}
              aria-current={active ? "page" : undefined}
              className={`flex shrink-0 items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium ${
                active ? "bg-teal-50 text-teal-800" : "text-slate-600"
              }`}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {item.label}
            </Link>
          );
        }
        return (
          <button
            key={item.id}
            type="button"
            onClick={() => onOpenLocked(item.label)}
            className="flex shrink-0 items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-500"
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            {item.label}
          </button>
        );
      })}
    </nav>
  );
}
