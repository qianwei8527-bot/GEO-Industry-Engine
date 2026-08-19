"use client";

import { GitBranch, Link2, ShieldCheck } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import StatusStrip from "@/components/app-shell/StatusStrip";
import { CODE_CONNECTIONS, connectionCounts } from "@/lib/code-connection";

export default function SystemMapPage() {
  const counts = connectionCounts();
  const surfaces = Array.from(new Set(CODE_CONNECTIONS.map((item) => item.surfaceId)));

  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <GitBranch className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">系统代码连接</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        {surfaces.map((surface) => (
          <div key={surface} className="mb-2">
            <div className="px-2 py-1 text-[11px] text-slate-500">{surfaceLabel(surface)}</div>
            {CODE_CONNECTIONS.filter((item) => item.surfaceId === surface).map((item) => (
              <div key={item.pageId} className="rounded-md px-2.5 py-1.5 text-xs text-slate-600">
                {item.pageLabel}
              </div>
            ))}
          </div>
        ))}
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        连接注册表：frontend/src/lib/code-connection.ts
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="operations"
      featureFlags={["system-map"]}
      navRail={navRail}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <span className="text-xs text-slate-500">恒域世界 / 系统代码连接</span>
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "连接总数", value: String(counts.total) },
            { label: "已实现", value: String(counts.implemented), tone: "success" },
            { label: "部分", value: String(counts.partial), tone: "warning" },
            { label: "预留", value: String(counts.reserved) },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <Link2 className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">恒域世界代码连接</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">每个页面都对应真实路由、组件和 API；新增页面只需在注册表登记。</p>
        </header>

        {surfaces.map((surface) => (
          <section key={surface} className="v106-panel mb-4 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">
              <span className="inline-flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-[color:var(--v106-primary)]" aria-hidden="true" />
                {surfaceLabel(surface)}
              </span>
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-xs">
                <thead>
                  <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                    <th className="pb-2 pr-3 font-medium">页面</th>
                    <th className="pb-2 pr-3 font-medium">路由</th>
                    <th className="pb-2 pr-3 font-medium">组件</th>
                    <th className="pb-2 pr-3 font-medium">API</th>
                    <th className="pb-2 font-medium">状态</th>
                  </tr>
                </thead>
                <tbody>
                  {CODE_CONNECTIONS.filter((item) => item.surfaceId === surface).map((item) => (
                    <tr key={item.pageId} className="border-b border-[color:var(--v106-border)] last:border-0">
                      <td className="py-2 pr-3">{item.pageLabel}</td>
                      <td className="py-2 pr-3 font-mono text-slate-600">{item.route}</td>
                      <td className="py-2 pr-3 font-mono text-slate-600">{item.component}</td>
                      <td className="py-2 pr-3">
                        <span className="text-slate-600">{item.api.length > 0 ? item.api.join("、") : "待接通"}</span>
                      </td>
                      <td className="py-2">
                        <span className={`rounded-md px-1.5 py-0.5 ${
                          item.status === "implemented"
                            ? "bg-emerald-50 text-emerald-700"
                            : item.status === "partial"
                              ? "bg-amber-50 text-amber-700"
                              : "bg-slate-100 text-slate-500"
                        }`}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}

        <section className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">如何新增连接</h2>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">1. 建页面</b>
              <p className="mt-1 text-xs text-slate-500">在 frontend/src/app 下创建路由，复用 AppShell。</p>
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">2. 接 API</b>
              <p className="mt-1 text-xs text-slate-500">在 frontend/src/lib/operations 或 realm-owner 增加真实接口。</p>
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">3. 登记连接</b>
              <p className="mt-1 text-xs text-slate-500">在 code-connection.ts 登记路由、组件、API 和状态。</p>
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}

function surfaceLabel(surfaceId: string): string {
  const labels: Record<string, string> = {
    owner: "域主工作台",
    public: "公共世界与客户协作端",
    operations: "平台运营后台",
    governance: "治理审计台",
  };
  return labels[surfaceId] || surfaceId;
}
