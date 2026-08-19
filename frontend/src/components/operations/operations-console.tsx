"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bot,
  FileText,
  Globe,
  Info,
  LayoutDashboard,
  PlugZap,
  Settings,
  ShieldCheck,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import RealmDrawer from "@/components/realm-owner/drawer";
import { getToken } from "@/lib/authFetch";
import {
  fetchOperationsAgents,
  fetchOperationsCapabilities,
  fetchOperationsConfigs,
  fetchOperationsDbStats,
  fetchOperationsHealth,
  fetchOperationsProviders,
  fetchOperationsRuns,
  fetchOperationsSnapshots,
  fetchOperationsTools,
  OperationsApiError,
} from "@/lib/operations/api";
import type {
  AsyncStatus,
  AsyncValue,
  OperationsDataState,
  OperationsView,
} from "@/lib/operations/types";

const NAV_ITEMS: Array<{ id: OperationsView; label: string; icon: LucideIcon }> = [
  { id: "overview", label: "平台总览", icon: LayoutDashboard },
  { id: "runtime", label: "运行任务", icon: Activity },
  { id: "connectors", label: "工具与连接", icon: PlugZap },
  { id: "capabilities", label: "Agent 与能力", icon: Bot },
  { id: "workflows", label: "工作流", icon: Workflow },
  { id: "reports", label: "报告与结果", icon: FileText },
  { id: "intelligence", label: "行业态势", icon: Globe },
  { id: "system", label: "系统与配置", icon: Settings },
];

const FEATURE_FLAGS = [
  { id: "owner", label: "域主工作台", status: "open" },
  { id: "public", label: "公共世界与客户协作端", status: "open" },
  { id: "operations", label: "平台运营后台", status: "open" },
  { id: "governance", label: "治理审计台", status: "reserved" },
  { id: "policy", label: "政策与经营", status: "hidden" },
  { id: "market", label: "能力市场", status: "hidden" },
  { id: "intel", label: "行业态势", status: "hidden" },
  { id: "collective", label: "共同治理", status: "hidden" },
];

function initialDataState(): OperationsDataState {
  return {
    phase: "loading",
    health: { status: "loading", data: null },
    dbStats: { status: "loading", data: null },
    configs: { status: "loading", data: null },
    agents: { status: "loading", data: null },
    tools: { status: "loading", data: null },
    providers: { status: "loading", data: null },
    capabilities: { status: "loading", data: null },
    runs: { status: "loading", data: null },
    snapshots: { status: "loading", data: null },
  };
}

async function wrap<T>(promise: Promise<T>): Promise<AsyncValue<T>> {
  try {
    return { status: "ok", data: await promise };
  } catch (err) {
    const status: AsyncStatus =
      err instanceof OperationsApiError && (err.status === 401 || err.status === 403)
        ? "no-permission"
        : "error";
    return {
      status,
      data: null,
      message: err instanceof Error ? err.message : "请求失败",
    };
  }
}

function SourceState({
  record,
  emptyTitle,
  emptyDescription,
  errorTitle,
}: {
  record: AsyncValue<unknown>;
  emptyTitle: string;
  emptyDescription: string;
  errorTitle: string;
}) {
  if (record.status === "no-permission") {
    return (
      <ModuleState
        variant="no-permission"
        title="无运营后台权限"
        description="当前账号未获得平台运营后台访问权限。"
        compact
      />
    );
  }
  if (record.status === "error") {
    return (
      <ModuleState
        variant="error"
        title={errorTitle}
        description={record.message || "接口请求失败"}
        compact
      />
    );
  }
  if (record.status === "empty") {
    return <ModuleState variant="empty" title={emptyTitle} description={emptyDescription} compact />;
  }
  return null;
}

export default function OperationsConsole() {
  const [view, setView] = useState<OperationsView>("overview");
  const [data, setData] = useState<OperationsDataState>(initialDataState);
  const [notice, setNotice] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      window.location.assign("/login?next=/operations");
      return;
    }
    let cancelled = false;
    void Promise.all([
      wrap(fetchOperationsHealth()),
      wrap(fetchOperationsDbStats()),
      wrap(fetchOperationsConfigs()),
      wrap(fetchOperationsAgents()),
      wrap(fetchOperationsTools()),
      wrap(fetchOperationsProviders()),
      wrap(fetchOperationsCapabilities()),
      wrap(fetchOperationsRuns()),
      wrap(fetchOperationsSnapshots()),
    ]).then(([health, dbStats, configs, agents, tools, providers, capabilities, runs, snapshots]) => {
      if (cancelled) return;
      setData({
        phase: "ready",
        health,
        dbStats,
        configs,
        agents,
        tools,
        providers,
        capabilities,
        runs,
        snapshots,
      });
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const currentNav = NAV_ITEMS.find((item) => item.id === view) || NAV_ITEMS[0];
  const statusItems = useMemo(
    () => [
      {
        label: "后端",
        value:
          data.health.status === "ok" && data.health.data?.status === "ok"
            ? "已连接"
            : data.health.status === "error" || data.health.status === "no-permission"
              ? "未连接"
              : "检查中",
        tone: data.health.status === "ok" ? ("success" as const) : ("warning" as const),
      },
      {
        label: "数据表",
        value: data.dbStats.status === "ok" ? String(data.dbStats.data?.total ?? 0) : "未知",
        tone: data.dbStats.status === "ok" ? ("success" as const) : ("neutral" as const),
      },
      { label: "Feature Flag", value: data.phase === "ready" ? "运营后台开放" : "待确认" },
      { label: "truth scope", value: "observed / inferred / unknown" },
      { label: "版本", value: "V10.6 运营原型" },
    ],
    [data],
  );

  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">平台运营后台</span>
      </div>
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = view === item.id;
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
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] leading-4 text-slate-500">
        只读运营原型，真实数据优先，模拟数据不对外展示。
      </div>
    </aside>
  );

  const mobileNav = (
    <div className="flex gap-2 overflow-x-auto border-b border-[color:var(--v106-border)] bg-white px-3 py-2 md:hidden">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const active = view === item.id;
        return (
          <button
            key={item.id}
            type="button"
            onClick={() => setView(item.id)}
            className={`inline-flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs ${
              active
                ? "bg-[color:var(--v106-primary-weak)] font-medium text-[color:var(--v106-primary-strong)]"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            {item.label}
          </button>
        );
      })}
    </div>
  );

  const contextBar = (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
      <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
        平台运营后台 <span className="mx-1 text-slate-300">/</span> {currentNav.label}
      </div>
      <DataSourceBadge
        name="后端"
        state={data.health.status === "ok" ? "connected" : data.health.status === "error" || data.health.status === "no-permission" ? "blocked" : "pending"}
      />
      <button
        type="button"
        onClick={() => setDrawerOpen(true)}
        className="inline-flex h-8 items-center gap-1.5 rounded-md border border-[color:var(--v106-border)] bg-white px-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
      >
        <Info className="h-4 w-4" aria-hidden="true" />
        运营说明
      </button>
    </header>
  );

  function renderOverview() {
    const sourceRows = [
      { name: "后端健康", record: data.health, empty: "尚无健康状态", label: "health" },
      { name: "数据表统计", record: data.dbStats, empty: "尚无数据表统计", label: "db-stats" },
      { name: "配置文件", record: data.configs, empty: "尚无配置", label: "configs" },
      { name: "Agent 注册", record: data.agents, empty: "尚无 Agent 注册", label: "agents" },
      { name: "MCP 工具", record: data.tools, empty: "尚无 MCP 工具", label: "mcp" },
      { name: "Provider", record: data.providers, empty: "尚无 Provider", label: "providers" },
      { name: "能力资产", record: data.capabilities, empty: "尚无能力资产", label: "capabilities" },
      { name: "运行记录", record: data.runs, empty: "尚无运行记录", label: "runs" },
      { name: "World 快照", record: data.snapshots, empty: "尚无 World 快照", label: "snapshots" },
    ];
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">平台总览</h1>
          <p className="mt-1 text-sm text-slate-500">只读聚合，不承载编辑；缺失接口保留真实空状态。</p>
        </header>
        <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatCard
            label="数据表总数"
            value={data.dbStats.status === "ok" ? String(data.dbStats.data?.total ?? 0) : "--"}
            icon={LayoutDashboard}
          />
          <StatCard
            label="配置文件"
            value={data.configs.status === "ok" ? String(Object.keys(data.configs.data || {}).length) : "--"}
            icon={FileText}
          />
          <StatCard
            label="Agent"
            value={data.agents.status === "ok" ? String(data.agents.data?.length ?? 0) : "--"}
            icon={Bot}
          />
          <StatCard
            label="MCP 工具"
            value={data.tools.status === "ok" ? String(data.tools.data?.length ?? 0) : "--"}
            icon={PlugZap}
          />
        </div>
        <section className="v106-panel mb-4 p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">真实数据源状态</h2>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
            {sourceRows.map((row) => (
              <div key={row.label} className="flex items-center justify-between gap-2 rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-2">
                <span className="text-xs text-slate-600">{row.name}</span>
                <DataSourceBadge
                  name={row.label}
                  state={row.record.status === "ok" ? "connected" : row.record.status === "empty" ? "pending" : row.record.status === "error" || row.record.status === "no-permission" ? "blocked" : "pending"}
                />
              </div>
            ))}
          </div>
        </section>
        <section className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">Feature Flag</h2>
          <div className="flex flex-wrap gap-2">
            {FEATURE_FLAGS.map((flag) => (
              <span
                key={flag.id}
                className={`inline-flex items-center rounded-md border px-2 py-1 text-xs ${
                  flag.status === "open"
                    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                    : flag.status === "reserved"
                      ? "border-amber-200 bg-amber-50 text-amber-700"
                      : "border-slate-200 bg-slate-50 text-slate-500"
                }`}
              >
                {flag.label} · {flag.status}
              </span>
            ))}
          </div>
        </section>
      </div>
    );
  }

  function renderRuntime() {
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">运行任务与接口监控</h1>
          <p className="mt-1 text-sm text-slate-500">能力运行记录来自真实 ToolExecutionRecord。</p>
        </header>
        {data.runs.status === "ok" && data.runs.data && data.runs.data.length > 0 ? (
          <section className="v106-panel mb-4 overflow-x-auto p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">能力运行记录</h2>
            <table className="w-full min-w-[720px] text-left text-xs">
              <thead>
                <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                  <th className="pb-2 pr-3 font-medium">执行码</th>
                  <th className="pb-2 pr-3 font-medium">能力</th>
                  <th className="pb-2 pr-3 font-medium">工具</th>
                  <th className="pb-2 pr-3 font-medium">来源</th>
                  <th className="pb-2 pr-3 font-medium">执行状态</th>
                  <th className="pb-2 pr-3 font-medium">truth</th>
                  <th className="pb-2 font-medium">时间</th>
                </tr>
              </thead>
              <tbody>
                {data.runs.data.map((run) => (
                  <tr key={run.id} className="border-b border-[color:var(--v106-border)] last:border-0">
                    <td className="py-2 pr-3 font-mono text-slate-600">{run.execution_code}</td>
                    <td className="py-2 pr-3">{run.capability_type || run.tool_name}</td>
                    <td className="py-2 pr-3">{run.tool_name}</td>
                    <td className="py-2 pr-3">{run.source_mode}</td>
                    <td className="py-2 pr-3">{run.execution_status}</td>
                    <td className="py-2 pr-3">{run.truth_status}</td>
                    <td className="py-2">{run.created_at || "--"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        ) : (
          <div className="mb-4">
            <SourceState
              record={data.runs}
              emptyTitle="尚无真实运行记录"
              emptyDescription="能力执行后这里会出现真实 ToolExecutionRecord。"
              errorTitle="运行记录接口不可用"
            />
          </div>
        )}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <AgentPanel data={data.agents} />
          <ToolPanel data={data.tools} />
        </div>
      </div>
    );
  }

  function renderConnectors() {
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">工具与连接</h1>
          <p className="mt-1 text-sm text-slate-500">Provider 与 MCP 只展示真实连接状态，密钥不进前端。</p>
        </header>
        <section className="v106-panel mb-4 p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">Provider</h2>
          {data.providers.status === "ok" && data.providers.data && data.providers.data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[680px] text-left text-xs">
                <thead>
                  <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                    <th className="pb-2 pr-3 font-medium">Provider</th>
                    <th className="pb-2 pr-3 font-medium">类型</th>
                    <th className="pb-2 pr-3 font-medium">验证</th>
                    <th className="pb-2 pr-3 font-medium">GEO 分</th>
                    <th className="pb-2 pr-3 font-medium">完成订单</th>
                    <th className="pb-2 font-medium">活跃</th>
                  </tr>
                </thead>
                <tbody>
                  {data.providers.data.map((provider) => (
                    <tr key={provider.id} className="border-b border-[color:var(--v106-border)] last:border-0">
                      <td className="py-2 pr-3 font-mono text-slate-700">{provider.entity_id}</td>
                      <td className="py-2 pr-3">{provider.provider_type}</td>
                      <td className="py-2 pr-3">{provider.verification_status}</td>
                      <td className="py-2 pr-3">{provider.geo_score}</td>
                      <td className="py-2 pr-3">{provider.completed_orders}</td>
                      <td className="py-2">{provider.is_active ? "是" : "否"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <SourceState
              record={data.providers}
              emptyTitle="尚无真实 Provider"
              emptyDescription="Provider 由真实 Entity 创建后才出现，不生成模拟候选。"
              errorTitle="Provider 接口不可用"
            />
          )}
        </section>
        <ToolPanel data={data.tools} />
      </div>
    );
  }

  function renderCapabilities() {
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">Agent 与能力资产</h1>
          <p className="mt-1 text-sm text-slate-500">Agent 注册表与能力目录，按真实接口读取。</p>
        </header>
        <AgentPanel data={data.agents} />
        <section className="v106-panel mt-4 p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">能力资产</h2>
          {data.capabilities.status === "ok" && data.capabilities.data && data.capabilities.data.length > 0 ? (
            <div className="grid grid-cols-1 gap-2 lg:grid-cols-2">
              {data.capabilities.data.map((capability) => (
                <div key={capability.capability_id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-slate-800">{capability.name}</span>
                    <span className={`rounded-md px-1.5 py-0.5 text-[11px] ${
                      capability.available
                        ? "bg-emerald-50 text-emerald-700"
                        : "bg-amber-50 text-amber-700"
                    }`}>
                      {capability.available ? "可用" : "未配置"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {capability.capability_type} · {capability.source_mode} · {capability.provider}
                  </p>
                  {capability.description && (
                    <p className="mt-1 text-xs leading-5 text-slate-600">{capability.description}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <SourceState
              record={data.capabilities}
              emptyTitle="尚无能力资产"
              emptyDescription="能力资产来自平台标准目录或域主创建，不生成模拟目录。"
              errorTitle="能力接口不可用"
            />
          )}
        </section>
      </div>
    );
  }

  function renderWorkflows() {
    const runs = data.runs.status === "ok" ? data.runs.data || [] : [];
    const grouped = runs.reduce<Record<string, number>>((acc, run) => {
      const key = run.tool_name || run.capability_type || "未知";
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">工作流</h1>
          <p className="mt-1 text-sm text-slate-500">Workflow 编辑器 API 尚未开放，当前只读真实运行记录。</p>
        </header>
        <div className="mb-4">
          <ModuleState
            variant="partial"
            title="Workflow 编辑器接口待接通"
            description="当前原型不创建或修改工作流，只展示已经发生的真实执行。"
            compact
          />
        </div>
        {Object.keys(grouped).length > 0 ? (
          <section className="v106-panel p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">按工具聚合</h2>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(grouped).map(([tool, count]) => (
                <div key={tool} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                  <div className="text-sm font-medium text-slate-800">{tool}</div>
                  <div className="mt-1 text-xs text-slate-500">{count} 次真实运行</div>
                </div>
              ))}
            </div>
          </section>
        ) : (
          <SourceState
            record={data.runs}
            emptyTitle="尚无工作流运行"
            emptyDescription="真实能力运行产生后，这里会出现聚合视图。"
            errorTitle="运行记录接口不可用"
          />
        )}
      </div>
    );
  }

  function renderReports() {
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">报告与结果</h1>
          <p className="mt-1 text-sm text-slate-500">诊断报告 API 尚未开放，先展示真实 World Snapshot。</p>
        </header>
        <div className="mb-4">
          <ModuleState
            variant="partial"
            title="诊断报告接口待接通"
            description="报告页面预留，等待真实报告生成协议接入。"
            compact
          />
        </div>
        <section className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">World Snapshot</h2>
          {data.snapshots.status === "ok" && data.snapshots.data && data.snapshots.data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-xs">
                <thead>
                  <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                    <th className="pb-2 pr-3 font-medium">World</th>
                    <th className="pb-2 pr-3 font-medium">版本</th>
                    <th className="pb-2 pr-3 font-medium">范围</th>
                    <th className="pb-2 font-medium">生成时间</th>
                  </tr>
                </thead>
                <tbody>
                  {data.snapshots.data.map((snapshot) => (
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
          ) : (
            <SourceState
              record={data.snapshots}
              emptyTitle="尚无 World Snapshot"
              emptyDescription="World State 生成后才会出现真实快照。"
              errorTitle="World Snapshot 接口不可用"
            />
          )}
        </section>
      </div>
    );
  }

  function renderIntelligence() {
    const snapshots = data.snapshots.status === "ok" ? data.snapshots.data || [] : [];
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">行业态势</h1>
          <p className="mt-1 text-sm text-slate-500">World Snapshot 与行业事件，来自真实 World State。</p>
        </header>
        <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatCard label="快照" value={String(snapshots.length)} icon={Globe} />
          <StatCard label="行业世界" value={String(new Set(snapshots.map((item) => item.world_code)).size)} icon={Globe} />
          <StatCard label="版本" value={String(new Set(snapshots.map((item) => item.world_version)).size)} icon={FileText} />
          <StatCard label="状态" value={data.snapshots.status === "ok" ? "已连接" : "受阻"} icon={Activity} />
        </div>
        <section className="v106-panel p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-800">World Snapshot</h2>
          {snapshots.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-xs">
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
          ) : (
            <SourceState
              record={data.snapshots}
              emptyTitle="尚无行业态势快照"
              emptyDescription="World State 生成后这里会展示真实行业快照。"
              errorTitle="行业态势接口不可用"
            />
          )}
        </section>
      </div>
    );
  }

  function renderSystem() {
    const configEntries = data.configs.status === "ok" ? Object.entries(data.configs.data || {}) : [];
    return (
      <div>
        <header className="mb-4">
          <h1 className="v106-page-title">系统与配置</h1>
          <p className="mt-1 text-sm text-slate-500">健康、数据表、配置目录与 Feature Flag。</p>
        </header>
        <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatCard label="后端状态" value={data.health.status === "ok" ? (data.health.data?.status || "ok") : "--"} icon={Activity} />
          <StatCard label="数据表总数" value={data.dbStats.status === "ok" ? String(data.dbStats.data?.total ?? 0) : "--"} icon={LayoutDashboard} />
          <StatCard label="配置分类" value={String(configEntries.length)} icon={Settings} />
          <StatCard label="Feature Flag" value={String(FEATURE_FLAGS.length)} icon={ShieldCheck} />
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <section className="v106-panel p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">配置目录</h2>
            {configEntries.length > 0 ? (
              <div className="space-y-3">
                {configEntries.map(([category, files]) => (
                  <div key={category} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                    <div className="text-xs font-semibold text-slate-700">{category}</div>
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {files.map((file) => (
                        <span key={file} className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">
                          {file.replace(".yaml", "")}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <SourceState
                record={data.configs}
                emptyTitle="尚无配置目录"
                emptyDescription="配置由仓库 config 目录真实读取。"
                errorTitle="配置接口不可用"
              />
            )}
          </section>
          <section className="v106-panel p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">Feature Flag 状态</h2>
            <div className="space-y-2">
              {FEATURE_FLAGS.map((flag) => (
                <div key={flag.id} className="flex items-center justify-between rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-2">
                  <span className="text-xs text-slate-700">{flag.label}</span>
                  <span className={`rounded-md px-1.5 py-0.5 text-[11px] ${
                    flag.status === "open"
                      ? "bg-emerald-50 text-emerald-700"
                      : flag.status === "reserved"
                        ? "bg-amber-50 text-amber-700"
                        : "bg-slate-100 text-slate-500"
                  }`}>
                    {flag.status}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    );
  }

  return (
    <AppShell
      surface="operations"
      featureFlags={["operations"]}
      userContext={{ label: "运营者", permissions: ["operations_read"] }}
      navRail={navRail}
      contextBar={contextBar}
      mobileNav={mobileNav}
      statusStrip={<StatusStrip items={statusItems} />}
      rightDrawer={
        <RealmDrawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title="平台运营后台"
          description="运营后台只读展示真实数据源、运行记录与配置目录。"
        >
          <div className="space-y-3">
            <p className="text-sm leading-6 text-slate-700">
              本原型不创建第二套运营数据模型；Provider、能力、运行和 World 快照均来自现有 API。
            </p>
            <p className="text-xs leading-5 text-slate-500">
              接口缺失时保留真实空状态或 partial 状态，不生成模拟业务数据。
            </p>
          </div>
        </RealmDrawer>
      }
    >
      <div className="mx-auto max-w-6xl">
        {notice && (
          <p className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            {notice}
          </p>
        )}
        {data.phase === "no-permission" && (
          <ModuleState
            variant="no-permission"
            title="需要登录运营后台"
            description="请先以平台运营账号登录。"
            actionLabel="去登录"
            onAction={() => {
              window.location.href = "/login?next=/operations";
            }}
          />
        )}
        {data.phase === "loading" && <ModuleState variant="loading" title="正在加载运营后台" />}
        {data.phase === "ready" && (
          <>
            {view === "overview" && renderOverview()}
            {view === "runtime" && renderRuntime()}
            {view === "connectors" && renderConnectors()}
            {view === "capabilities" && renderCapabilities()}
            {view === "workflows" && renderWorkflows()}
            {view === "reports" && renderReports()}
            {view === "intelligence" && renderIntelligence()}
            {view === "system" && renderSystem()}
          </>
        )}
      </div>
    </AppShell>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: LucideIcon;
}) {
  return (
    <div className="v106-panel p-4">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Icon className="h-4 w-4" aria-hidden="true" />
        {label}
      </div>
      <div className="mt-2 text-2xl font-bold text-slate-900">{value}</div>
    </div>
  );
}

function AgentPanel({ data }: { data: AsyncValue<import("@/lib/operations/types").AgentSummary[]> }) {
  return (
    <section className="v106-panel p-4">
      <h2 className="mb-3 text-sm font-semibold text-slate-800">Agent 注册表</h2>
      {data.status === "ok" && data.data && data.data.length > 0 ? (
        <div className="space-y-2">
          {data.data.map((agent) => (
            <div key={agent.name} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <div className="text-sm font-medium text-slate-800">{agent.name}</div>
              <p className="mt-1 text-xs leading-5 text-slate-500">{agent.description}</p>
            </div>
          ))}
        </div>
      ) : (
        <SourceState
          record={data}
          emptyTitle="尚无 Agent 注册"
          emptyDescription="Agent 注册表来自真实 Agent Registry。"
          errorTitle="Agent 接口不可用"
        />
      )}
    </section>
  );
}

function ToolPanel({ data }: { data: AsyncValue<import("@/lib/operations/types").McpToolSummary[]> }) {
  return (
    <section className="v106-panel p-4">
      <h2 className="mb-3 text-sm font-semibold text-slate-800">MCP 工具</h2>
      {data.status === "ok" && data.data && data.data.length > 0 ? (
        <div className="space-y-2">
          {data.data.map((tool) => (
            <div key={tool.name} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <div className="text-sm font-medium text-slate-800">{tool.name}</div>
              <p className="mt-1 text-xs leading-5 text-slate-500">{tool.description}</p>
              {tool.params.length > 0 && (
                <p className="mt-1 text-[11px] text-slate-400">参数：{tool.params.join("、")}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <SourceState
          record={data}
          emptyTitle="尚无 MCP 工具"
          emptyDescription="MCP 工具来自真实 MCP Server 注册表。"
          errorTitle="MCP 接口不可用"
        />
      )}
    </section>
  );
}
