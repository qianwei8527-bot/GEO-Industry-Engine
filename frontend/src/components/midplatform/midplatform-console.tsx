"use client";

import { useEffect, useState } from "react";
import { Boxes, ShieldCheck } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import { getToken } from "@/lib/authFetch";
import { fetchOperationsDbStats, fetchOperationsHealth } from "@/lib/operations/api";
import type { OperationsDbStats, OperationsHealth } from "@/lib/operations/types";

type PlatformId =
  | "identity"
  | "project"
  | "workflow"
  | "evidence"
  | "demand"
  | "assets"
  | "policy"
  | "world"
  | "governance"
  | "tools";

const PLATFORMS: Array<{ id: PlatformId; label: string; title: string; sub: string; rows: Array<[string, string]> }> = [
  { id: "identity", label: "身份与域权", title: "身份与域权中台", sub: "Realm、Entity、成员和权限的唯一真相源", rows: [
    ["定位", "统一 Realm 身份链与权限"],
    ["核心实体", "Realm、Entity、Membership、ControlGrant、Role"],
    ["主要 API", "/realm、/entities、/membership、/permission"],
    ["可配置", "角色、权限策略、认领状态机"],
    ["边界", "前端不自行判断身份，所有权限走后端"],
  ] },
  { id: "project", label: "项目与执行", title: "项目与执行中台", sub: "项目、计划、任务、进度、提醒", rows: [
    ["定位", "真实项目闭环"],
    ["核心实体", "GeoProject、WorkItem、Reminder、Progress"],
    ["主要 API", "/geo-projects、/execution/projects/{id}/plan"],
    ["可配置", "项目模板、阶段、任务模板、提醒规则"],
    ["边界", "不建立第二套 Task 体系"],
  ] },
  { id: "workflow", label: "工作流与 Agent", title: "工作流与 Agent 中台", sub: "Workflow、Agent 配置、工具执行", rows: [
    ["定位", "可配置执行能力"],
    ["核心实体", "Workflow、AgentConfig、ToolExecutionRecord"],
    ["主要 API", "/agent/list、/capabilities/runs、tool-executions"],
    ["可配置", "Agent 角色、工具、模型、预算、权限"],
    ["边界", "工作流归域主，平台负责运行、版本和审计"],
  ] },
  { id: "evidence", label: "证据与可信", title: "证据与可信中台", sub: "Evidence、Claim、Outcome、信誉", rows: [
    ["定位", "可信事实与证据链"],
    ["核心实体", "Evidence、EvidenceClaim、Outcome、Reputation"],
    ["主要 API", "/evidence、/claims、/trust"],
    ["可配置", "验证规则、信誉规则、truth scope 映射"],
    ["边界", "observed 不得显示为 verified"],
  ] },
  { id: "demand", label: "需求与连接", title: "需求与连接中台", sub: "真实需求、连接候选、合作记录", rows: [
    ["定位", "需求到连接"],
    ["核心实体", "DemandEvent、ConnectionCandidate、Engagement"],
    ["主要 API", "/demand、/connection、/engagement"],
    ["可配置", "匹配策略、候选展示规则"],
    ["边界", "候选必须带理由、证据、风险和未知项"],
  ] },
  { id: "assets", label: "资产与能力包", title: "资产与能力包中台", sub: "SOP、Skill、Method、能力包和授权", rows: [
    ["定位", "域主资产化"],
    ["核心实体", "CapabilityDefinition、CapabilityPackage、LicenseTerm"],
    ["主要 API", "/capabilities、/capabilities/runs"],
    ["可配置", "版本、来源、适用条件、授权、收益规则"],
    ["边界", "模板只能来自真实有效方法，需域主确认"],
  ] },
  { id: "policy", label: "政策与综合经营", title: "政策与综合经营中台", sub: "政策、财务、税务、法务、合同、现金流", rows: [
    ["定位", "综合经营能力"],
    ["核心实体", "PolicySource、PolicyEvent、Jurisdiction、FinancialSnapshot"],
    ["预留实体", "TaxProfile、ContractRecord、CashflowSnapshot、Budget"],
    ["可配置", "适用地区、政策版本、风险边界"],
    ["边界", "高风险财税法决策必须专业审核人确认"],
  ] },
  { id: "world", label: "行业态势", title: "行业态势中台", sub: "World State、行业事件、信号和缺口", rows: [
    ["定位", "行业现实"],
    ["核心实体", "WorldContract、WorldStateSnapshot、IndustryEvent"],
    ["主要 API", "/universe/world-state/snapshots、/worlds"],
    ["可配置", "覆盖范围、快照范围、信号规则"],
    ["边界", "推断必须标记，未知区必须显示缺口"],
  ] },
  { id: "governance", label: "治理与审计", title: "治理与审计中台", sub: "事件、审计、审批、共同治理", rows: [
    ["定位", "治理与审计"],
    ["核心实体", "EventBackbone、AuditLog、Approval、GovernanceProposal"],
    ["主要 API", "/event、/audit、/approval、/governance"],
    ["可配置", "审批流、风险分级、审计保留期"],
    ["边界", "所有外部动作和权限变更留痕"],
  ] },
  { id: "tools", label: "工具与连接", title: "工具与连接中台", sub: "MCP、Adapter、外部平台连接", rows: [
    ["定位", "连接层"],
    ["核心实体", "Connector、MCP Server、Adapter、CredentialPolicy"],
    ["主要 API", "/mcp/tools、/providers、/connector"],
    ["可配置", "连接、工具、资源、密钥策略、限流"],
    ["边界", "外部平台不得成为不可替换核心，密钥不进前端"],
  ] },
];

export default function MidPlatformConsole() {
  const [view, setView] = useState<PlatformId>("identity");
  const [phase, setPhase] = useState<"loading" | "ready" | "no-permission">("loading");
  const [health, setHealth] = useState<OperationsHealth | null>(null);
  const [dbStats, setDbStats] = useState<OperationsDbStats | null>(null);

  useEffect(() => {
    if (!getToken()) {
      window.location.assign("/login?next=/midplatform");
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

  const current = PLATFORMS.find((item) => item.id === view) || PLATFORMS[0];
  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <Boxes className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">中台能力域</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        {PLATFORMS.map((item) => {
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
        10 个中台 · 统一领域模型和 API
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="operations"
      featureFlags={["midplatform"]}
      userContext={{ label: "运营者", permissions: ["operations_read"] }}
      navRail={navRail}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
            中台能力域 <span className="mx-1 text-slate-300">/</span> {current.label}
          </div>
          <DataSourceBadge name="后端" state={phase === "ready" ? "connected" : phase === "no-permission" ? "blocked" : "pending"} />
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "后端", value: health?.status === "ok" ? "已连接" : "未连接" },
            { label: "数据表", value: dbStats ? String(dbStats.total) : "未知" },
            { label: "中台", value: String(PLATFORMS.length) },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">{current.title}</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">{current.sub}</p>
        </header>
        {phase === "loading" && <ModuleState variant="loading" title="正在加载中台能力域" />}
        {phase === "no-permission" && (
          <ModuleState variant="no-permission" title="需要运营权限" description="当前账号无权查看中台能力域。" />
        )}
        {phase === "ready" && (
          <section className="v106-panel p-4">
            <table className="w-full text-left text-xs">
              <tbody>
                {current.rows.map(([label, value]) => (
                  <tr key={label} className="border-b border-[color:var(--v106-border)] last:border-0">
                    <td className="w-32 py-2.5 pr-4 font-medium text-slate-600">{label}</td>
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
