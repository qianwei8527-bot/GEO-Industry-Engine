"use client";

import { useEffect, useState } from "react";
import { Compass, FilePlus, Globe, Landmark, Link2, ShieldCheck } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

interface PublicSnapshot {
  snapshot_id: string;
  world_code: string;
  world_version: string;
  state_scope: string;
  created_at: string | null;
}

export default function PublicWorldHub() {
  const [snapshots, setSnapshots] = useState<PublicSnapshot[]>([]);
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/universe/world-state/snapshots`)
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error("snapshots unavailable"))))
      .then((data: { snapshots?: PublicSnapshot[] }) => {
        if (cancelled) return;
        setSnapshots(data.snapshots || []);
        setPhase("ready");
      })
      .catch(() => {
        if (!cancelled) setPhase("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <Globe className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">公共世界</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        <a href="/public" className="mb-1 flex items-center gap-2 rounded-md bg-[color:var(--v106-primary-weak)] px-2.5 py-2 text-sm font-medium text-[color:var(--v106-primary-strong)]">
          <Landmark className="h-4 w-4" aria-hidden="true" />
          公开世界
        </a>
        <a href="/intake" className="mb-1 flex items-center gap-2 rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">
          <FilePlus className="h-4 w-4" aria-hidden="true" />
          资料提交
        </a>
        <a href="/client" className="mb-1 flex items-center gap-2 rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">
          <Link2 className="h-4 w-4" aria-hidden="true" />
          客户协作
        </a>
        <a href="/market" className="mb-1 flex items-center gap-2 rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          能力市场
        </a>
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        公开内容只展示已验证或已观察结果。
      </div>
    </aside>
  );

  const contextBar = (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
      <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
        公共世界 <span className="mx-1 text-slate-300">/</span> 公开世界
      </div>
      <DataSourceBadge name="World Snapshot" state={phase === "ready" ? "connected" : phase === "error" ? "blocked" : "pending"} />
    </header>
  );

  return (
    <AppShell
      surface="public"
      featureFlags={["public"]}
      navRail={navRail}
      contextBar={contextBar}
      statusStrip={
        <StatusStrip
          items={[
            { label: "数据连接", value: phase === "ready" ? "已连接" : phase === "error" ? "未连接" : "检查中" },
            { label: "公开范围", value: "仅真实结果" },
            { label: "truth scope", value: "verified / observed" },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">公开世界</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">公开行业、域、主体、案例和能力展示；未验证数据不对外展示。</p>
        </header>

        <section className="v106-panel mb-4 p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">公开能力方向</h2>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">行业世界</b>
              <p className="mt-1 text-xs text-slate-500">GEO 是首个行业世界，域由真实主体和真实关系构成。</p>
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">可信结果</b>
              <p className="mt-1 text-xs text-slate-500">只展示已验证或已观察的案例和交付物。</p>
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">能力展示</b>
              <p className="mt-1 text-xs text-slate-500">能力包、SOP、Skill 需要域主确认后才对外。</p>
            </div>
          </div>
        </section>

        <section className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">World Snapshot</h2>
          {phase === "loading" && <ModuleState variant="loading" title="正在加载公开快照" />}
          {phase === "error" && <ModuleState variant="error" title="World Snapshot 接口不可用" compact />}
          {phase === "ready" && snapshots.length === 0 && (
            <ModuleState variant="empty" title="尚无公开快照" description="World State 生成后才会出现真实快照。" compact />
          )}
          {phase === "ready" && snapshots.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-xs">
                <thead>
                  <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                    <th className="pb-2 pr-3 font-medium">World</th>
                    <th className="pb-2 pr-3 font-medium">版本</th>
                    <th className="pb-2 pr-3 font-medium">范围</th>
                    <th className="pb-2 font-medium">时间</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshots.map((snapshot) => (
                    <tr key={snapshot.snapshot_id} className="border-b border-[color:var(--v106-border)] last:border-0">
                      <td className="py-2 pr-3">{snapshot.world_code}</td>
                      <td className="py-2 pr-3">{snapshot.world_version}</td>
                      <td className="py-2 pr-3">{snapshot.state_scope}</td>
                      <td className="py-2">{snapshot.created_at || "--"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}
