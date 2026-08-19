"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Bot, CircleDot, Database, FileText, GitBranch, Link2, Play, ShieldCheck, Sparkles, Users, Wrench, type LucideIcon } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import PrimarySidebar, { MobileRealmNav } from "@/components/realm-owner/primary-sidebar";
import RealmContextHeader from "@/components/realm-owner/realm-context-header";
import IssueClosedLoopWorkbench from "@/components/realm-owner/issue-closed-loop-workbench";
import SimulationLoopPanel from "@/components/realm-owner/simulation-loop-panel";
import ClientPositioningWorkbench from "@/components/realm-owner/client-positioning-workbench";
import ProjectPlanWorkbench from "@/components/realm-owner/project-plan-workbench";
import TruthBadge from "@/components/realm-owner/truth-badge";
import { getToken } from "@/lib/authFetch";
import { fetchCurrentUser, fetchRealmWorkspace } from "@/lib/realm-owner/queries";
import { fetchGeoProjects, fetchIntakes, fetchIssues } from "@/lib/realm-owner/queries-v105";
import type { GeoProjectSummary, IntakeItem, IssueRecordItem, TruthScope } from "@/lib/realm-owner/types";
import type { RealmWorkspaceResponse, UserProfile } from "@/lib/realm-owner/types";
import { EMPTY_TOOL_CONFIG, type ToolConfigDraft } from "@/lib/realm-owner/tool-config";
import { fetchToolConfigs, saveToolConfig } from "@/lib/realm-owner/tool-config-api";

export type RealmOwnerSection = "customers" | "projects" | "execution" | "results" | "tools";

const SECTION_META: Record<
  RealmOwnerSection,
  { title: string; subtitle: string; icon: typeof Users }
> = {
  customers: { title: "客户与定位", subtitle: "资料上传、AI分析、域主确认", icon: Users },
  projects: { title: "项目与计划", subtitle: "项目、阶段、步骤、任务、进度", icon: Database },
  execution: { title: "执行与问题", subtitle: "单步骤执行、问题库、尝试和纠偏", icon: Play },
  results: { title: "结果与资产", subtitle: "Evidence、Outcome、复盘、Skill候选", icon: FileText },
  tools: { title: "工具与连接", subtitle: "MCP、Codex、OpenClaw、本地工具和外部服务", icon: Link2 },
};

export default function RealmOwnerSectionPage({
  realmId,
  section,
}: {
  realmId: string;
  section: RealmOwnerSection;
}) {
  const meta = SECTION_META[section];
  const [phase, setPhase] = useState<"loading" | "ready" | "error" | "no-permission">("loading");
  const [phaseMessage, setPhaseMessage] = useState("");
  const [workspace, setWorkspace] = useState<RealmWorkspaceResponse | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [intakes, setIntakes] = useState<IntakeItem[]>([]);
  const [projects, setProjects] = useState<GeoProjectSummary[]>([]);
  const [issues, setIssues] = useState<IssueRecordItem[]>([]);
  const [toolDraft, setToolDraft] = useState<ToolConfigDraft>(EMPTY_TOOL_CONFIG);
  const [toolDraftLoaded, setToolDraftLoaded] = useState(false);
  const [v105Error, setV105Error] = useState("");

  useEffect(() => {
    if (section === "tools" && !toolDraftLoaded) {
      fetchToolConfigs(realmId)
        .then(setToolDraft)
        .catch(() => setV105Error("四原语配置读取失败，保留本地默认草稿。"))
        .finally(() => setToolDraftLoaded(true));
    }
  }, [realmId, section, toolDraftLoaded]);

  useEffect(() => {
    if (!getToken()) {
      window.location.assign("/login?next=" + encodeURIComponent(`/realm/${realmId}/${section}`));
      return;
    }
    let cancelled = false;
    async function run() {
      try {
        const [userResult, workspaceResult, intakeResult, projectResult, issueResult] =
          await Promise.allSettled([
            fetchCurrentUser(),
            fetchRealmWorkspace(realmId),
            fetchIntakes(realmId),
            fetchGeoProjects(realmId),
            fetchIssues(realmId),
          ]);
        if (cancelled) return;
        if (userResult.status === "fulfilled") setUser(userResult.value);
        if (userResult.status === "rejected" || workspaceResult.status === "rejected") {
          setPhase("no-permission");
          return;
        }
        setWorkspace(workspaceResult.value);
        setIntakes(intakeResult.status === "fulfilled" ? intakeResult.value : []);
        setProjects(projectResult.status === "fulfilled" ? projectResult.value : []);
        setIssues(issueResult.status === "fulfilled" ? issueResult.value : []);
        if (
          intakeResult.status === "rejected" ||
          projectResult.status === "rejected" ||
          issueResult.status === "rejected"
        ) {
          setV105Error("部分数据接口不可用，已保留真实空状态。");
        }
        setPhase("ready");
      } catch (err) {
        if (cancelled) return;
        setPhase("error");
        setPhaseMessage(err instanceof Error ? err.message : "加载失败");
      }
    }
    void run();
    return () => {
      cancelled = true;
    };
  }, [realmId, section]);

  const canWrite = Boolean(workspace?.access.controlled);
  const statusItems = useMemo(
    () => [
      { label: "数据连接", value: workspace ? "已连接" : "未连接", tone: workspace ? ("success" as const) : ("warning" as const) },
      { label: "权限", value: canWrite ? "域主可写" : "成员只读" },
      { label: "truth scope", value: "observed / inferred / unknown" },
      { label: "版本", value: "V10.6 域主工作台" },
    ],
    [canWrite, workspace],
  );

  const realmName = workspace?.realm?.realm_code || "Realm";
  const fallbackRealm = {
    id: realmId,
    displayName: realmName,
    worldName: null,
    trackName: "90天待解锁",
    businessStage: null,
    operatingCycleLabel: "90天待解锁",
    permissions: canWrite ? ["realm_write"] : ["realm_read"],
  };
  const shellUser = {
    id: user?.id || undefined,
    label: user?.name || "未登录",
    permissions: canWrite ? ["realm_write"] : ["realm_read"],
  };

  function refreshProjects() {
    void fetchGeoProjects(realmId)
      .then(setProjects)
      .catch(() => setV105Error("项目接口不可用"));
  }
  function refreshIssues() {
    void fetchIssues(realmId)
      .then(setIssues)
      .catch(() => setV105Error("问题库接口不可用"));
  }

  function updateToolDraft(part: keyof ToolConfigDraft, key: string, value: string) {
    setToolDraft((prev) => ({
      ...prev,
      [part]: { ...prev[part], [key]: value },
    }));
  }

  function renderContent() {
    if (section === "customers") {
      return (
        <>
          <div className="mb-3">
            <SimulationLoopPanel realmId={realmId} canWrite={canWrite} />
          </div>
          <ClientPositioningWorkbench realmId={realmId} canWrite={canWrite} />
        </>
      );
    }
    if (section === "projects") {
      return (
        <ProjectPlanWorkbench
          realmId={realmId}
          projects={projects}
        />
      );
    }
    if (section === "execution") {
      const timeline = workspace?.timeline || [];
      const current = timeline[0] || null;
      return (
        <>
          <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-3">
            <MiniStat label="当前步骤" value={current ? "进行中" : "待启动"} icon={Play} />
            <MiniStat label="执行记录" value={String(timeline.length)} icon={CircleDot} />
            <MiniStat label="问题库" value={String(issues.length)} icon={Wrench} />
          </div>
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <section className="v106-panel p-4">
              <h2 className="mb-3 text-sm font-semibold text-slate-800">当前步骤</h2>
              {current ? (
                <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-slate-800">{current.label}</span>
                    <TruthBadge scope={current.truth_status as TruthScope} />
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{current.type} · {current.at}</p>
                </div>
              ) : (
                <ModuleState variant="empty" title="尚无当前步骤" description="项目计划生成后开始执行。" compact />
              )}
            </section>
            <section className="v106-panel p-4">
              <h2 className="mb-3 text-sm font-semibold text-slate-800">执行记录</h2>
              {timeline.length > 0 ? (
                <div className="space-y-2">
                  {timeline.map((item, index) => (
                    <div key={`${item.type}-${index}`} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-medium text-slate-700">{item.label}</span>
                        <span className="text-[11px] text-slate-400">{item.at}</span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-500">{item.type} · {item.truth_status}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <ModuleState variant="empty" title="尚无执行记录" description="Agent 和工具运行后自动记录。" compact />
              )}
            </section>
          </div>
          <section className="v106-panel mt-3 p-4">
            <div className="mb-3 flex items-center justify-between gap-2">
              <h2 className="text-sm font-semibold text-slate-800">执行时间轴</h2>
              <span className="text-xs text-slate-500">{timeline.length} 条真实记录</span>
            </div>
            {timeline.length > 0 ? (
              <div className="space-y-2">
                {timeline.map((item, index) => (
                  <div key={`${item.type}-${index}`} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-slate-800">{item.label}</span>
                      <span className="text-[11px] text-slate-400">{item.at}</span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-[color:var(--v106-primary)]"
                        style={{ width: `${timeline.length === 1 ? 100 : Math.round(((index + 1) / timeline.length) * 100)}%` }}
                      />
                    </div>
                    <p className="mt-1 text-[11px] text-slate-500">{item.type} · {item.truth_status}</p>
                  </div>
                ))}
              </div>
            ) : (
              <ModuleState variant="empty" title="尚无执行时间轴" description="真实执行后自动生成。" compact />
            )}
          </section>
          <div className="mt-3">
            <IssueClosedLoopWorkbench realmId={realmId} canWrite={canWrite} projects={projects} />
          </div>
        </>
      );
    }
    if (section === "results") {
      const evidence = workspace?.evidence || [];
      const assets = workspace?.assets || [];
      const timeline = workspace?.timeline || [];
      const skillCandidates = issues.filter((item) => item.is_template_candidate);
      return (
        <>
          <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
            <MiniStat label="Evidence" value={String(evidence.length)} icon={ShieldCheck} />
            <MiniStat label="资产" value={String(assets.length)} icon={Database} />
            <MiniStat label="Skill 候选" value={String(skillCandidates.length)} icon={Sparkles} />
            <MiniStat label="复盘" value={String(timeline.length)} icon={GitBranch} />
          </div>
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <section className="v106-panel p-4">
              <h2 className="mb-3 text-sm font-semibold text-slate-800">Evidence</h2>
              {evidence.length > 0 ? (
                <div className="space-y-2">
                  {evidence.map((item) => (
                    <div key={item.id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <div className="text-sm font-medium text-slate-800">{item.claim}</div>
                          <div className="mt-1 text-xs text-slate-500">{item.source_name || item.source_url || "无来源"}</div>
                        </div>
                        <TruthBadge scope={item.truth_status as TruthScope} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <ModuleState variant="empty" title="尚无真实证据" description="observed 不得显示为 verified。" compact />
              )}
            </section>
            <div className="space-y-3">
              <section className="v106-panel p-4">
                <h2 className="mb-3 text-sm font-semibold text-slate-800">资产</h2>
                {assets.length > 0 ? (
                  <div className="space-y-2">
                    {assets.map((item) => (
                      <div key={item.id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-sm font-medium text-slate-800">{item.title}</span>
                          <TruthBadge scope={item.truth_status as TruthScope} />
                        </div>
                        <p className="mt-1 text-xs text-slate-500">{item.asset_type || "document"}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ModuleState variant="empty" title="尚无资产" description="复盘和 Skill 候选由域主确认后进入资产。" compact />
                )}
              </section>
              <section className="v106-panel p-4">
                <h2 className="mb-3 text-sm font-semibold text-slate-800">Skill 候选</h2>
                {skillCandidates.length > 0 ? (
                  <div className="space-y-2">
                    {skillCandidates.map((item) => (
                      <div key={item.id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                        <div className="text-sm font-medium text-slate-800">{item.title || item.original_text}</div>
                        <p className="mt-1 text-xs text-slate-500">{item.template_status} · {item.ai_classification?.category || "未分类"}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <ModuleState variant="empty" title="尚无 Skill 候选" description="真实复盘后生成，域主确认后才成为资产。" compact />
                )}
              </section>
            </div>
          </div>
        </>
      );
    }
    const authorizations = workspace?.authorizations || [];
    return (
      <>
        <section className="v106-panel mb-4 p-4">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold text-slate-800">四原语配置草稿</h2>
            <span className="text-xs text-slate-500">本地草稿，后续接入后端配置 API</span>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">Agent</b>
              <ConfigField label="名称" value={toolDraft.agent.name} onChange={(value) => updateToolDraft("agent", "name", value)} />
              <ConfigField label="工具" value={toolDraft.agent.tools} onChange={(value) => updateToolDraft("agent", "tools", value)} />
              <ConfigField label="预算" value={toolDraft.agent.budget} onChange={(value) => updateToolDraft("agent", "budget", value)} />
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">Skills</b>
              <ConfigField label="技能包" value={toolDraft.skill.name} onChange={(value) => updateToolDraft("skill", "name", value)} />
              <ConfigField label="版本" value={toolDraft.skill.version} onChange={(value) => updateToolDraft("skill", "version", value)} />
              <ConfigField label="来源" value={toolDraft.skill.source} onChange={(value) => updateToolDraft("skill", "source", value)} />
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">Workflows</b>
              <ConfigField label="工作流" value={toolDraft.workflow.name} onChange={(value) => updateToolDraft("workflow", "name", value)} />
              <ConfigField label="步骤" value={toolDraft.workflow.steps} onChange={(value) => updateToolDraft("workflow", "steps", value)} />
              <ConfigField label="人工确认点" value={toolDraft.workflow.approvalPoint} onChange={(value) => updateToolDraft("workflow", "approvalPoint", value)} />
            </div>
            <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <b className="text-sm font-medium text-slate-800">MCP</b>
              <ConfigField label="连接" value={toolDraft.mcp.name} onChange={(value) => updateToolDraft("mcp", "name", value)} />
              <ConfigField label="工具" value={toolDraft.mcp.tools} onChange={(value) => updateToolDraft("mcp", "tools", value)} />
              <ConfigField label="密钥策略" value={toolDraft.mcp.secretPolicy} onChange={(value) => updateToolDraft("mcp", "secretPolicy", value)} />
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              void Promise.all([
                saveToolConfig(realmId, "agent", toolDraft.agent),
                saveToolConfig(realmId, "skill", toolDraft.skill),
                saveToolConfig(realmId, "workflow", toolDraft.workflow),
                saveToolConfig(realmId, "mcp", toolDraft.mcp),
              ])
                .then(() => setV105Error("四原语配置已保存到 Realm。"))
                .catch(() => setV105Error("四原语配置保存失败，请稍后重试。"));
            }}
            className="mt-3 rounded-md bg-[color:var(--v106-primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[color:var(--v106-primary-strong)]"
          >
            保存草稿
          </button>
        </section>
        <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
          <MiniStat label="数据授权" value={String(authorizations.length)} icon={Link2} />
          <MiniStat label="MCP" value="待接通" icon={Wrench} />
          <MiniStat label="Agent" value="可配置" icon={Bot} />
          <MiniStat label="Skills / Workflows" value="可配置" icon={GitBranch} />
        </div>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          <section className="v106-panel p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">数据授权</h2>
            {authorizations.length > 0 ? (
              <div className="space-y-2">
                {authorizations.map((item) => (
                  <div key={item.id} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-slate-800">{item.source_name || item.authorization_code_masked || "授权"}</span>
                      <TruthBadge scope={item.truth_status as TruthScope} />
                    </div>
                    <p className="mt-1 text-xs text-slate-500">{item.use_scope} · {item.status}</p>
                  </div>
                ))}
              </div>
            ) : (
              <ModuleState variant="empty" title="尚无数据授权" description="连接外部工具前需要域主创建授权。" compact />
            )}
          </section>
          <section className="v106-panel p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-800">四原语连接</h2>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
              {[
                ["MCP", "工具与资源连接", "待接通"],
                ["Agent", "角色、工具、预算、权限", "可配置"],
                ["Skills", "技能包、版本、来源、授权", "可配置"],
                ["Workflows", "步骤、条件、人工确认点", "可配置"],
              ].map(([title, desc, state]) => (
                <div key={title} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                  <div className="flex items-center justify-between gap-2">
                    <b className="text-sm font-medium text-slate-800">{title}</b>
                    <span className={`rounded-md px-1.5 py-0.5 text-[11px] ${state === "待接通" ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>{state}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{desc}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </>
    );
  }

  const Icon = meta.icon;
  return (
    <AppShell
      surface="owner"
      featureFlags={["today", "customers", "projects", "execution", "results", "tools"]}
      realmContext={{ id: realmId, name: realmName, realmType: workspace?.realm?.realm_type || undefined }}
      userContext={shellUser}
      navRail={<PrimarySidebar realmId={realmId} activeId={section} onOpenLocked={() => undefined} />}
      contextBar={
        <RealmContextHeader
          realm={fallbackRealm}
          onSearch={() => undefined}
          onOpenAssistant={() => undefined}
          onOpenDecisions={() => undefined}
        />
      }
      mobileNav={<MobileRealmNav realmId={realmId} activeId={section} onOpenLocked={() => undefined} />}
      statusStrip={<StatusStrip items={statusItems} />}
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">{meta.title}</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">{meta.subtitle}</p>
        </header>
        {v105Error && (
          <div className="mb-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            {v105Error}
          </div>
        )}
        {phase === "loading" && <ModuleState variant="loading" title={`正在加载${meta.title}`} />}
        {phase === "error" && (
          <ModuleState variant="error" title="加载失败" description={phaseMessage} actionLabel="重试" onAction={() => window.location.reload()} />
        )}
        {phase === "no-permission" && (
          <ModuleState
            variant="no-permission"
            title={user ? "无权限访问该 Realm" : "需要登录"}
            description={user ? "当前账号不是该 Realm 成员，不展示客户内容。" : "请先登录域主账号。"}
            actionLabel={user ? undefined : "去登录"}
            onAction={user ? undefined : () => window.location.assign("/login?next=" + encodeURIComponent(`/realm/${realmId}/${section}`))}
          />
        )}
        {phase === "ready" && (
          <>
            {!canWrite && (
              <div className="mb-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                当前为成员只读视图；写操作需要域主或编辑权限。
              </div>
            )}
            {renderContent()}
          </>
        )}
      </div>
    </AppShell>
  );
}

function MiniStat({
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

function ConfigField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="mt-2">
      <label className="block text-[11px] font-medium text-slate-500">{label}</label>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="v106-control mt-1 w-full px-2.5 py-1.5 text-sm"
      />
    </div>
  );
}
