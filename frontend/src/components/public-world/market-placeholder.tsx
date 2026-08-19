"use client";

import { useEffect, useState } from "react";
import { Lock, ShieldCheck } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

interface PublicCapability {
  capability_id: string;
  name: string;
  capability_type: string;
  source_mode: string;
  provider: string;
  description: string | null;
  available: boolean;
}

export default function MarketPlaceholder() {
  const [capabilities, setCapabilities] = useState<PublicCapability[]>([]);
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/capabilities/public`)
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error("capabilities unavailable"))))
      .then((data: { capabilities?: PublicCapability[] }) => {
        if (cancelled) return;
        setCapabilities(data.capabilities || []);
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
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">能力市场</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        <a href="/public" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">公开世界</a>
        <a href="/intake" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">资料提交</a>
        <a href="/client" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">客户协作</a>
        <a href="/market" className="mb-1 block rounded-md bg-[color:var(--v106-primary-weak)] px-2.5 py-2 text-sm font-medium text-[color:var(--v106-primary-strong)]">能力市场</a>
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        能力市场在第三阶段开放。
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="public"
      featureFlags={["market"]}
      navRail={navRail}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <span className="text-xs text-slate-500">公共世界 / 能力市场</span>
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "Feature Flag", value: "hidden", tone: "warning" },
            { label: "阶段", value: "第三阶段开放" },
            { label: "边界", value: "不建空壳页面" },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-4xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-[color:var(--v106-warning)]" aria-hidden="true" />
            <h1 className="v106-page-title">能力市场</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">能力发现、评估和获得授权；当前阶段不开放空壳页面。</p>
        </header>
        <section className="v106-panel mb-4 p-4">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold text-slate-800">平台标准能力</h2>
            <span className="text-xs text-slate-500">真实能力目录</span>
          </div>
          {phase === "loading" && <ModuleState variant="loading" title="正在加载能力目录" />}
          {phase === "error" && <ModuleState variant="error" title="能力目录接口不可用" compact />}
          {phase === "ready" && capabilities.length === 0 && (
            <ModuleState variant="empty" title="暂无公开能力" description="平台标准能力配置后自动出现。" compact />
          )}
          {phase === "ready" && capabilities.length > 0 && (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
              {capabilities.map((capability) => (
                <div key={capability.capability_id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                  <div className="flex items-center justify-between gap-2">
                    <b className="text-sm font-medium text-slate-800">{capability.name}</b>
                    <span className={`rounded-md px-1.5 py-0.5 text-[11px] ${capability.available ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                      {capability.available ? "可用" : "未配置"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{capability.capability_type} · {capability.source_mode} · {capability.provider}</p>
                  {capability.description && <p className="mt-2 text-xs leading-5 text-slate-600">{capability.description}</p>}
                </div>
              ))}
            </div>
          )}
        </section>
        <ModuleState
          variant="blocked"
          title="市场交易未开放"
          description="能力发现已开放，授权购买与收益分配在第三阶段真实能力包跑通后开放。"
        />
      </div>
    </AppShell>
  );
}
