"use client";

import { useEffect, useState } from "react";
import { Database, Lock } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import { getToken } from "@/lib/authFetch";
import { fetchOperationsDbStats, fetchOperationsHealth } from "@/lib/operations/api";
import type { OperationsDbStats, OperationsHealth } from "@/lib/operations/types";

type BackendId = "data" | "runtime" | "security" | "primitives" | "flow";

const BASES: Array<{ id: BackendId; label: string; title: string; sub: string; rows: Array<[string, string]> }> = [
  { id: "data", label: "数据事件底座", title: "数据、事件与平台底座", sub: "存储、搜索、向量、事件、队列、快照", rows: [
    ["PostgreSQL", "主数据存储：Realm、Project、Evidence、Capability、World State"],
    ["对象存储 / 搜索 / 向量", "文件、检索、语义"],
    ["Event Backbone / Queue / Scheduler", "事件流、异步、定时任务"],
    ["Snapshot / 备份恢复", "World State 快照、数据回滚"],
  ] },
  { id: "runtime", label: "运行底座", title: "Agent 与工作流运行底座", sub: "Runtime、Memory、Citation、Sandbox、Approval", rows: [
    ["Agent Runtime", "执行 Agent，记录输入、输出、版本、引用、成本"],
    ["Workflow Runtime", "执行步骤、条件和人工确认点"],
    ["Tool Execution", "工具调用、重试、幂等、降级"],
    ["Observability", "日志、指标、可观测性"],
  ] },
  { id: "security", label: "连接安全底座", title: "外部连接与安全底座", sub: "MCP、Adapter、Webhook、Secret、SSRF", rows: [
    ["MCP / Adapter / API", "连接外部平台、工具和数据源"],
    ["Webhook / Callback", "异步回调和事件"],
    ["Credential / Secret", "密钥只存后端，不进前端"],
    ["Rate Limit / SSRF / 数据出境", "限流、请求安全、跨域受控"],
  ] },
  { id: "primitives", label: "四原语原则", title: "四原语运行原则", sub: "Agent、Skills、Workflows、MCP 可配置闭环", rows: [
    ["Agent", "可配置角色、工具、模型、预算、权限"],
    ["Skills", "可配置技能包、版本、来源、授权"],
    ["Workflows", "可配置步骤、条件、人工确认点"],
    ["MCP", "可配置连接、工具、资源、密钥策略"],
    ["统一闭环", "目录 → 配置 → 授权 → 运行 → 记录 → 复盘 → 资产"],
  ] },
  { id: "flow", label: "统一执行审计流", title: "统一执行与审计流", sub: "用户操作到外部服务，全程记录与安全控制", rows: [
    ["输入", "用户、Realm、项目、授权范围"],
    ["执行", "Agent / Workflow / Tool / MCP 调用"],
    ["输出", "结果、版本、引用、成本"],
    ["可信", "verified / observed / inferred / unknown / simulation"],
    ["安全", "密钥脱敏、限流、SSRF、数据出境"],
  ] },
];

export default function BackendConsole() {
  const [view, setView] = useState<BackendId>("data");
  const [phase, setPhase] = useState<"loading" | "ready" | "no-permission">("loading");
  const [health, setHealth] = useState<OperationsHealth | null>(null);
  const [dbStats, setDbStats] = useState<OperationsDbStats | null>(null);

  useEffect(() => {
    if (!getToken()) {
      window.location.assign("/login?next=/backend");
      return;
    }
    let cancelled = false;
    void Promise.allSettled([fetchOperationsHealth(), fetchOperationsDbStats()]).then(
      ([healthResult, statsResult]) => {
        if (cancelled) return;
        if (healthResult.status === "rejected") {
          setPhase("no-permission");
          return;
        }
        setHealth(healthResult.value);
        setDbStats(statsResult.status === "fulfilled" ? statsResult.value : null);
        setPhase("ready");
      },
    );
    return () => {
      cancelled = true;
    };
  }, []);

  const current = BASES.find((item) => item.id === view) || BASES[0];
  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <Database className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">后端基础设施</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        {BASES.map((item) => {
          const active = item.id === view;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => setView(item.id)}
              className={`mb-1 flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-left text-sm ${
                active
                  ? "bg-[color:var(--v106-primary-weak)] font-medium text-[color:var(--v106-primary-strong)]"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        3 个底座 · 4 原语可配置 · 全程审计
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="operations"
      featureFlags={["backend"]}
      userContext={{ label: "运营者", permissions: ["operations_read"] }}
      navRail={navRail}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
            后端基础设施 <span className="mx-1 text-slate-300">/</span> {current.label}
          </div>
          <DataSourceBadge name="后端" state={phase === "ready" ? "connected" : phase === "no-permission" ? "blocked" : "pending"} />
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "后端", value: health?.status === "ok" ? "已连接" : "未连接" },
            { label: "数据表", value: dbStats ? String(dbStats.total) : "未知" },
            { label: "底座", value: String(BASES.length) },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">{current.title}</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">{current.sub}</p>
        </header>
        {phase === "loading" && <ModuleState variant="loading" title="正在加载后端基础设施" />}
        {phase === "no-permission" && (
          <ModuleState variant="no-permission" title="需要运营权限" description="当前账号无权查看后端基础设施。" />
        )}
        {phase === "ready" && (
          <section className="v106-panel p-4">
            <table className="w-full text-left text-xs">
              <tbody>
                {current.rows.map(([label, value]) => (
                  <tr key={label} className="border-b border-[color:var(--v106-border)] last:border-0">
                    <td className="w-40 py-2.5 pr-4 font-medium text-slate-600">{label}</td>
                    <td className="py-2.5 text-slate-800">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </div>
    </AppShell>
  );
}
