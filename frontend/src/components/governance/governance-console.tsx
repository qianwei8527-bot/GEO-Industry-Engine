"use client";

import { useEffect, useState } from "react";
import { FileText, Lock, ScrollText, ShieldCheck, Users } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import { getToken } from "@/lib/authFetch";
import { fetchApprovals, fetchAuditLogs, type ApprovalItem, type AuditLogItem } from "@/lib/governance/api";
import { fetchOperationsDbStats, fetchOperationsHealth } from "@/lib/operations/api";
import type { OperationsDbStats, OperationsHealth } from "@/lib/operations/types";

type GovernanceView = "permissions" | "approvals" | "audit" | "risk" | "collective";

const NAV: Array<{ id: GovernanceView; label: string; icon: typeof Users }> = [
  { id: "permissions", label: "权限策略", icon: Users },
  { id: "approvals", label: "审批中心", icon: ShieldCheck },
  { id: "audit", label: "审计日志", icon: ScrollText },
  { id: "risk", label: "风险控制", icon: Lock },
  { id: "collective", label: "共同治理", icon: FileText },
];

export default function GovernanceConsole() {
  const [view, setView] = useState<GovernanceView>("permissions");
  const [phase, setPhase] = useState<"loading" | "ready" | "no-permission" | "error">("loading");
  const [health, setHealth] = useState<OperationsHealth | null>(null);
  const [dbStats, setDbStats] = useState<OperationsDbStats | null>(null);
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);

  useEffect(() => {
    if (!getToken()) {
      window.location.assign("/login?next=/governance");
      return;
    }
    let cancelled = false;
    void Promise.allSettled([
      fetchOperationsHealth(),
      fetchOperationsDbStats(),
      fetchApprovals(),
      fetchAuditLogs(),
    ]).then(
      ([healthResult, statsResult, approvalResult, auditResult]) => {
        if (cancelled) return;
        if (healthResult.status === "rejected") {
          setPhase("no-permission");
          return;
        }
        setHealth(healthResult.value);
        setDbStats(statsResult.status === "fulfilled" ? statsResult.value : null);
        setApprovals(approvalResult.status === "fulfilled" ? approvalResult.value.approvals : []);
        setAuditLogs(auditResult.status === "fulfilled" ? auditResult.value.logs : []);
        setPhase("ready");
      },
    );
    return () => {
      cancelled = true;
    };
  }, []);

  const current = NAV.find((item) => item.id === view) || NAV[0];
  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">治理审计台</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        {NAV.map((item) => {
          const Icon = item.icon;
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
              <Icon className="h-4 w-4" aria-hidden="true" />
              {item.label}
            </button>
          );
        })}
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        权限真相源：node_memberships + ControlGrant。
      </div>
    </aside>
  );

  const contextBar = (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
      <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
        治理审计台 <span className="mx-1 text-slate-300">/</span> {current.label}
      </div>
      <DataSourceBadge name="后端" state={phase === "ready" ? "connected" : phase === "error" ? "blocked" : "pending"} />
    </header>
  );

  function renderView() {
    if (view === "permissions") {
      return (
        <div className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">权限策略</h2>
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                <th className="pb-2 pr-3 font-medium">角色</th>
                <th className="pb-2 pr-3 font-medium">范围</th>
                <th className="pb-2 pr-3 font-medium">读写</th>
                <th className="pb-2 font-medium">真相源</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["域主", "Realm", "读 + 写", "node_memberships"],
                ["运营者", "平台", "读 + 配置", "node_memberships"],
                ["治理者", "平台", "读 + 审批", "node_memberships"],
                ["客户", "项目", "只读 + 反馈", "RealmDataAuthorization"],
              ].map((row) => (
                <tr key={row[0]} className="border-b border-[color:var(--v106-border)] last:border-0">
                  {row.map((cell) => (
                    <td key={cell} className="py-2 pr-3">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    if (view === "approvals") {
      return approvals.length > 0 ? (
        <div className="v106-panel overflow-x-auto p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">审批队列</h2>
          <table className="w-full min-w-[640px] text-left text-xs">
            <thead>
              <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                <th className="pb-2 pr-3 font-medium">实体</th>
                <th className="pb-2 pr-3 font-medium">类型</th>
                <th className="pb-2 pr-3 font-medium">理由</th>
                <th className="pb-2 font-medium">时间</th>
              </tr>
            </thead>
            <tbody>
              {approvals.map((item) => (
                <tr key={item.id} className="border-b border-[color:var(--v106-border)] last:border-0">
                  <td className="py-2 pr-3 font-mono text-slate-600">{item.entity_id}</td>
                  <td className="py-2 pr-3">{item.claim_type}</td>
                  <td className="py-2 pr-3">{item.reason || "--"}</td>
                  <td className="py-2">{item.created_at || "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <ModuleState variant="empty" title="暂无审批项" description="高风险动作和中风险发布会进入这里；禁止动作永不自动执行。" />
      );
    }
    if (view === "audit") {
      return auditLogs.length > 0 ? (
        <div className="v106-panel overflow-x-auto p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">审计日志</h2>
          <table className="w-full min-w-[720px] text-left text-xs">
            <thead>
              <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                <th className="pb-2 pr-3 font-medium">时间</th>
                <th className="pb-2 pr-3 font-medium">动作</th>
                <th className="pb-2 pr-3 font-medium">对象</th>
                <th className="pb-2 pr-3 font-medium">操作者</th>
                <th className="pb-2 font-medium">结果</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((item) => (
                <tr key={item.id} className="border-b border-[color:var(--v106-border)] last:border-0">
                  <td className="py-2 pr-3">{item.occurred_at || "--"}</td>
                  <td className="py-2 pr-3">{item.action}</td>
                  <td className="py-2 pr-3">{item.target_type || "--"}</td>
                  <td className="py-2 pr-3">{item.actor_label || "--"}</td>
                  <td className="py-2">{item.result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <ModuleState variant="empty" title="暂无审计日志" description="Event Backbone 和 AuditLog 接入后，这里会展示真实事件流。" />
      );
    }
    if (view === "risk") {
      return (
        <div className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">风险控制</h2>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {[
              ["未验证数据", "不得对外展示"],
              ["外部工具", "低/中/高三级授权"],
              ["密钥", "只存后端，不进前端"],
            ].map(([title, desc]) => (
              <div key={title} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <b className="text-sm font-medium text-slate-800">{title}</b>
                <p className="mt-1 text-xs text-slate-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return (
      <ModuleState
        variant="blocked"
        title="共同治理未开放"
        description="GovernanceProposal 和 CollectiveDecision 在第四阶段试点开放。"
      />
    );
  }

  return (
    <AppShell
      surface="governance"
      featureFlags={["governance"]}
      userContext={{ label: "治理者", permissions: ["governance_read"] }}
      navRail={navRail}
      contextBar={contextBar}
      statusStrip={
        <StatusStrip
          items={[
            { label: "后端", value: health?.status === "ok" ? "已连接" : "未连接" },
            { label: "数据表", value: dbStats ? String(dbStats.total) : "未知" },
            { label: "权限真相源", value: "node_memberships" },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">{current.label}</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">治理、审计和风险控制，所有外部动作和权限变更留痕。</p>
        </header>
        {phase === "loading" && <ModuleState variant="loading" title="正在加载治理审计台" />}
        {phase === "no-permission" && (
          <ModuleState variant="no-permission" title="需要治理权限" description="当前账号无权访问治理审计台。" />
        )}
        {phase === "ready" && renderView()}
      </div>
    </AppShell>
  );
}
