"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Shield, TrendingUp, AlertTriangle, Map, BarChart3, Target, ArrowRight, Search, ExternalLink, Building2, Users, Award, Calendar, Activity } from "lucide-react";
import EvolutionTimeline from "@/components/EvolutionTimeline";

export default function CompanyPage() {
  const { id } = useParams();
  const [ctx, setCtx] = useState(null as any);
  const [dec, setDec] = useState(null as any);
  const [agent, setAgent] = useState(null as any);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");

  useEffect(() => { loadAll(); }, [id]);

  async function loadAll() {
    try {
      const { api } = await import("@/lib/api");
      const cid = id as string;
      const [ctxData, decData, agentData] = await Promise.all([
        api.context.company(cid),
        api.decision.company(cid),
        api.agent.analyze(cid + " GEO"),
      ]);
      setCtx(ctxData);
      setDec(decData);
      setAgent(agentData);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  if (loading) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
    </div>
  );

  const c = ctx?.company || {};
  const s = ctx?.scoring || {};
  const d = dec || {};
  const caps = ctx?.capabilities || [];
  const evs = ctx?.evidence || [];
  const rels = ctx?.relationships || [];
  const events = ctx?.events || [];
  const score = d?.overall ?? s?.overall ?? 0;

  const tabs = [
    { key: "overview", label: "GEO身份卡", icon: Shield },
    { key: "score", label: "评分详情", icon: BarChart3 },
    { key: "capability", label: "能力画像", icon: Target },
    { key: "evidence", label: "信任证据", icon: Award },
    { key: "network", label: "产业关系", icon: Users },
    { key: "events", label: "事件轨迹", icon: Calendar },
    { key: "strategy", label: "战略报告", icon: TrendingUp },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Nav */}
      <header className="border-b border-slate-800 px-6 py-3 flex items-center justify-between bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <Link href="/" className="text-slate-400 hover:text-white text-sm flex items-center gap-2">
          <Building2 className="w-4 h-4" /> GEO 产业生态
        </Link>
        <div className="flex gap-2 text-xs">
          <Link href="/detection" className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded">检测中心</Link>
          <Link href="/certification" className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded">认证中心</Link>
          <Link href="/navigation" className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded">产业导航</Link>
          <Link href="/marketplace" className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded">交易市场</Link>
        </div>
      </header>

      {/* Hero Identity Card */}
      <section className="border-b border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/30 px-6 py-8">
        <div className="max-w-6xl mx-auto flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{c.name}</h1>
              {c.is_verified && <Award className="w-5 h-5 text-emerald-400" />}
            </div>
            <p className="text-slate-400 text-sm">{c.description}</p>
            <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
              <span>GEO ID: {c.geo_id || "待生成"}</span>
              <span>|</span>
              <span>{c.headquarters || "未设置"}</span>
              <span>|</span>
              <span>{c.company_size || "未知规模"}</span>
              <span>|</span>
              <span>成立: {c.founded_year || "-"}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-6xl font-bold text-emerald-400 tabular-nums">{score}</div>
            <div className="text-xs text-slate-500 mt-1">GEO Score</div>
            <div className={score >= 70 ? "text-emerald-400 text-sm" : score >= 40 ? "text-yellow-400 text-sm" : "text-red-400 text-sm"}>
              {score >= 70 ? "A级·领先" : score >= 40 ? "B级·成长中" : "C级·待提升"}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Action Bar */}
      <div className="max-w-6xl mx-auto mt-6 flex flex-wrap items-center gap-3">
        <Link href={"/certification/apply?company=" + (c.geo_id || id)}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-black font-semibold rounded-lg text-sm transition-colors shadow-lg shadow-emerald-500/20">
          <Award className="w-4 h-4" /> 申请认证
        </Link>
        <button onClick={async () => {
          try { const { api } = await import("@/lib/api"); const r = await api.agent.analyze("优化 " + (c.name || "") + " GEO表现"); }
          catch(e) { console.error(e); }
        }}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-sm transition-colors">
          <TrendingUp className="w-4 h-4" /> 生成优化方案
        </button>
        <Link href={"/marketplace?from=" + (c.geo_id || id)}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg text-sm transition-colors">
          <Users className="w-4 h-4" /> 寻找合作伙伴
        </Link>
        <button onClick={() => {
          const btn = document.activeElement;
          if (btn) { btn.textContent = "已关注"; btn.classList.add("opacity-50"); }
        }}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 font-medium rounded-lg text-sm transition-colors border border-slate-600">
          <Activity className="w-4 h-4" /> 加入关注
        </button>
        {!c.is_verified && (
          <span className="text-xs text-slate-500 ml-auto hidden md:block">
            认证后解锁交易市场全部功能
          </span>
        )}
      </div>
      {/* Tab Nav */}
      <nav className="border-b border-slate-800 px-6 py-0 sticky top-[57px] z-40 bg-slate-950">
        <div className="max-w-6xl mx-auto flex gap-1 overflow-x-auto">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={"flex items-center gap-1.5 px-4 py-3 text-sm whitespace-nowrap border-b-2 transition-colors " +
                (tab === t.key ? "border-emerald-400 text-emerald-400" : "border-transparent text-slate-500 hover:text-slate-300")}>
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-6">
        {/* OVERVIEW TAB */}
        {tab === "overview" && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { label: "AI可见度", value: d?.visibility?.score ?? s?.geo_score ?? "-", color: "text-blue-400" },
                { label: "可信度", value: d?.trust?.score ?? s?.trust_score ?? "-", color: "text-emerald-400" },
                { label: "增长力", value: d?.growth?.score ?? "-", color: "text-purple-400" },
                { label: "机会指数", value: d?.opportunity?.score ?? "-", color: "text-yellow-400" },
                { label: "风险评估", value: d?.risk?.score ?? "-", color: "text-orange-400" },
              ].map((item, i) => (
                <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                  <div className="text-xs text-slate-500 mb-1">{item.label}</div>
                  <div className={"text-3xl font-bold " + item.color}>{item.value ?? "-"}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2"><Target className="w-4 h-4" /> 核心能力</h3>
                <div className="flex flex-wrap gap-2">
                  {caps.slice(0, 6).map((cap: any, i: number) => (
                    <span key={i} className="px-3 py-1.5 bg-slate-800 rounded-full text-xs flex items-center gap-1.5">
                      <span className={"w-1.5 h-1.5 rounded-full " + (cap.level >= 4 ? "bg-emerald-400" : cap.level >= 3 ? "bg-blue-400" : "bg-slate-500")} />
                      {cap.name} <span className="text-slate-500">L{cap.level}</span>
                    </span>
                  ))}
                  {caps.length === 0 && <span className="text-xs text-slate-500">暂无能力数据</span>}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2"><Award className="w-4 h-4" /> 信任证据</h3>
                <div className="space-y-2">
                  {evs.slice(0, 4).map((ev: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-xs p-2 bg-slate-800/50 rounded">
                      <span className={"w-1.5 h-1.5 rounded-full " + (ev.confidence_level >= 0.8 ? "bg-emerald-400" : "bg-yellow-400")} />
                      <span className="truncate">{ev.claim}</span>
                      <span className="text-slate-500 ml-auto">{Math.round((ev.confidence_level||0)*100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {d?.recommendations?.length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2"><Activity className="w-4 h-4" /> 战略建议</h3>
                <div className="space-y-2">
                  {d.recommendations.slice(0, 5).map((rec: any, i: number) => (
                    <div key={i} className="flex items-start gap-3 p-2 bg-slate-800/30 rounded text-sm">
                      <span className={"mt-0.5 px-1.5 py-0.5 rounded text-xs " + (rec.priority === "high" ? "bg-red-900/50 text-red-400" : "bg-yellow-900/50 text-yellow-400")}>
                        {rec.priority === "high" ? "高优" : "中优"}
                      </span>
                      <div>
                        <div className="font-medium">{rec.title}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{rec.reason}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* SCORE TAB */}
        {tab === "score" && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">GEO 评分详情</h2>
              <p className="text-xs text-slate-500 mb-4">权重来源: {d?.weights_source || "config/scoring/assessment.yaml"}</p>
              {[
                { key: "visibility", label: "AI 可见度", data: d?.visibility },
                { key: "trust", label: "可信度", data: d?.trust },
                { key: "capability", label: "能力成熟度", data: d?.capability },
                { key: "growth", label: "增长力", data: d?.growth },
                { key: "opportunity", label: "机会指数", data: d?.opportunity },
                { key: "risk", label: "风险评估", data: d?.risk },
              ].map((item, i) => (
                <div key={i} className="mb-4 last:mb-0">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">{item.label}</span>
                    <span className="text-emerald-400 font-mono">{item.data?.score ?? "-"}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded h-2">
                    <div className="bg-emerald-400 rounded h-2 transition-all" style={{ width: Math.min(100, ((item.data?.score ?? 0) / 100) * 100) + "%" }} />
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{item.data?.level}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CAPABILITY TAB */}
        {tab === "capability" && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">能力画像 ({caps.length}项)</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {caps.map((cap: any, i: number) => (
                  <div key={i} className="bg-slate-800/50 rounded-lg p-4 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium">{cap.name}</div>
                      <div className="text-xs text-slate-500">{cap.category}</div>
                    </div>
                    <div className="flex items-center gap-1">
                      {[1,2,3,4,5].map(l => (
                        <div key={l} className={"w-2.5 h-2.5 rounded-full " + (l <= (cap.level||0) ? "bg-emerald-400" : "bg-slate-700")} />
                      ))}
                      <span className="text-xs text-slate-400 ml-1">L{cap.level}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* EVIDENCE TAB */}
        {tab === "evidence" && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">信任证据 ({evs.length}条)</h2>
              <div className="space-y-3">
                {evs.map((ev: any, i: number) => (
                  <div key={i} className="bg-slate-800/30 rounded-lg p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="text-sm font-medium">{ev.claim}</div>
                        <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                          <span className="px-2 py-0.5 bg-slate-700 rounded text-xs">{ev.source_type}</span>
                          {ev.source_url && (
                            <a href={ev.source_url} target="_blank" className="text-blue-400 hover:underline flex items-center gap-1">
                              来源 <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-xs">
                        <div className={"font-bold " + (ev.confidence_level >= 0.8 ? "text-emerald-400" : "text-yellow-400")}>
                          {Math.round((ev.confidence_level||0)*100)}%
                        </div>
                        <div className="text-slate-500">置信度</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* NETWORK TAB */}
        {tab === "network" && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">产业关系网络 ({rels.length}条)</h2>
              <div className="space-y-3">
                {rels.map((r: any, i: number) => (
                  <div key={i} className="bg-slate-800/30 rounded-lg p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={"px-2 py-1 rounded text-xs " + (r.relation_type === "partners_with" ? "bg-blue-900/50 text-blue-400" : r.relation_type === "competitor_of" ? "bg-red-900/50 text-red-400" : "bg-slate-700 text-slate-300")}>
                        {r.relation_type}
                      </span>
                      <div>
                        <div className="text-sm font-medium">{r.target_name || "未知实体"}</div>
                        <div className="text-xs text-slate-500">{r.target_type}</div>
                      </div>
                    </div>
                    <div className="text-right text-xs text-slate-400">
                      权重: {r.weight}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* EVENTS TAB */}
        {tab === "events" && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">事件轨迹 ({events.length}条)</h2>
              <div className="relative pl-6 border-l-2 border-slate-800 space-y-4">
                {events.map((e: any, i: number) => (
                  <div key={i} className="relative">
                    <div className="absolute -left-[25px] w-3 h-3 rounded-full bg-emerald-400 border-2 border-slate-950" />
                    <div className="bg-slate-800/30 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 bg-slate-700 rounded text-xs">{e.event_type}</span>
                        <span className="text-sm font-medium">{e.title}</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span>{e.event_date?.toString().slice(0, 10)}</span>
                        {e.impact && <span className="text-slate-400">影响: {e.impact}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STRATEGY TAB */}
        {tab === "strategy" && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-400" /> AI 战略评估报告</h2>
              {agent?.data?.report ? (
                <div className="space-y-4">
                  {/* GEO Identity */}
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-slate-300 mb-2">GEO 数字身份</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <span className="text-slate-500">GEO ID:</span><span>{agent.data.report.geo_identity?.geo_id}</span>
                      <span className="text-slate-500">实体类型:</span><span>{agent.data.report.geo_identity?.entity_type}</span>
                      <span className="text-slate-500">认证状态:</span><span>{agent.data.report.geo_identity?.is_verified ? "已认证" : "未认证"}</span>
                    </div>
                  </div>

                  {/* Visibility */}
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-slate-300 mb-2">AI 可见度</h3>
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-blue-400">{agent.data.report.visibility?.score}</span>
                      <span className="text-sm text-slate-400">{agent.data.report.visibility?.interpretation}</span>
                    </div>
                  </div>

                  {/* Trust */}
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-slate-300 mb-2">可信度评估</h3>
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-emerald-400">{agent.data.report.trust?.score}</span>
                      <span className="text-sm text-slate-400">{agent.data.report.trust?.interpretation}</span>
                    </div>
                  </div>

                  {/* Competitive */}
                  {agent.data.report.competitive_position && (
                    <div className="bg-slate-800/30 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-slate-300 mb-2">竞争定位</h3>
                      <div className="flex items-center gap-4">
                        <span className="text-2xl font-bold text-purple-400">{agent.data.report.competitive_position.score}</span>
                        <div className="text-sm text-slate-400">
                          <div>{agent.data.report.competitive_position.reasons}</div>
                          <div className="text-xs text-slate-500 mt-1">{agent.data.report.competitive_position.actions}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Roadmap */}
                  {agent.data.report.roadmap && (
                    <div className="bg-slate-800/30 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-slate-300 mb-2">发展路线图</h3>
                      <pre className="text-xs text-slate-400 whitespace-pre-wrap">{agent.data.report.roadmap.actions}</pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Activity className="w-8 h-8 mx-auto mb-2 animate-pulse" />
                  <p className="text-sm">Agent 战略报告生成中...</p>
                </div>
              )}
            </div>
          </div>
        )}
      {/* GEO Universe Evolution Timeline */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <EvolutionTimeline entityId={id as string} />
      </div>

      </main>
    </div>
  );
}
