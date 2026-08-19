"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { getToken } from "@/lib/authFetch";
import AppShell from "@/components/app-shell/AppShell";
import { buildMapView, buildViewModel, isRealmScopedDemand } from "@/lib/realm-owner/adapter";
import { MAP_NODE_DEFS, PRIMARY_NAV_DEFS } from "@/lib/realm-owner/config";
import {
  fetchConnectionCandidates,
  fetchCurrentUser,
  fetchDemandEvents,
  fetchEntityName,
  fetchRealmClaims,
  fetchRealmWorkspace,
  fetchWorldSnapshots,
  generateConnectionCandidates,
} from "@/lib/realm-owner/queries";
import {
  fetchGeoProjects,
  fetchIntakes,
  fetchIssues,
} from "@/lib/realm-owner/queries-v105";
import type {
  ConnectionCandidateItem,
  DemandEventItem,
  GeoProjectSummary,
  IntakeItem,
  IssueRecordItem,
  MapMode,
  RealmClaimItem,
  RealmOwnerHomeViewModel,
  RealmWorkspaceResponse,
  UserProfile,
  WorldStateSnapshotItem,
} from "@/lib/realm-owner/types";
import IntakeLaunchPanel from "./intake-launch-panel";
import IntakeAnalysisPanel from "./intake-analysis-panel";
import ExecutionPlanPanel from "./execution-plan-panel";
import IssueLibraryPanel from "./issue-library-panel";
import PrimarySidebar, { MobileRealmNav } from "./primary-sidebar";
import RealmContextHeader from "./realm-context-header";
import StartupTruthStrip from "./startup-truth-strip";
import StartupTaskRail from "./startup-task-rail";
import IndustryEvolutionCanvas from "./industry-evolution-canvas";
import ResourceConnectionPanel from "./resource-connection-panel";
import TrustedInformationFeed from "./trusted-information-feed";
import NextBestActionPanel from "./next-best-action-panel";
import TruthScopeLegend from "./truth-scope-legend";
import RealmAIAssistantDrawer from "./realm-ai-assistant-drawer";
import RealmDecisionApprovalDrawer, { type DecisionApprovalItem } from "./realm-decision-approval-drawer";
import RealInputDrawer from "./real-input-drawer";
import ResourceNeedFormDrawer from "./resource-need-form-drawer";
import PositionConfigDrawer from "./position-config-drawer";
import PublicIntakeTokenPanel from "./public-intake-token-panel";
import ModuleState from "./module-state";
import {
  LockedNavDrawer,
  MapConfigDrawer,
  NodeDetailDrawer,
  TaskDetailDrawer,
} from "./detail-drawers";

type DrawerName =
  | "realInput"
  | "task"
  | "node"
  | "position"
  | "resourceForm"
  | "assistant"
  | "decisions"
  | "mapConfig"
  | "locked"
  | null;

interface ModuleErrorMap {
  demand?: string;
  candidates?: string;
  snapshots?: string;
  claims?: string;
}

function errorMessage(err: unknown, fallback: string): string {
  const payload = err as { status?: number; message?: string };
  return payload.message || fallback;
}

function isForbidden(err: unknown): boolean {
  return (err as { status?: number }).status === 403;
}

export default function RealmOwnerShell({ realmId }: { realmId: string }) {
  const [phase, setPhase] = useState<"loading" | "ready" | "forbidden" | "error">("loading");
  const [phaseMessage, setPhaseMessage] = useState("");
  const [workspace, setWorkspace] = useState<RealmWorkspaceResponse | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [demandEvents, setDemandEvents] = useState<DemandEventItem[]>([]);
  const [candidates, setCandidates] = useState<ConnectionCandidateItem[]>([]);
  const [snapshots, setSnapshots] = useState<WorldStateSnapshotItem[]>([]);
  const [candidateNames, setCandidateNames] = useState<Record<string, string>>({});
  const [claims, setClaims] = useState<RealmClaimItem[]>([]);
  const [claimsError, setClaimsError] = useState<string | null>(null);
  const [mode, setMode] = useState<MapMode>("business_flow");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewModel, setViewModel] = useState<RealmOwnerHomeViewModel | null>(null);
  const [drawer, setDrawer] = useState<DrawerName>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [lockedLabel, setLockedLabel] = useState("");
  const [assistantPrefill, setAssistantPrefill] = useState("");
  const [generating, setGenerating] = useState(false);
  const [refreshingSnapshots, setRefreshingSnapshots] = useState(false);
  const [moduleErrors, setModuleErrors] = useState<ModuleErrorMap>({});
  const [intakes, setIntakes] = useState<IntakeItem[]>([]);
  const [issues, setIssues] = useState<IssueRecordItem[]>([]);
  const [projects, setProjects] = useState<GeoProjectSummary[]>([]);
  const [v105Error, setV105Error] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const token = getToken();
    if (!token) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }

    let cancelled = false;
    setPhase("loading");
    setPhaseMessage("");
    setWorkspace(null);
    setViewModel(null);
    setDemandEvents([]);
    setCandidates([]);
    setSnapshots([]);
    setCandidateNames({});
      setClaims([]);
      setClaimsError(null);
      setModuleErrors({});
      setIntakes([]);
      setIssues([]);
      setProjects([]);
      setV105Error(null);

    async function run() {
      const [userResult, workspaceResult] = await Promise.allSettled([
        fetchCurrentUser(),
        fetchRealmWorkspace(realmId),
      ]);
      if (cancelled) return;

      if (workspaceResult.status === "rejected") {
        const err = workspaceResult.reason;
        if (isForbidden(err)) {
          setPhase("forbidden");
        } else if ((err as { status?: number }).status === 401) {
          window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
        } else {
          setPhase("error");
          setPhaseMessage(errorMessage(err, "Realm 数据加载失败"));
        }
        return;
      }

        const ws = workspaceResult.value;
        const currentUser = userResult.status === "fulfilled" ? userResult.value : null;
        setWorkspace(ws);
        setUser(currentUser);

        const writeAllowed = Boolean(ws.access.controlled);
        const [intakeResult, issueResult, projectResult] = await Promise.allSettled([
          writeAllowed ? fetchIntakes(realmId) : Promise.resolve([]),
          writeAllowed ? fetchIssues(realmId) : Promise.resolve([]),
          writeAllowed ? fetchGeoProjects(realmId) : Promise.resolve([]),
        ]);
        if (cancelled) return;
        setIntakes(intakeResult.status === "fulfilled" ? intakeResult.value : []);
        setIssues(issueResult.status === "fulfilled" ? issueResult.value : []);
        setProjects(projectResult.status === "fulfilled" ? projectResult.value : []);
        if (
          intakeResult.status === "rejected" ||
          issueResult.status === "rejected" ||
          projectResult.status === "rejected"
        ) {
          setV105Error("V10.5 数据接口部分不可用，已保留真实空状态。");
        }

        const canReviewClaims = currentUser?.role === "admin" || currentUser?.role === "reviewer";
      const [demandResult, candidateResult, snapshotResult, claimResult] = await Promise.allSettled([
        fetchDemandEvents(),
        fetchConnectionCandidates(),
        fetchWorldSnapshots(),
        canReviewClaims ? fetchRealmClaims() : Promise.resolve([]),
      ]);
      if (cancelled) return;

      const demands = demandResult.status === "fulfilled" ? demandResult.value : [];
      const allCandidates = candidateResult.status === "fulfilled" ? candidateResult.value : [];
      const snapshotsData = snapshotResult.status === "fulfilled" ? snapshotResult.value : [];
      const claimsData = claimResult.status === "fulfilled" ? claimResult.value : [];

      const nextErrors: ModuleErrorMap = {};
      if (demandResult.status === "rejected") nextErrors.demand = errorMessage(demandResult.reason, "需求接口不可用");
      if (candidateResult.status === "rejected") nextErrors.candidates = errorMessage(candidateResult.reason, "候选接口不可用");
      if (snapshotResult.status === "rejected") nextErrors.snapshots = errorMessage(snapshotResult.reason, "World Snapshot 接口不可用");
      if (claimResult.status === "rejected") {
        if (!isForbidden(claimResult.reason)) nextErrors.claims = errorMessage(claimResult.reason, "审批接口不可用");
      }
      setModuleErrors(nextErrors);
      setClaims(claimsData);
      setClaimsError(
        claimResult.status === "rejected" && isForbidden(claimResult.reason)
          ? "无审批权限（仅保留只读入口）"
          : null,
      );

      const scopedDemands = demands.filter((event) => isRealmScopedDemand(event, realmId, currentUser?.id || null));
      const scopedIds = new Set(scopedDemands.map((event) => event.id));
      const scopedCandidates = allCandidates.filter(
        (candidate) => candidate.demand_event_id && scopedIds.has(candidate.demand_event_id),
      );
      const ids = Array.from(new Set(scopedCandidates.map((candidate) => candidate.target_node_id))).slice(0, 20);
      const names: Record<string, string> = {};
      const nameResults = await Promise.allSettled(ids.map((id) => fetchEntityName(id)));
      nameResults.forEach((result, index) => {
        if (result.status === "fulfilled" && result.value) names[ids[index]] = result.value;
      });
      if (cancelled) return;

      setDemandEvents(demands);
      setCandidates(allCandidates);
      setSnapshots(snapshotsData);
      setCandidateNames(names);
      setViewModel(
        buildViewModel({
          workspace: ws,
          user: currentUser,
          realmId,
          realmDemandEvents: demands,
          allCandidates,
          candidateNames: names,
          snapshots: snapshotsData,
          mode,
        }),
      );
      setPhase("ready");
    }

    run();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [realmId]);

  const canWrite = Boolean(workspace?.access.controlled);

  const decisionItems: DecisionApprovalItem[] = useMemo(
    () =>
      claims.map((claim) => ({
        id: claim.claim_id,
        title: `领域认领：${claim.entity_name}`,
        status: "pending" as const,
        detail: claim.reason || "等待审批",
      })),
    [claims],
  );

  function openDrawer(name: DrawerName) {
    setDrawer(name);
  }

  function openLockedNav(label: string) {
    setLockedLabel(label);
    setDrawer("locked");
  }

  function openTask(taskId: string) {
    setSelectedTaskId(taskId);
    setDrawer("task");
  }

  function openNode(nodeId: string) {
    setSelectedNodeId(nodeId);
    setDrawer("node");
  }

  function openAssistant(prefill = "") {
    setAssistantPrefill(prefill);
    setDrawer("assistant");
  }

  function handleModeChange(next: MapMode) {
    setMode(next);
    setViewModel((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        map: buildMapView({
          mode: next,
          snapshots,
          ownerPosition: prev.map.ownerPosition,
        }),
      };
    });
  }

  async function refreshWorkspace() {
    try {
      const ws = await fetchRealmWorkspace(realmId);
      setWorkspace(ws);
      if (viewModel) {
        setViewModel(
          buildViewModel({
            workspace: ws,
            user,
            realmId,
            realmDemandEvents: demandEvents,
            allCandidates: candidates,
            candidateNames,
            snapshots,
            mode,
          }),
        );
      }
    } catch (err) {
      setPhaseMessage(errorMessage(err, "刷新 Realm 数据失败"));
    }
  }

    async function refreshIntakes() {
      try {
        setIntakes(await fetchIntakes(realmId));
      } catch (err) {
          setV105Error(errorMessage(err, '客户资料接口不可用'));
      }
    }

    async function refreshIssues() {
      try {
        setIssues(await fetchIssues(realmId));
      } catch (err) {
          setV105Error(errorMessage(err, '问题库接口不可用'));
      }
    }

    async function refreshProjects() {
      try {
        setProjects(await fetchGeoProjects(realmId));
      } catch (err) {
          setV105Error(errorMessage(err, '项目接口不可用'));
      }
    }

    async function refreshDemandData() {
    try {
      const [demandResult, candidateResult] = await Promise.allSettled([
        fetchDemandEvents(),
        fetchConnectionCandidates(),
      ]);
      const demands = demandResult.status === "fulfilled" ? demandResult.value : demandEvents;
      const allCandidates = candidateResult.status === "fulfilled" ? candidateResult.value : candidates;
      const scopedDemands = demands.filter((event) => isRealmScopedDemand(event, realmId, user?.id || null));
      const scopedIds = new Set(scopedDemands.map((event) => event.id));
      const scopedCandidates = allCandidates.filter(
        (candidate) => candidate.demand_event_id && scopedIds.has(candidate.demand_event_id),
      );
      const ids = Array.from(new Set(scopedCandidates.map((candidate) => candidate.target_node_id))).slice(0, 20);
      const names: Record<string, string> = { ...candidateNames };
      const nameResults = await Promise.allSettled(ids.map((id) => fetchEntityName(id)));
      nameResults.forEach((result, index) => {
        if (result.status === "fulfilled" && result.value) names[ids[index]] = result.value;
      });
      setDemandEvents(demands);
      setCandidates(allCandidates);
      setCandidateNames(names);
      if (workspace) {
        setViewModel(
          buildViewModel({
            workspace,
            user,
            realmId,
            realmDemandEvents: demands,
            allCandidates,
            candidateNames: names,
            snapshots,
            mode,
          }),
        );
      }
    } catch (err) {
      setModuleErrors((prev) => ({ ...prev, candidates: errorMessage(err, "刷新资源数据失败") }));
    }
  }

  async function refreshSnapshots() {
    setRefreshingSnapshots(true);
    try {
      const data = await fetchWorldSnapshots();
      setSnapshots(data);
      setModuleErrors((prev) => ({ ...prev, snapshots: undefined }));
      if (viewModel) {
        setViewModel((prev) =>
          prev
            ? {
                ...prev,
                map: buildMapView({
                  mode,
                  snapshots: data,
                  ownerPosition: prev.map.ownerPosition,
                }),
              }
            : prev,
        );
      }
    } catch (err) {
      setModuleErrors((prev) => ({ ...prev, snapshots: errorMessage(err, "World Snapshot 接口不可用") }));
    } finally {
      setRefreshingSnapshots(false);
    }
  }

  async function generateCandidates() {
    const scopedDemands = demandEvents.filter((event) =>
      isRealmScopedDemand(event, realmId, user?.id || null),
    );
    const realDemand = scopedDemands.find(
      (event) => !event.is_synthetic && event.truth_status !== "synthetic",
    );
    if (!realDemand) return;
    setGenerating(true);
    try {
      await generateConnectionCandidates(realDemand.id);
      await refreshDemandData();
    } catch (err) {
      setModuleErrors((prev) => ({ ...prev, candidates: errorMessage(err, "候选生成失败") }));
    } finally {
      setGenerating(false);
    }
  }

  function draftContact(candidateId: string) {
    const candidate = candidates.find((item) => item.id === candidateId);
    const name = candidate ? candidateNames[candidate.target_node_id] : "该主体";
    openAssistant(
      `请为候选“${name || "该主体"}”起草第一条真实连接联系内容；先核验证据、风险与未知项，不做出任何承诺。`,
    );
  }

  function openTarget(targetHref: string | null) {
    if (targetHref === "real-input") {
      if (!canWrite) {
        setLockedLabel("写操作");
        setDrawer("locked");
        return;
      }
      setDrawer("realInput");
    } else if (targetHref === "resource-demand") {
      if (!canWrite) {
        setLockedLabel("写操作");
        setDrawer("locked");
        return;
      }
      setDrawer("resourceForm");
    }
  }

  function savePositionDraft(nodeId: string) {
    setViewModel((prev) =>
      prev
        ? {
            ...prev,
            map: {
              ...prev.map,
              ownerPosition: { status: "draft", nodeIds: [nodeId] },
            },
          }
        : prev,
    );
  }

  const fallbackRealm: RealmOwnerHomeViewModel["realm"] = {
    id: realmId,
    displayName: "Realm",
    worldName: null,
    trackName: "90天待解锁",
    businessStage: null,
    operatingCycleLabel: "90天待解锁",
    permissions: [],
  };
  const enabledFeatureFlags = PRIMARY_NAV_DEFS.filter((item) => item.enabled).map((item) => item.id);
  const shellRealmContext = {
    id: realmId,
    name: viewModel?.realm.displayName || fallbackRealm.displayName,
    realmType: workspace?.realm?.realm_type || undefined,
  };
  const shellUserContext = {
    id: user?.id || undefined,
    label: user?.name || "未登录",
    permissions: canWrite ? ["realm_write"] : ["realm_read"],
  };

  if (phase === "forbidden") {
    return (
      <AppShell
        surface="owner"
        featureFlags={enabledFeatureFlags}
        realmContext={shellRealmContext}
        userContext={shellUserContext}
        navRail={<PrimarySidebar realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
      >
        <ModuleState variant="no-permission" title="权限不足" description="无法确认当前用户对该 Realm 的访问权限，不展示资源详情。" />
      </AppShell>
    );
  }

  if (phase === "error") {
    return (
      <AppShell
        surface="owner"
        featureFlags={enabledFeatureFlags}
        realmContext={shellRealmContext}
        userContext={shellUserContext}
        navRail={<PrimarySidebar realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
      >
        <ModuleState
          variant="error"
          title="Realm 数据加载失败"
          description={phaseMessage}
          actionLabel="重试"
          onAction={() => window.location.reload()}
        />
      </AppShell>
    );
  }

  if (phase === "loading" || !workspace || !viewModel) {
    return (
      <AppShell
        surface="owner"
        featureFlags={enabledFeatureFlags}
        realmContext={shellRealmContext}
        userContext={shellUserContext}
        navRail={<PrimarySidebar realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
        contextBar={
          <RealmContextHeader realm={fallbackRealm} onSearch={setSearchQuery} onOpenAssistant={() => openAssistant()} onOpenDecisions={() => openDrawer("decisions")} />
        }
        mobileNav={<MobileRealmNav realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
      >
        <ModuleState variant="loading" title="正在加载域主工作台" />
      </AppShell>
    );
  }

  const selectedTask = viewModel.startupTasks.find((task) => task.id === selectedTaskId) || null;
  const selectedNodeDefinition = MAP_NODE_DEFS[mode].find((node) => node.id === selectedNodeId) || null;
  const selectedNodeTruth = viewModel.map.nodes.find((node) => node.id === selectedNodeId)?.truthScope || "simulation";

  return (
    <AppShell
      surface="owner"
      featureFlags={enabledFeatureFlags}
      realmContext={shellRealmContext}
      userContext={shellUserContext}
      navRail={<PrimarySidebar realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
      contextBar={
        <RealmContextHeader
          realm={viewModel.realm}
          onSearch={setSearchQuery}
          onOpenAssistant={() => openAssistant()}
          onOpenDecisions={() => openDrawer("decisions")}
        />
      }
      mobileNav={<MobileRealmNav realmId={realmId} activeId="today" onOpenLocked={openLockedNav} />}
      statusStrip={<StartupTruthStrip readiness={viewModel.readiness} />}
    >
          {!canWrite && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
              <AlertTriangle className="h-4 w-4 shrink-0" aria-hidden="true" />
              当前为成员只读视图：可查看公开/授权数据，写操作需要域主或编辑权限。
            </div>
          )}

          <header className="mb-3">
            <h1 className="text-[28px] font-bold leading-tight text-slate-900">域主工作台</h1>
            <p className="mt-1 text-sm text-slate-500">今日工作视图：待办、提醒、AI建议、阻塞和风险，全部来自真实经营数据</p>
          </header>

          <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">客户资料</div>
              <div className="mt-1 text-2xl font-bold text-slate-900">{intakes.length}</div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">项目</div>
              <div className="mt-1 text-2xl font-bold text-slate-900">{projects.length}</div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">问题</div>
              <div className="mt-1 text-2xl font-bold text-slate-900">{issues.length}</div>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">可信事实</div>
              <div className="mt-1 text-2xl font-bold text-slate-900">
                {workspace?.position?.trust?.verified_evidence || 0} / {workspace?.position?.trust?.observed_evidence || 0}
              </div>
            </div>
          </div>

            {v105Error && (
              <div className='mb-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800'>
                <AlertTriangle className='mt-0.5 h-4 w-4 shrink-0' aria-hidden='true' />
                {v105Error}
              </div>
            )}

            <div className='mt-3'>
              <PublicIntakeTokenPanel
                realmId={realmId}
                authorizations={workspace.authorizations}
                canWrite={canWrite}
                onChanged={refreshWorkspace}
              />
            </div>

            <div className='mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2'>
              <IntakeLaunchPanel
                realmId={realmId}
                canWrite={canWrite}
                onCreated={() => void refreshIntakes()}
              />
              <IntakeAnalysisPanel
                realmId={realmId}
                intake={intakes[0] || null}
                canWrite={canWrite}
                onChanged={() => void refreshIntakes()}
                onOpenManualForm={() => openTarget('real-input')}
              />
            </div>

            <div className='mt-3'>
              <ExecutionPlanPanel
                realmId={realmId}
                canWrite={canWrite}
                projects={projects}
                intake={intakes[0] || null}
                onRefreshProjects={() => void refreshProjects()}
              />
            </div>

            <div className='mt-3'>
              <IssueLibraryPanel
                realmId={realmId}
                canWrite={canWrite}
                issues={issues}
                projects={projects}
                onRefreshIssues={() => void refreshIssues()}
              />
            </div>

            <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[220px_minmax(0,1fr)_280px]">
            <StartupTaskRail
              tasks={viewModel.startupTasks}
              onOpenTask={openTask}
              onStartRealInput={() => openTarget("real-input")}
              canWrite={canWrite}
            />
            <IndustryEvolutionCanvas
              map={viewModel.map}
              mode={mode}
              onModeChange={handleModeChange}
              onOpenNode={openNode}
              onOpenPositionConfig={() => openDrawer("position")}
              onOpenMapConfig={() => openDrawer("mapConfig")}
              state={moduleErrors.snapshots ? "partial" : "ready"}
              stateTitle={moduleErrors.snapshots ? "World Snapshot 接口不可用" : undefined}
              stateDescription={moduleErrors.snapshots ? "地图继续显示预演模板，不影响其他模块。" : undefined}
              onRetry={refreshSnapshots}
            />
            <ResourceConnectionPanel
              resources={viewModel.resources}
              onOpenDemandForm={() => openTarget("resource-demand")}
              onGenerateCandidates={generateCandidates}
              generating={generating}
              onDraftContact={draftContact}
              canWrite={canWrite}
              state={moduleErrors.demand || moduleErrors.candidates ? "partial" : "ready"}
              stateTitle="资源数据部分不可用"
              stateDescription="已保留已有真实数据，缺失接口单独标记。"
              onRetry={refreshDemandData}
            />
          </div>

          <div className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
            <TrustedInformationFeed information={viewModel.information} searchQuery={searchQuery} />
            <NextBestActionPanel nextAction={viewModel.nextAction} onOpenTarget={openTarget} />
          </div>

          <div className="mt-3">
            <TruthScopeLegend />
          </div>

      <RealInputDrawer
        open={drawer === "realInput"}
        onClose={() => setDrawer(null)}
        realmId={realmId}
        onSaved={refreshWorkspace}
      />

      <TaskDetailDrawer
        open={drawer === "task"}
        onClose={() => setDrawer(null)}
        task={selectedTask}
        onStartRealInput={() => openTarget("real-input")}
      />

      <NodeDetailDrawer
        open={drawer === "node"}
        onClose={() => setDrawer(null)}
        definition={selectedNodeDefinition}
        truthScope={selectedNodeTruth}
        onDraftPosition={savePositionDraft}
      />

      <PositionConfigDrawer
        open={drawer === "position"}
        onClose={() => setDrawer(null)}
        realmName={viewModel.realm.displayName}
        nodes={MAP_NODE_DEFS[mode]}
        current={viewModel.map.ownerPosition}
        onSaveDraft={savePositionDraft}
      />

      <ResourceNeedFormDrawer
        open={drawer === "resourceForm"}
        onClose={() => setDrawer(null)}
        realmId={realmId}
        onCreated={refreshDemandData}
      />

      <RealmAIAssistantDrawer
        open={drawer === "assistant"}
        onClose={() => setDrawer(null)}
        realmId={realmId}
        prefilledQuery={assistantPrefill}
      />

      <RealmDecisionApprovalDrawer
        open={drawer === "decisions"}
        onClose={() => setDrawer(null)}
        items={decisionItems}
        loading={false}
        error={claimsError}
      />

      <MapConfigDrawer
        open={drawer === "mapConfig"}
        onClose={() => setDrawer(null)}
        dataSourceLabel={viewModel.map.dataSourceLabel}
        snapshotId={viewModel.map.snapshotId}
        onRefresh={refreshSnapshots}
        refreshing={refreshingSnapshots}
      />

      <LockedNavDrawer
        open={drawer === "locked"}
        onClose={() => setDrawer(null)}
        label={lockedLabel}
      />
    </AppShell>
  );
}
