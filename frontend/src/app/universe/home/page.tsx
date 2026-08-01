"use client";

import { useState, useEffect } from "react";
import {
  Building2, Users, Bot, Landmark, Target, Compass, Shield,
  Eye, Zap, Clock, Loader2, ChevronRight, TrendingUp, Link2,
  Star, Award, AlertCircle, CheckCircle2, ArrowUpRight,
  Network, Database, Sparkles, Layers, GitBranch, Radio,
  Activity, Crosshair, BookOpen, Briefcase, Search, RefreshCw,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getNodeTypeIcon(type: string) {
  switch (type) {
    case "company": return <Building2 className="w-4 h-4" />;
    case "provider": return <Users className="w-4 h-4" />;
    case "ai_agent": return <Bot className="w-4 h-4" />;
    case "government": return <Landmark className="w-4 h-4" />;
    default: return <Target className="w-4 h-4" />;
  }
}

function getNodeTypeLabel(type: string) {
  const map: Record<string, string> = {
    company: "企业", provider: "服务商", ai_agent: "AI Agent", government: "政府",
  };
  return map[type] || type;
}

function scoreColor(v: number) {
  if (v >= 70) return "text-emerald-400";
  if (v >= 40) return "text-amber-400";
  return "text-rose-400";
}

function barColor(v: number) {
  if (v >= 70) return "bg-emerald-500";
  if (v >= 40) return "bg-amber-500";
  return "bg-rose-500";
}

export default function UniverseHomePage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [nodeType, setNodeType] = useState("company");
  const [nodeIdInput, setNodeIdInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [panelLoading, setPanelLoading] = useState(false);
  const [repLoading, setRepLoading] = useState(false);
  const [oppLoading, setOppLoading] = useState(false);
  const [panel, setPanel] = useState<any>(null);
  const [reputation, setReputation] = useState<any>(null);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/companies/`)
      .then(r => r.json())
      .then((data: any) => {
        const list = Array.isArray(data) ? data : (data.companies || data.items || []);
        setCompanies(list.slice(0, 8));
        if (list.length > 0) {
          setSelected(list[0]);
          setNodeIdInput((list[0].id || "").replace(/^comp_/, ""));
        }
        setLoading(false);
      })
      .catch(() => { setLoading(false); setError("无法连接后端服务"); });
  }, []);

  useEffect(() => {
    if (!selected) return;
    const rawId = (selected.id || "").replace(/^comp_/, "");
    const type = selected.type || "company";

    setPanelLoading(true); setRepLoading(true); setOppLoading(true); setError("");

    fetch(`${API_BASE}/universe/home/${type}/${rawId}`)
      .then(r => r.ok ? r.json() : null)
      .then(setPanel)
      .catch(() => setPanel(null))
      .finally(() => setPanelLoading(false));

    fetch(`${API_BASE}/universe/reputation/node/${rawId}`)
      .then(r => r.ok ? r.json() : null)
      .then(setReputation)
      .catch(() => setReputation(null))
      .finally(() => setRepLoading(false));

    fetch(`${API_BASE}/universe/intelligence/opportunities/${rawId}`)
      .then(r => r.ok ? r.json() : [])
      .then((data: any) => setOpportunities(Array.isArray(data) ? data : []))
      .catch(() => setOpportunities([]))
      .finally(() => setOppLoading(false));
  }, [selected]);

  const handleSearch = async () => {
    const id = nodeIdInput.trim();
    if (!id) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/universe/home/${nodeType}/${id}`);
      if (!res.ok) throw new Error("节点不存在");
      const data = await res.json();
      setSelected({ id, type: nodeType, name: data?.data?.node?.name || id, ...(data?.data?.node || {}) });
    } catch (e: any) {
      setError(e.message || "查询失败");
    } finally {
      setLoading(false);
    }
  };

  const refreshAll = async () => {
    if (!selected) return;
    const rawId = (selected.id || "").replace(/^comp_/, "");
    const type = selected.type || "company";
    setPanelLoading(true); setRepLoading(true); setOppLoading(true);
    try {
      const [p, r, o] = await Promise.all([
        fetch(`${API_BASE}/universe/home/${type}/${rawId}`).then(x => x.ok ? x.json() : null),
        fetch(`${API_BASE}/universe/reputation/node/${rawId}`).then(x => x.ok ? x.json() : null),
        fetch(`${API_BASE}/universe/intelligence/opportunities/${rawId}`).then(x => x.ok ? x.json() : []),
      ]);
      setPanel(p); setReputation(r);
      setOpportunities(Array.isArray(o) ? o : []);
    } catch { /* silent */ }
    setPanelLoading(false); setRepLoading(false); setOppLoading(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-[70vh] bg-slate-950">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  const node = panel?.identity || selected || {};
  const position = panel?.position || {};
  const positionData = position.position || {};
  const interpretation = position.interpretation || {};
  const intelligence = panel?.capability || {};
  const graph = panel?.relationship || {};
  const evolution = panel?.memory || {};
  const memoryTimeline = evolution.timeline || {};
  const velocity = evolution.velocity || {};
  const possibility = panel?.possibility || {};
  const possibilityStates = possibility.states || {};
  const possibilityTransitions = possibility.transitions || [];
  const connectionNeeds = possibility.connection_needs || [];
  const geoScore = node.geo_score ?? 0;
  const trust = node.trust_score ?? panel?.reputation?.overall_score ?? 0;
  const evidenceCount = memoryTimeline?.layers?.facts?.count ?? 0;
  const capCount = intelligence.total_acquired ?? intelligence.acquired?.length ?? 0;
  const relCount = graph.total ?? 0;
  const growthStage = positionData.growth_stage || node.growth_stage || "position";
  const repStatus = panel?.reputation?.status || reputation?.status || "N/A";
  const repScore = panel?.reputation?.overall_score ?? reputation?.overall_score ?? 0;
  const repLevel = panel?.reputation?.overall_level || reputation?.overall_level || "N/A";
  const repDims = panel?.reputation?.dimensions || reputation?.dimensions || {};
  const repTrend = panel?.reputation?.trend || reputation?.trend || "stable";
  const significantEvents = memoryTimeline?.significant_events || [];

  const stageLabels: Record<string, string> = {
    position: "定位", selfknow: "自知", action: "行动",
    provision: "使用", accumulate: "沉淀", reputation: "信誉",
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-[1440px] mx-auto px-6 py-6">

        <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Activity className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold leading-tight">Universe Home</h1>
              <p className="text-sm text-slate-400">节点认知、信誉、关系与机会的完整视图</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5">
              {["company", "provider", "ai_agent", "government"].map(t => (
                <button key={t} onClick={() => setNodeType(t)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${nodeType === t ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white"}`}>
                  {getNodeTypeLabel(t)}
                </button>
              ))}
            </div>
            <input
              value={nodeIdInput}
              onChange={e => setNodeIdInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="Node ID"
              className="w-44 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
            />
            <button onClick={handleSearch}
              className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:border-blue-500 transition">
              <Search className="w-4 h-4 text-slate-400" />
            </button>
            <button onClick={refreshAll}
              className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:border-blue-500 transition">
              <RefreshCw className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-sm text-rose-300">
            {error}
          </div>
        )}

        {!selected ? (
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-16 text-center">
            <div className="w-16 h-16 mx-auto rounded-full bg-blue-500/10 flex items-center justify-center mb-4">
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">选择或搜索一个节点</h3>
            <p className="text-slate-400 text-sm">输入节点 ID 或从列表中选择，查看完整的 Universe 认知。</p>
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-4">

            <div className="col-span-12 lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                  {getNodeTypeIcon(nodeType)}
                </div>
                <div className="min-w-0">
                  <h2 className="font-semibold truncate">{node.name || selected.name || "Unknown Node"}</h2>
                  <p className="text-xs text-slate-500">{getNodeTypeLabel(nodeType)} · {selected.id}</p>
                </div>
              </div>

              <div className="space-y-3 text-sm">
                <InfoRow label="成长阶段" value={stageLabels[growthStage] || growthStage} icon={<Crosshair className="w-3.5 h-3.5 text-blue-400" />} />
                <InfoRow label="信誉状态" value={`${repStatus} (${repLevel})`} icon={<Shield className="w-3.5 h-3.5 text-emerald-400" />} />
                <InfoRow label="趋势" value={repTrend} icon={<TrendingUp className="w-3.5 h-3.5 text-purple-400" />} />
                <InfoRow label="GEO Score" value={String(geoScore ?? 0)} icon={<Award className="w-3.5 h-3.5 text-amber-400" />} />
              </div>

              <div className="mt-5 pt-4 border-t border-slate-800">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">关键指标</h3>
                <div className="space-y-3">
                  <MetricBar label="GEO Score" value={geoScore || 0} max={100} />
                  <MetricBar label="Trust" value={trust || 0} max={100} />
                  <MetricBar label="Evidence" value={evidenceCount || 0} max={20} />
                  <MetricBar label="Capability" value={capCount || 0} max={15} />
                  <MetricBar label="Relationship" value={relCount || 0} max={15} />
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-800">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">节点导航</h3>
                <div className="space-y-1">
                  {[
                    ["/universe/3d", "3D Universe", GitBranch],
                    ["/universe/connections", "未来连接", Link2],
                    ["/universe/growth", "成长轨迹", TrendingUp],
                    ["/universe/opportunities", "机会方向", Briefcase],
                  ].map(([href, label, Icon]: any) => (
                    <a key={href} href={href}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-slate-800 hover:text-white transition group">
                      <Icon className="w-4 h-4" />
                      {label}
                      <ChevronRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100" />
                    </a>
                  ))}
                </div>
              </div>
            </div>

            <div className="col-span-12 lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-blue-400" /> 我的位置
              </h3>
              {positionData.industry_rank != null && (
                <div className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-500">行业位置</span>
                    <span className="text-blue-300 font-medium">Top {(positionData.industry_rank * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full">
                    <div className="h-full rounded-full bg-blue-500" style={{ width: Math.max(8, (1 - positionData.industry_rank) * 100) + "%" }} />
                  </div>
                </div>
              )}
              <div className="space-y-2 text-xs mb-4">
                <InfoRow label="成长阶段" value={stageLabels[growthStage] || growthStage} icon={<Activity className="w-3.5 h-3.5 text-blue-400" />} />
                <InfoRow label="信誉等级" value={positionData.reputation_level || repLevel} icon={<Shield className="w-3.5 h-3.5 text-emerald-400" />} />
                <InfoRow label="影响力" value={String(positionData.influence_score ?? 0)} icon={<Zap className="w-3.5 h-3.5 text-amber-400" />} />
                {positionData.capability_rank != null && (
                  <InfoRow label="能力位置" value={`Top ${(positionData.capability_rank * 100).toFixed(0)}%`} icon={<Layers className="w-3.5 h-3.5 text-purple-400" />} />
                )}
              </div>
              {interpretation.narrative && (
                <p className="text-xs text-slate-400 leading-relaxed mb-3">{interpretation.narrative}</p>
              )}
              <div className="flex flex-wrap gap-1.5">
                {(interpretation.strengths || []).slice(0, 2).map((s: string, i: number) => (
                  <span key={i} className="text-[10px] px-2 py-1 rounded bg-emerald-500/10 text-emerald-400">{s}</span>
                ))}
                {(interpretation.gaps || []).slice(0, 2).map((g: string, i: number) => (
                  <span key={i} className="text-[10px] px-2 py-1 rounded bg-rose-500/10 text-rose-400">{g}</span>
                ))}
              </div>
            </div>

            <div className="col-span-12 lg:col-span-6 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                    <Shield className="w-4 h-4 text-emerald-400" /> 信誉向量
                  </h3>
                  {repLoading ? <Loader2 className="w-4 h-4 text-slate-500 animate-spin" /> : (
                    <span className={`text-xs px-2 py-0.5 rounded ${repTrend === "rising" ? "bg-emerald-500/10 text-emerald-400" : repTrend === "falling" ? "bg-rose-500/10 text-rose-400" : "bg-slate-800 text-slate-400"}`}>
                      {repTrend === "rising" ? "↑ Rising" : repTrend === "falling" ? "↓ Falling" : "Stable"}
                    </span>
                  )}
                </div>

                {reputation ? (
                  <>
                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-center">
                        <div className={`text-4xl font-bold ${scoreColor(repScore)}`}>{repScore}</div>
                        <div className="text-xs text-slate-500 mt-1">Overall ({repLevel})</div>
                      </div>
                      <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${barColor(repScore)}`} style={{ width: Math.min(repScore, 100) + "%" }} />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(repDims).map(([key, val]: any) => (
                        <div key={key} className="bg-slate-800/50 rounded-lg p-3">
                          <div className="text-[10px] text-slate-500 uppercase">{key}</div>
                          <div className="text-lg font-semibold mt-1">{val?.score != null ? val.score : "N/A"}</div>
                          <div className={`text-[10px] ${val?.level && val.level !== "N/A" ? "text-emerald-400" : "text-slate-600"}`}>
                            {val?.level || "N/A"}
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-slate-500">暂无信誉数据。记录信誉事件后将在此显示。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-purple-400" /> 能力
                </h3>
                {panelLoading ? (
                  <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
                ) : intelligence.capabilities?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {intelligence.capabilities.slice(0, 10).map((c: any, i: number) => (
                      <span key={i} className="px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-300 text-xs border border-purple-500/20">
                        {c.name || c}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无能力数据。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400" /> 风险信号
                </h3>
                {panelLoading ? (
                  <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
                ) : intelligence.risks?.length > 0 ? (
                  <div className="space-y-2">
                    {intelligence.risks.slice(0, 4).map((r: any, i: number) => (
                      <div key={i} className="flex items-start gap-2 text-xs">
                        <AlertCircle className="w-3.5 h-3.5 text-rose-400 mt-0.5 flex-shrink-0" />
                        <span className="text-slate-300">{r.description || r.signal || r}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无风险信号。</p>
                )}
              </div>
            </div>

            <div className="col-span-12 lg:col-span-3 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-400" /> 成长轨迹
                </h3>
                {velocity.trend && velocity.trend !== "unknown" && (
                  <div className="mb-3 flex items-center gap-2 text-xs">
                    <span className="text-slate-500">速度</span>
                    <span className={velocity.trend === "accelerating" ? "text-emerald-400" : velocity.trend === "decelerating" ? "text-rose-400" : "text-slate-300"}>
                      {velocity.trend === "accelerating" ? "↑ 加速" : velocity.trend === "decelerating" ? "↓ 减速" : "→ 稳定"}
                    </span>
                    <span className="text-slate-600">· {velocity.velocity ?? 0} facts/月</span>
                  </div>
                )}
                {significantEvents.length > 0 ? (
                  <div className="space-y-3">
                    {significantEvents.slice(0, 4).map((t: any, i: number) => (
                      <div key={i} className="flex items-start gap-2">
                        <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${t.significance >= 0.5 ? "bg-blue-400" : "bg-slate-600"}`} />
                        <div>
                          <p className="text-xs text-slate-300">{t.title}</p>
                          <p className="text-[10px] text-slate-600">{t.date || ""}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无事件记录。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-purple-400" /> 未来可能性
                </h3>
                {Object.keys(possibilityStates).length > 1 ? (
                  <div className="space-y-3">
                    {[30, 90, 180].map(horizon => {
                      const states = Object.values(possibilityStates).filter((s: any) => s.horizon_days === horizon);
                      if (!states.length) return null;
                      const s: any = states[0];
                      return (
                        <div key={horizon} className="bg-slate-800/50 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="text-[10px] text-slate-500 uppercase">T+{horizon}</span>
                            <span className="text-xs font-semibold text-purple-300">{s.stage || s.horizon}</span>
                          </div>
                          <p className="text-[10px] text-slate-400 line-clamp-2">{s.description}</p>
                          <div className="mt-2 flex items-center gap-1 text-[10px]">
                            <TrendingUp className="w-3 h-3 text-purple-400" />
                            <span className="text-slate-500">影响力 {s.influence ?? 0}</span>
                            <span className="text-slate-600">· 能力 +{(s.new_capabilities || []).length}</span>
                          </div>
                        </div>
                      );
                    })}
                    {connectionNeeds.length > 0 && (
                      <div className="pt-2 border-t border-slate-800">
                        <p className="text-[10px] text-slate-500 uppercase mb-2">需要的连接</p>
                        <div className="flex flex-wrap gap-1.5">
                          {connectionNeeds.slice(0, 4).map((n: any, i: number) => (
                            <span key={i} className="text-[10px] px-2 py-1 rounded bg-purple-500/10 text-purple-300">{n.type}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无未来推演。运行决策分析后生成。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" /> 关系机会
                </h3>
                {oppLoading ? (
                  <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
                ) : opportunities.length > 0 ? (
                  <div className="space-y-3">
                    {opportunities.slice(0, 4).map((o: any, i: number) => (
                      <div key={i} className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium truncate">{o.node_b_name || o.node_b_id}</span>
                          <span className={`text-xs font-bold ${scoreColor(o.confidence * 100)}`}>
                            {(o.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500 line-clamp-2">{o.recommended_action}</p>
                        {o.risks?.length > 0 && (
                          <div className="mt-2 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3 text-rose-400" />
                            <span className="text-[10px] text-rose-300">{o.risks[0].description}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无关系机会。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-400" /> 最近活动
                </h3>
                {panelLoading ? (
                  <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />
                ) : evolution.timeline?.length > 0 ? (
                  <div className="space-y-3">
                    {evolution.timeline.slice(0, 5).map((t: any, i: number) => (
                      <div key={i} className="flex items-start gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                        <div>
                          <p className="text-xs text-slate-300">{t.label || t.event || t}</p>
                          <p className="text-[10px] text-slate-600">{t.date || t.timestamp || ""}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">暂无活动记录。</p>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Universe 链路</h3>
                <div className="space-y-1 text-xs text-slate-500">
                  <ChainStep done={!!node} label="Observation" />
                  <ChainStep done={evidenceCount > 0} label="Evidence" />
                  <ChainStep done={capCount > 0} label="Capability" />
                  <ChainStep done={repScore > 0} label="Reputation" />
                  <ChainStep done={relCount > 0} label="Relationship" />
                  <ChainStep done={opportunities.length > 0} label="Opportunity" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoRow({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-2 text-slate-500 text-xs">{icon}{label}</span>
      <span className="text-slate-200 font-medium text-xs">{value}</span>
    </div>
  );
}

function MetricBar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.min(Math.round((value / max) * 100), 100);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-500">{label}</span>
        <span className="text-slate-300 font-medium">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-slate-800 rounded-full">
        <div className={`h-full rounded-full ${barColor(pct)}`} style={{ width: pct + "%" }} />
      </div>
    </div>
  );
}

function ChainStep({ done, label }: { done: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2 py-0.5">
      {done ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Radio className="w-3.5 h-3.5 text-slate-700" />}
      <span className={done ? "text-slate-300" : "text-slate-600"}>{label}</span>
    </div>
  );
}
