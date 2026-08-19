"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Building2, Landmark, Shield, Database, FolderKanban, FileText,
  Bot, GitBranch, Plus, Loader2, RefreshCw, AlertCircle,
  ArrowRight, Boxes, KeyRound, CircleDot, Sparkles,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

function authHeaders(token: string) {
  return { "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

function parseList(value: string): string[] {
  return value.split(/[,，\n]/).map((s) => s.trim()).filter(Boolean);
}

export default function RealmWorkbench() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [realms, setRealms] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [workspace, setWorkspace] = useState<any>(null);
  const [project, setProject] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [projectAssets, setProjectAssets] = useState<any>({ artifacts: [], realm_data_assets: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Realm creation/claim
  const [entName, setEntName] = useState("");
  const [entWebsite, setEntWebsite] = useState("");
  const [brandName, setBrandName] = useState("");
  const [claimId, setClaimId] = useState("");

  // Data import
  const [authSource, setAuthSource] = useState("");
  const [authUrl, setAuthUrl] = useState("");
  const [authScope, setAuthScope] = useState("project_evidence");
  const [assetKey, setAssetKey] = useState("");
  const [assetTitle, setAssetTitle] = useState("");
  const [evClaim, setEvClaim] = useState("");
  const [evUrl, setEvUrl] = useState("");
  const [relationTarget, setRelationTarget] = useState("");
  const [relationType, setRelationType] = useState("partner");

  // Project
  const [projectName, setProjectName] = useState("");
  const [projectObjective, setProjectObjective] = useState("");
  const [projectAudience, setProjectAudience] = useState("");
  const [projectScenario, setProjectScenario] = useState("");
  const [projectQuestions, setProjectQuestions] = useState("");
  const [workTitle, setWorkTitle] = useState("");
  const [workType, setWorkType] = useState("diagnosis");
  const [authId, setAuthId] = useState("");
  const [toolName, setToolName] = useState("geo_visibility");
  const [toolOutput, setToolOutput] = useState("");
  const [artifactTitle, setArtifactTitle] = useState("");
  const [artifactType, setArtifactType] = useState("report");
  const [artifactText, setArtifactText] = useState("");
  const [publishUrl, setPublishUrl] = useState("");
  const [publishRecipient, setPublishRecipient] = useState("");
  const [monitorKey, setMonitorKey] = useState("");
  const [monitorValue, setMonitorValue] = useState("");
  const [monitorRef, setMonitorRef] = useState("");
  const [outcomeClaimId, setOutcomeClaimId] = useState("");
  const [outcomeText, setOutcomeText] = useState("");
  const [outcomeType, setOutcomeType] = useState("visibility_observation");
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    const t = localStorage.getItem("geo_token");
    setToken(t);
    if (!t) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/me`, { headers: authHeaders(t) });
        if (!res.ok) throw new Error("unauthorized");
        setUser(await res.json());
        await loadRealms(t);
      } catch {
        setToken(null);
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function api(path: string, options: RequestInit = {}, authToken?: string | null) {
    const activeToken = authToken ?? token;
    if (!activeToken) return null;
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { ...authHeaders(activeToken), ...(options.headers || {}) },
    });
    if (res.status === 401) {
      setToken(null);
      throw new Error("登录已失效");
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || data.message || "请求失败");
    }
    return res.json();
  }

  async function loadRealms(t: string = token || "") {
    const data = await api("/realm/mine", {}, t);
    setRealms(data?.realms || []);
    if (data?.realms?.length && !selectedId) {
      setSelectedId(data.realms[0].entity_id);
      await selectRealm(data.realms[0].entity_id, t);
    }
  }

  async function selectRealm(id: string, t: string = token || "") {
    setSelectedId(id);
    const ws = await api(`/realm/${id}`, {}, t);
    setWorkspace(ws);
    setProject(null);
    setTimeline([]);
    setProjectAssets({ artifacts: [], realm_data_assets: [] });
  }

  async function run(fn: () => Promise<any>) {
    setError("");
    try {
      const result = await fn();
      await loadRealms();
      if (selectedId) await selectRealm(selectedId);
      return result;
    } catch (e: any) {
      setError(e.message || "操作失败");
      return null;
    }
  }

  async function createEnterprise() {
    if (!entName) return setError("请输入企业名称");
    await run(async () => {
      const ws = await api("/realm/enterprises", {
        method: "POST", body: JSON.stringify({ name: entName, website: entWebsite }),
      });
      setEntName(""); setEntWebsite("");
      if (ws?.identity?.id) await selectRealm(ws.identity.id);
    });
  }

  async function createBrand() {
    if (!brandName) return setError("请输入品牌名称");
    await run(async () => {
      const ws = await api("/realm/brands", {
        method: "POST", body: JSON.stringify({ name: brandName }),
      });
      setBrandName("");
      if (ws?.identity?.id) await selectRealm(ws.identity.id);
    });
  }

  async function claimRealm() {
    if (!claimId) return setError("请输入要认领的实体 ID");
    await run(async () => {
      const result = await api(`/realm/${claimId}/claim`, { method: "POST", body: JSON.stringify({}) });
      setClaimId("");
      if (result?.status === "approved") await selectRealm(claimId);
    });
  }

  async function createAuth() {
    if (!selectedId) return;
    await run(async () => {
      await api(`/realm/${selectedId}/authorizations`, {
        method: "POST",
        body: JSON.stringify({
          source_name: authSource, source_url: authUrl, use_scope: authScope,
        }),
      });
      setAuthSource(""); setAuthUrl("");
    });
  }

  async function createAsset() {
    if (!selectedId || !assetKey || !assetTitle) return setError("资产 key 和标题必填");
    await run(async () => {
      await api(`/realm/${selectedId}/assets`, {
        method: "POST",
        body: JSON.stringify({ asset_key: assetKey, title: assetTitle, asset_type: "document" }),
      });
      setAssetKey(""); setAssetTitle("");
    });
  }

  async function submitEvidence() {
    if (!selectedId || !evClaim || !evUrl) return setError("主张和来源 URL 必填");
    await run(async () => {
      await api(`/realm/${selectedId}/evidence`, {
        method: "POST",
        body: JSON.stringify({ claim: evClaim, source_url: evUrl, source_type: "realm_owner" }),
      });
      setEvClaim(""); setEvUrl("");
    });
  }

  async function createRelation() {
    if (!selectedId || !relationTarget || !relationType) return setError("目标与关系类型必填");
    await run(async () => {
      await api(`/realm/${selectedId}/relationships`, {
        method: "POST",
        body: JSON.stringify({ target_id: relationTarget, relation_type: relationType, description: "域主声明关系" }),
      });
      setRelationTarget("");
    });
  }

  async function createProjectForRealm() {
    if (!workspace?.realm?.id || !projectName) {
      setError("项目名称必填，且需要选择已认领的域");
      return;
    }
    await run(async () => {
      const p = await api("/geo-projects", {
        method: "POST",
        body: JSON.stringify({
          realm_id: workspace.realm.id,
          name: projectName,
          objective: projectObjective,
          target_audience: projectAudience,
          scenario: projectScenario,
          question_set: parseList(projectQuestions),
        }),
      });
      setProjectName(""); setProjectObjective(""); setProjectAudience(""); setProjectScenario(""); setProjectQuestions("");
      if (p?.id) await openProject(p.id);
    });
  }

  async function openProject(id: string) {
    try {
      const p = await api(`/geo-projects/${id}`);
      setProject(p);
      const tl = await api(`/geo-projects/${id}/timeline`);
      setTimeline(tl?.timeline || []);
      const assets = await api(`/geo-projects/${id}/assets`);
    setProjectAssets(assets || { artifacts: [], realm_data_assets: [] });
    const s = await api(`/geo-projects/${id}/summary`);
    setSummary(s || null);
    } catch (e: any) {
      setError(e.message || "加载项目失败");
    }
  }

  async function addWorkItem() {
    if (!project?.id || !workTitle) return setError("工作项标题必填");
    await run(async () => {
      await api(`/geo-projects/${project.id}/work-items`, {
        method: "POST", body: JSON.stringify({ work_type: workType, title: workTitle }),
      });
      setWorkTitle("");
      if (project.id) await openProject(project.id);
    });
  }

  async function addToolRun() {
    if (!project?.id) return;
    if (!authId) return setError("请选择数据授权");
    await run(async () => {
      await api(`/geo-projects/${project.id}/tool-executions`, {
        method: "POST",
        body: JSON.stringify({
          provider: "universe", tool_name: toolName,
          authorization_id: authId,
          model_name: "rule-based", model_version: "1.0",
          output_manifest: { summary: toolOutput },
        }),
      });
      setToolOutput("");
      if (project.id) await openProject(project.id);
    });
  }

  async function runLocalTool() {
    if (!project?.id) return;
    if (!authId) return setError("请选择数据授权");
    await run(async () => {
      await api(`/geo-projects/${project.id}/tool-executions/run`, {
        method: "POST",
        body: JSON.stringify({ authorization_id: authId, tool_name: "geo_visibility" }),
      });
      if (project.id) await openProject(project.id);
    });
  }

  async function addArtifact() {
    if (!project?.id || !artifactTitle) return setError("产物标题必填");
    await run(async () => {
      await api(`/geo-projects/${project.id}/artifacts`, {
        method: "POST",
        body: JSON.stringify({
          artifact_type: artifactType, title: artifactTitle, content_text: artifactText,
        }),
      });
      setArtifactTitle(""); setArtifactText("");
      if (project.id) await openProject(project.id);
    });
  }

  async function publishArtifact(id: string) {
    if (!project?.id) return;
    await run(async () => {
      await api(`/geo-projects/${project.id}/artifacts/${id}/publish`, {
        method: "POST",
        body: JSON.stringify({ published_url: publishUrl, delivery_recipient: publishRecipient }),
      });
      setPublishUrl(""); setPublishRecipient("");
      if (project.id) await openProject(project.id);
    });
  }

  async function recordMonitoring() {
    if (!project?.id || !monitorKey) return setError("监测指标必填");
    await run(async () => {
      await api(`/geo-projects/${project.id}/monitoring-results`, {
        method: "POST",
        body: JSON.stringify({
          metric_key: monitorKey,
          metric_value: Number(monitorValue || 0),
          raw_result_ref: monitorRef,
        }),
      });
      setMonitorKey(""); setMonitorValue(""); setMonitorRef("");
      if (project.id) await openProject(project.id);
    });
  }

  async function addOutcome() {
    if (!project?.id || !outcomeText) return setError("结果主张必填");
    await run(async () => {
      await api(`/geo-projects/${project.id}/outcomes`, {
        method: "POST",
        body: JSON.stringify({
          outcome_type: outcomeType,
          claim_text: outcomeText,
          evidence_claim_id: outcomeClaimId || undefined,
        }),
      });
      setOutcomeText(""); setOutcomeClaimId("");
      if (project.id) await openProject(project.id);
    });
  }

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center bg-slate-50">
        <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (!token || !user) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center bg-slate-50">
        <div className="max-w-md w-full mx-6 border border-slate-200 bg-white rounded-xl p-8 text-center shadow-sm">
          <KeyRound className="w-8 h-8 text-blue-600 mx-auto mb-3" />
          <h1 className="text-lg font-semibold text-slate-900 mb-2">域主看板</h1>
          <p className="text-sm text-slate-500 mb-6">登录后创建或认领企业域、品牌域，并开始首条 GEO 项目闭环。</p>
          <Link href="/login" className="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700">
            登录 <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  const trust = workspace?.position?.trust || {};
  const unknown = workspace?.unknown || [];

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-[1440px] mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-blue-600 flex items-center justify-center">
              <Landmark className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 leading-tight">域主看板</h1>
              <p className="text-sm text-slate-500">恒域世界 · 查看已认领的域并进入域主工作台</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <CircleDot className="w-4 h-4 text-emerald-500" />
            {user.name || user.email}
            <button onClick={() => { localStorage.removeItem("geo_token"); window.location.href = "/login"; }}
              className="ml-2 text-xs text-slate-400 hover:text-rose-600">
              退出
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 px-4 py-3 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-12 lg:col-span-3 space-y-4">
            <Section title="我的域" icon={<Boxes className="w-4 h-4" />}>
              {realms.length === 0 ? (
                <p className="text-sm text-slate-400">暂无已认领的域</p>
              ) : (
                <div className="space-y-2">
                  {realms.map((r: any) => (
                    <button key={r.entity_id} onClick={() => selectRealm(r.entity_id)}
                      className={`w-full text-left rounded-lg border px-3 py-2.5 transition ${
                        selectedId === r.entity_id
                          ? "border-blue-500 bg-blue-50"
                          : "border-slate-200 bg-white hover:border-blue-300"
                      }`}>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium text-slate-800 truncate">{r.name}</span>
                        {r.realm_type === "enterprise"
                          ? <Building2 className="w-4 h-4 text-blue-600" />
                          : <Sparkles className="w-4 h-4 text-amber-500" />}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">{r.realm_type} · {r.realm_code}</div>
                    </button>
                  ))}
                </div>
              )}
            </Section>

            <Section title="创建 / 认领" icon={<Plus className="w-4 h-4" />}>
              <div className="space-y-3">
                <div>
                  <input value={entName} onChange={(e) => setEntName(e.target.value)} placeholder="企业名称"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                  <input value={entWebsite} onChange={(e) => setEntWebsite(e.target.value)} placeholder="官网（可选）"
                    className="mt-2 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                  <button onClick={createEnterprise}
                    className="mt-2 w-full bg-blue-600 text-white rounded-lg py-2 text-sm font-medium hover:bg-blue-700">
                    创建企业域
                  </button>
                </div>
                <div className="pt-2 border-t border-slate-200">
                  <input value={brandName} onChange={(e) => setBrandName(e.target.value)} placeholder="品牌名称"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                  <button onClick={createBrand}
                    className="mt-2 w-full bg-slate-800 text-white rounded-lg py-2 text-sm font-medium hover:bg-slate-900">
                    创建品牌域
                  </button>
                </div>
                <div className="pt-2 border-t border-slate-200">
                  <input value={claimId} onChange={(e) => setClaimId(e.target.value)} placeholder="已有实体 ID"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                  <button onClick={claimRealm}
                    className="mt-2 w-full border border-slate-300 text-slate-700 rounded-lg py-2 text-sm font-medium hover:border-blue-500">
                    认领已有实体
                  </button>
                </div>
              </div>
            </Section>
          </div>

          <div className="col-span-12 lg:col-span-5 space-y-4">
            {workspace ? (
              <>
                <Section title="域状态" icon={<Shield className="w-4 h-4" />}>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <Stat label="域类型" value={workspace.realm?.realm_type || "unknown"} />
                    <Stat label="生命周期" value={workspace.realm?.lifecycle_state || "unknown"} />
                    <Stat label="认领状态" value={workspace.realm?.claim_status || "none"} />
                    <Stat label="可信事实" value={`${trust.verified_evidence || 0}`} />
                  </div>
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="rounded-lg bg-slate-100 px-3 py-2">
                      <div className="text-slate-400">Observed</div>
                      <div className="text-lg font-semibold text-slate-800 mt-1">{trust.observed_evidence || 0}</div>
                    </div>
                    <div className="rounded-lg bg-slate-100 px-3 py-2">
                      <div className="text-slate-400">Verified</div>
                      <div className="text-lg font-semibold text-emerald-600 mt-1">{trust.verified_evidence || 0}</div>
                    </div>
                    <div className="rounded-lg bg-slate-100 px-3 py-2">
                      <div className="text-slate-400">Synthetic</div>
                      <div className="text-lg font-semibold text-amber-600 mt-1">{trust.synthetic_evidence || 0}</div>
                    </div>
                    <div className="rounded-lg bg-slate-100 px-3 py-2">
                      <div className="text-slate-400">Verified Claim</div>
                      <div className="text-lg font-semibold text-blue-600 mt-1">{trust.verified_claims || 0}</div>
                    </div>
                  </div>
                  {unknown.length > 0 && (
                    <div className="mt-4 space-y-1.5">
                      {unknown.map((u: string, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-amber-700">
                          <AlertCircle className="w-3.5 h-3.5" /> {u}
                        </div>
                      ))}
                    </div>
                  )}
                </Section>

                <Section title="数据授权与资产" icon={<Database className="w-4 h-4" />}>
                  <div className="grid md:grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <input value={authSource} onChange={(e) => setAuthSource(e.target.value)} placeholder="来源名称"
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                      <input value={authUrl} onChange={(e) => setAuthUrl(e.target.value)} placeholder="来源 URL"
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                      <select value={authScope} onChange={(e) => setAuthScope(e.target.value)}
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                        <option value="realm_owner">域主自有</option>
                        <option value="project_evidence">项目证据</option>
                        <option value="ai_tools">AI 工具</option>
                        <option value="simulation">模拟</option>
                      </select>
                      <button onClick={createAuth}
                        className="w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                        添加授权
                      </button>
                    </div>
                    <div className="space-y-2">
                      <input value={assetKey} onChange={(e) => setAssetKey(e.target.value)} placeholder="资产 key"
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                      <input value={assetTitle} onChange={(e) => setAssetTitle(e.target.value)} placeholder="资产标题"
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
                      <button onClick={createAsset}
                        className="w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                        登记资产
                      </button>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <input value={evClaim} onChange={(e) => setEvClaim(e.target.value)} placeholder="自有数据主张"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <div className="flex gap-2">
                      <input value={evUrl} onChange={(e) => setEvUrl(e.target.value)} placeholder="来源 URL"
                        className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                      <button onClick={submitEvidence}
                        className="px-4 bg-slate-800 text-white rounded-lg text-sm hover:bg-slate-900">
                        导入
                      </button>
                    </div>
                  </div>
                  {workspace.assets?.length > 0 && (
                    <div className="mt-4 border-t border-slate-200 pt-3">
                      <div className="text-xs text-slate-400 mb-2">资产清单</div>
                      <div className="space-y-1.5">
                        {workspace.assets.map((a: any) => (
                          <div key={a.id} className="flex items-center justify-between text-sm">
                            <span className="text-slate-700">{a.title}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              a.truth_status === "observed" ? "bg-slate-100 text-slate-500" : "bg-amber-50 text-amber-600"
                            }`}>{a.truth_status}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </Section>

                <Section title="关系与证据" icon={<GitBranch className="w-4 h-4" />}>
                  <div className="grid md:grid-cols-2 gap-3">
                    <div>
                      <input value={relationTarget} onChange={(e) => setRelationTarget(e.target.value)} placeholder="目标实体 ID"
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                      <select value={relationType} onChange={(e) => setRelationType(e.target.value)}
                        className="mt-2 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                        <option value="partner">合作</option>
                        <option value="competitor">竞争</option>
                        <option value="supplier">供应</option>
                        <option value="customer">客户</option>
                        <option value="influence">影响</option>
                      </select>
                      <button onClick={createRelation}
                        className="mt-2 w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                        建立关系
                      </button>
                    </div>
                    <div className="text-sm text-slate-500">
                      {workspace.evidence?.length > 0 ? (
                        <div className="space-y-2 max-h-44 overflow-auto pr-1">
                          {workspace.evidence.slice(0, 8).map((e: any) => (
                            <div key={e.id} className="rounded-lg bg-slate-50 px-3 py-2">
                              <div className="text-xs text-slate-700 line-clamp-2">{e.claim}</div>
                              <div className="text-[10px] text-slate-400 mt-1">{e.truth_status} · {e.may_affect_real_metrics ? "可进入真实指标" : "隔离"}</div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-slate-400 text-xs">尚未导入自有数据</div>
                      )}
                    </div>
                  </div>
                </Section>
              </>
            ) : (
              <div className="rounded-xl border border-slate-200 bg-white p-10 text-center">
                <Building2 className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                <p className="text-sm text-slate-400">选择或创建一个域</p>
              </div>
            )}
          </div>

          <div className="col-span-12 lg:col-span-4 space-y-4">
            <Section title="GEO 项目" icon={<FolderKanban className="w-4 h-4" />}>
              {workspace && (
                <div className="space-y-2">
                  <input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="项目名称"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                  <input value={projectObjective} onChange={(e) => setProjectObjective(e.target.value)} placeholder="目标"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                  <input value={projectAudience} onChange={(e) => setProjectAudience(e.target.value)} placeholder="目标人群"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                  <input value={projectScenario} onChange={(e) => setProjectScenario(e.target.value)} placeholder="场景"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                  <input value={projectQuestions} onChange={(e) => setProjectQuestions(e.target.value)} placeholder="AI 问题集，逗号分隔"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                  <button onClick={createProjectForRealm}
                    className="w-full bg-blue-600 text-white rounded-lg py-2 text-sm font-medium hover:bg-blue-700">
                    创建 GEO 项目
                  </button>
                </div>
              )}
              <div className="mt-4 space-y-2">
                {workspace?.projects?.map((p: any) => (
                  <button key={p.id} onClick={() => openProject(p.id)}
                    className={`w-full text-left rounded-lg border px-3 py-2.5 ${
                      project?.id === p.id ? "border-blue-500 bg-blue-50" : "border-slate-200 bg-white hover:border-blue-300"
                    }`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-slate-800 truncate">{p.name}</span>
                      <span className="text-xs text-slate-400">{p.status}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">{p.project_code} · {p.truth_status}</div>
                  </button>
                ))}
              </div>
            </Section>

            {project && (
              <>
                <Section title="项目执行" icon={<Bot className="w-4 h-4" />}>
                  <div className="space-y-2">
                    <input value={workTitle} onChange={(e) => setWorkTitle(e.target.value)} placeholder="工作项标题"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <select value={workType} onChange={(e) => setWorkType(e.target.value)}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                      <option value="diagnosis">诊断</option>
                      <option value="content">内容</option>
                      <option value="report">报告</option>
                      <option value="execution">执行</option>
                      <option value="measurement">测量</option>
                    </select>
                    <button onClick={addWorkItem}
                      className="w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                      记录工作项
                    </button>
                  </div>
                  <div className="mt-3 space-y-2">
                    {workspace?.authorizations?.length > 0 && (
                      <select value={authId} onChange={(e) => setAuthId(e.target.value)}
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                        <option value="">选择数据授权</option>
                        {workspace.authorizations.filter((a: any) => a.status === "active").map((a: any) => (
                          <option key={a.id} value={a.id}>{a.source_name || a.use_scope} · {a.status}</option>
                        ))}
                      </select>
                    )}
                    <input value={toolOutput} onChange={(e) => setToolOutput(e.target.value)} placeholder="工具输出摘要"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <button onClick={addToolRun}
                      className="w-full bg-slate-800 text-white rounded-lg py-2 text-sm hover:bg-slate-900">
                      记录执行声明
                    </button>
                    <button onClick={runLocalTool}
                      className="w-full bg-blue-600 text-white rounded-lg py-2 text-sm hover:bg-blue-700">
                      运行本地真实工具
                    </button>
                  </div>
                  <div className="mt-3 space-y-2">
                    <input value={artifactTitle} onChange={(e) => setArtifactTitle(e.target.value)} placeholder="产物标题"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <select value={artifactType} onChange={(e) => setArtifactType(e.target.value)}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                      <option value="diagnosis">诊断</option>
                      <option value="report">报告</option>
                      <option value="content">内容</option>
                      <option value="measurement">测量</option>
                    </select>
                    <textarea value={artifactText} onChange={(e) => setArtifactText(e.target.value)} placeholder="产物内容"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm min-h-20" />
                    <button onClick={addArtifact}
                      className="w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                      保存产物
                    </button>
                  </div>
                  <div className="mt-3 space-y-2">
                    <input value={outcomeClaimId} onChange={(e) => setOutcomeClaimId(e.target.value)} placeholder="Evidence Claim ID（可选）"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <input value={outcomeText} onChange={(e) => setOutcomeText(e.target.value)} placeholder="结果主张"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <select value={outcomeType} onChange={(e) => setOutcomeType(e.target.value)}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                      <option value="visibility_observation">可见性观察</option>
                      <option value="content_published">内容发布</option>
                      <option value="connection_formed">连接形成</option>
                      <option value="evidence_claim">证据主张</option>
                    </select>
                    <button onClick={addOutcome}
                      className="w-full bg-white border border-slate-300 text-slate-700 rounded-lg py-2 text-sm hover:border-blue-500">
                      记录结果
                    </button>
                  </div>
                </Section>

                <Section title="执行时间线" icon={<RefreshCw className="w-4 h-4" />}>
                  {timeline.length > 0 ? (
                    <div className="space-y-2">
                      {timeline.slice(0, 10).map((t: any, i: number) => (
                        <div key={i} className="flex items-start gap-2">
                          <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                          <div className="min-w-0">
                            <div className="text-sm text-slate-700 truncate">{t.label}</div>
                            <div className="text-[10px] text-slate-400 mt-0.5">{t.type} · {t.status} · {t.truth_status}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400">暂无执行记录</p>
                  )}
                </Section>

                <Section title="项目产物" icon={<FileText className="w-4 h-4" />}>
                  {projectAssets.artifacts?.length > 0 ? (
                    <div className="space-y-2">
                      {projectAssets.artifacts.map((a: any) => (
                        <div key={a.id} className="rounded-lg bg-white border border-slate-200 px-3 py-2">
                          <div className="flex items-center justify-between gap-2">
                            <div className="text-sm text-slate-700">{a.title}</div>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              a.status === "published" ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-500"
                            }`}>{a.status}</span>
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">{a.artifact_type} · {a.truth_status}</div>
                          {a.status !== "published" && (
                            <div className="mt-2 flex gap-2">
                              <input value={publishUrl} onChange={(e) => setPublishUrl(e.target.value)}
                                placeholder="发布 URL / 交付凭证"
                                className="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 text-xs" />
                              <input value={publishRecipient} onChange={(e) => setPublishRecipient(e.target.value)}
                                placeholder="平台 / 对象"
                                className="w-28 border border-slate-300 rounded-lg px-2 py-1.5 text-xs" />
                              <button onClick={() => publishArtifact(a.id)}
                                className="px-3 bg-emerald-600 text-white rounded-lg text-xs hover:bg-emerald-700">
                                发布
                              </button>
                            </div>
                          )}
                          {a.published_url && (
                            <a href={a.published_url} target="_blank" rel="noreferrer"
                              className="mt-2 block text-xs text-blue-600 truncate">{a.published_url}</a>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400">暂无项目产物</p>
                  )}
                </Section>

                <Section title="监测回填" icon={<RefreshCw className="w-4 h-4" />}>
                  <div className="space-y-2">
                    <input value={monitorKey} onChange={(e) => setMonitorKey(e.target.value)}
                      placeholder="监测指标，如 mention_rate" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    <div className="flex gap-2">
                      <input value={monitorValue} onChange={(e) => setMonitorValue(e.target.value)}
                        type="number" placeholder="指标值" className="w-32 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                      <input value={monitorRef} onChange={(e) => setMonitorRef(e.target.value)}
                        placeholder="原始结果引用" className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                    </div>
                    <button onClick={recordMonitoring}
                      className="w-full bg-slate-800 text-white rounded-lg py-2 text-sm hover:bg-slate-900">
                      记录监测结果
                    </button>
                  </div>
                  {summary && (
                    <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                      <div className="rounded-lg bg-slate-100 px-3 py-2">
                        <div className="text-slate-400">已发布产物</div>
                        <div className="text-lg font-semibold text-slate-800">{summary.artifacts?.published || 0}</div>
                      </div>
                      <div className="rounded-lg bg-slate-100 px-3 py-2">
                        <div className="text-slate-400">系统执行</div>
                        <div className="text-lg font-semibold text-slate-800">{summary.tool_executions?.system || 0}</div>
                      </div>
                      <div className="rounded-lg bg-slate-100 px-3 py-2">
                        <div className="text-slate-400">工具成本</div>
                        <div className="text-lg font-semibold text-slate-800">{summary.tool_executions?.cost || 0}</div>
                      </div>
                      <div className="rounded-lg bg-slate-100 px-3 py-2">
                        <div className="text-slate-400">监测结果</div>
                        <div className="text-lg font-semibold text-slate-800">{summary.monitoring_results || 0}</div>
                      </div>
                    </div>
                  )}
                </Section>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-3">
        {icon} {title}
      </h2>
      {children}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-100 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-slate-400">{label}</div>
      <div className="text-sm font-semibold text-slate-800 mt-1 truncate">{value}</div>
    </div>
  );
}
