"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { ReactNode } from "react";
import {
  Building2, Users, Bot, Landmark, Target, Shield, Crosshair,
  Clock, TrendingUp, Link2, Sparkles, AlertCircle, CheckCircle2,
  Radio, ArrowLeft, Loader2, Compass, Network, GitBranch,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

const TYPE_META: Record<string, { label: string; icon: ReactNode }> = {
  company: { label: "企业", icon: <Building2 className="w-4 h-4" /> },
  provider: { label: "服务商", icon: <Users className="w-4 h-4" /> },
  ai_agent: { label: "AI Agent", icon: <Bot className="w-4 h-4" /> },
  government: { label: "政府", icon: <Landmark className="w-4 h-4" /> },
};

function nodeIcon(type: string) {
  return TYPE_META[type]?.icon || <Target className="w-4 h-4" />;
}

function stageLabel(stage: string) {
  const map: Record<string, string> = {
    position: "定位", selfknow: "自知", action: "行动",
    provision: "使用", accumulate: "沉淀", reputation: "信誉",
  };
  return map[stage] || stage || "未知";
}

export default function NodeUniverseHome() {
  const params = useParams();
  const nodeId = String(params?.node || "");
  const [nodeType, setNodeType] = useState("company");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!nodeId) return;
    setLoading(true);
    setError("");
    fetch(`${API_BASE}/universe/node/${nodeType}/${encodeURIComponent(nodeId)}/home`)
      .then(async (r) => {
        if (!r.ok) throw new Error("无法加载节点");
        return r.json();
      })
      .then(setData)
      .catch((e: any) => setError(e.message || "加载失败"))
      .finally(() => setLoading(false));
  }, [nodeId, nodeType]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <Loader2 className="w-7 h-7 text-blue-400 animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="max-w-md w-full mx-6 border border-slate-800 rounded-xl p-8 text-center">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-3" />
          <p className="text-sm text-slate-300">{error || "节点不存在"}</p>
        </div>
      </div>
    );
  }

  const identity = data.identity || {};
  const pos = data.position?.current?.position || {};
  const interpretation = data.position?.current?.interpretation || {};
  const rep = data.position?.reputation || {};
  const caps = data.position?.capabilities?.acquired || [];
  const risks = data.position?.risks?.risks || [];
  const causality = data.story?.causality?.chain || [];
  const milestones = data.story?.milestones || [];
  const significantEvents = data.story?.timeline?.significant_events || [];
  const relations = data.ecosystem?.relations?.edges || [];
  const futureStates = Object.values(data.future?.possibility?.states || {});
  const needs = data.future?.connection_needs || [];
  const candidates = data.opportunities?.connection_candidates || [];
  const direction = data.future?.direction?.summary || "";
  const reputationLevel = pos.reputation_level || rep.level || "N/A";
  const rank = pos.industry_rank != null ? `Top ${Math.round(pos.industry_rank * 100)}%` : "";
  const strengths = interpretation.strengths || [];
  const gaps = interpretation.gaps || [];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <a href="/universe/home" className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-white mb-8 transition">
          <ArrowLeft className="w-3.5 h-3.5" /> Universe
        </a>

        <div className="flex items-start justify-between flex-wrap gap-4 pb-8 border-b border-slate-800">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-blue-500/20 flex items-center justify-center">
              {nodeIcon(nodeType)}
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">{identity.name || nodeId}</h1>
              <p className="text-sm text-slate-500 mt-1">
                {TYPE_META[nodeType]?.label || nodeType} · {identity.type_label || ""}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {Object.entries(TYPE_META).map(([key, meta]) => (
              <button
                key={key}
                onClick={() => setNodeType(key)}
                className={`px-3 py-1.5 rounded-md text-xs border transition ${
                  nodeType === key
                    ? "bg-blue-600 border-blue-500 text-white"
                    : "border-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                {meta.label}
              </button>
            ))}
          </div>
        </div>

        <Section icon={<Compass className="w-4 h-4 text-blue-400" />} title="我的位置">
          <div className="grid md:grid-cols-3 gap-4">
            <Stat label="行业" value={data.position?.industry?.industry_name || "未知"} />
            <Stat label="阶段" value={stageLabel(pos.growth_stage)} />
            <Stat label="信誉" value={`${rep.status || "UNKNOWN"} (${reputationLevel})`} />
            {rank && <Stat label="行业位置" value={rank} />}
            <Stat label="影响" value={String(pos.influence_score ?? 0)} />
            <Stat label="趋势" value={pos.trend || rep.trend || "stable"} />
          </div>
          {interpretation.narrative && (
            <p className="mt-4 text-sm text-slate-400 leading-relaxed max-w-3xl">{interpretation.narrative}</p>
          )}
          {(strengths.length > 0 || gaps.length > 0) && (
            <div className="mt-4 flex flex-wrap gap-2">
              {strengths.slice(0, 3).map((s: string, i: number) => (
                <span key={i} className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  {s}
                </span>
              ))}
              {gaps.slice(0, 3).map((g: string, i: number) => (
                <span key={i} className="text-xs px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/20">
                  {g}
                </span>
              ))}
            </div>
          )}
          {caps.length > 0 && (
            <div className="mt-5">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3">能力</h4>
              <div className="flex flex-wrap gap-2">
                {caps.slice(0, 12).map((c: any, i: number) => (
                  <span key={i} className="text-xs px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {c.label || c.cap_id || c}
                  </span>
                ))}
              </div>
            </div>
          )}
          {risks.length > 0 && (
            <div className="mt-5">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3">风险</h4>
              <div className="space-y-2">
                {risks.slice(0, 3).map((r: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
                    <span>{r.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>

        <Section icon={<Clock className="w-4 h-4 text-emerald-400" />} title="我的故事">
          {causality.length > 0 ? (
            <div className="space-y-0">
              {causality.map((step: any, i: number) => (
                <div key={i} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 mt-2" />
                    {i < causality.length - 1 && <div className="w-px flex-1 bg-slate-800" />}
                  </div>
                  <div className="pb-6">
                    <p className="text-sm text-slate-200">{step.label || step.event_type}</p>
                    <p className="text-xs text-slate-500 mt-1">{step.description || ""} · {step.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">暂无足够事件，无法投影因果链。</p>
          )}
          {milestones.length > 0 && (
            <div className="mt-6">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3">关键节点</h4>
              <div className="grid md:grid-cols-3 gap-3">
                {milestones.slice(0, 6).map((m: any, i: number) => (
                  <div key={i} className="rounded-lg bg-slate-900 border border-slate-800 p-4">
                    <p className="text-xs text-slate-500">{m.date}</p>
                    <p className="text-sm text-slate-200 mt-1 line-clamp-2">{m.event}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {significantEvents.length > 0 && (
            <div className="mt-6">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3">重要事件</h4>
              <div className="space-y-2">
                {significantEvents.slice(0, 4).map((e: any, i: number) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    {e.title} <span className="text-xs text-slate-600">{e.date}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>

        <Section icon={<Network className="w-4 h-4 text-purple-400" />} title="我的生态">
          {relations.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-3">
              {relations.map((r: any, i: number) => (
                <div key={i} className="rounded-lg bg-slate-900 border border-slate-800 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm text-slate-200 truncate">{r.target}</span>
                    <span className="text-xs px-2 py-1 rounded bg-purple-500/10 text-purple-300">{r.relation_type}</span>
                  </div>
                  <div className="flex items-center justify-between mt-2 text-xs text-slate-500">
                    <span>{r.stage}</span>
                    <span>强度 {Math.round((r.strength || 0) * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">暂无已投影的关系。</p>
          )}
        </Section>

        <Section icon={<GitBranch className="w-4 h-4 text-amber-400" />} title="未来路径">
          {direction && (
            <p className="text-sm text-slate-300 mb-5 max-w-3xl leading-relaxed">{direction}</p>
          )}
          {futureStates.length > 0 ? (
            <div className="grid md:grid-cols-3 gap-3">
              {futureStates.slice(0, 6).map((s: any, i: number) => (
                <div key={i} className="rounded-lg bg-slate-900 border border-slate-800 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-500 uppercase">T+{s.horizon_days}</span>
                    <TrendingUp className="w-4 h-4 text-amber-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-200">{s.stage || s.horizon}</p>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{s.description}</p>
                  <p className="text-xs text-slate-600 mt-2">概率 {(s.probability || 0) * 100}%</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">暂无未来推演。</p>
          )}
          {needs.length > 0 && (
            <div className="mt-6">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3">需要的连接</h4>
              <div className="flex flex-wrap gap-2">
                {needs.slice(0, 8).map((n: any, i: number) => (
                  <span key={i} className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20">
                    {n.type || n.needed_capability || n.needed_node_type}
                  </span>
                ))}
              </div>
            </div>
          )}
        </Section>

        <Section icon={<Sparkles className="w-4 h-4 text-sky-400" />} title="下一步机会">
          {candidates.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-3">
              {candidates.slice(0, 6).map((c: any, i: number) => (
                <div key={i} className="rounded-lg bg-slate-900 border border-slate-800 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-medium text-slate-200 truncate">{c.name || c.node_id}</span>
                    <span className="text-sm font-semibold text-sky-300">{Math.round((c.future_alignment_score || 0) * 100)}%</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2 line-clamp-2">{c.recommendation || c.connects_to_future || c.label || ""}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">暂无下一步连接建议。</p>
          )}
        </Section>

        <div className="pt-6 flex items-center gap-2 text-xs text-slate-600">
          <Radio className="w-3.5 h-3.5" /> Universe Home · {nodeId}
        </div>
      </div>
    </div>
  );
}

function Section({ icon, title, children }: { icon: ReactNode; title: string; children: ReactNode }) {
  return (
    <section className="py-8 border-b border-slate-800">
      <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-slate-400 mb-5">
        {icon} {title}
      </h2>
      {children}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-900 border border-slate-800 p-4">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="text-sm font-medium text-slate-100 mt-1">{value}</p>
    </div>
  );
}
