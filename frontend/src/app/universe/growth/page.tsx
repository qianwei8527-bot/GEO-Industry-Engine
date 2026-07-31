"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  TrendingUp, Loader2, Award, Clock, Target, Zap, Shield,
  Crosshair, Eye, Compass, ChevronRight, Star, BarChart3,
  ArrowUpRight, CheckCircle2, Circle, Timer
} from "lucide-react";

const LIFECYCLE_STEPS = [
  { key: "position", label: "定位", icon: Crosshair, desc: "我在哪里？处于什么阶段？" },
  { key: "selfknow", label: "自知", icon: Eye, desc: "缺什么能力？缺什么关系？" },
  { key: "action", label: "行动", icon: Zap, desc: "下一步该做什么？" },
  { key: "provision", label: "使用", icon: Compass, desc: "Universe提供的路径与资源" },
  { key: "accumulate", label: "沉淀", icon: Clock, desc: "每一次行动留下记录" },
  { key: "reputation", label: "信誉", icon: Shield, desc: "可追溯的资产" },
];

export default function GrowthPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<any>(null);
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [snapLoading, setSnapLoading] = useState(false);

  useEffect(() => {
    api.companies.list("").then((data: any) => {
      const list = Array.isArray(data) ? data : (data.companies || data.items || []);
      setCompanies(list.slice(0, 8));
      if (list.length > 0) setSelectedCompany(list[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCompany) return;
    setSnapLoading(true);
    const rawId = (selectedCompany.id || "").replace(/^comp_/, "");
    api.identity.snapshots(rawId)
      .then((data: any) => setSnapshots(Array.isArray(data) ? data : (data.snapshots || [])))
      .catch(() => setSnapshots([]))
      .finally(() => setSnapLoading(false));
  }, [selectedCompany]);

  // Determine lifecycle stage
  const geoScore = selectedCompany?.geo_score || 0;
  const evidenceCount = selectedCompany?.evidence_count || 0;
  const relationshipCount = selectedCompany?.relationship_count || 0;
  const stageIndex = (() => {
    if (!geoScore && !evidenceCount) return 0;
    if (geoScore > 0 && evidenceCount === 0) return 1;
    if (evidenceCount > 0 && relationshipCount === 0) return 2;
    if (relationshipCount > 0 && geoScore < 50) return 3;
    if (geoScore >= 50 && geoScore < 80) return 4;
    return 5;
  })();

  if (loading) return (
    <div className="flex items-center justify-center min-h-[70vh] bg-slate-950">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">如何变化？</h1>
          <p className="text-slate-400 text-sm">追踪成长轨迹，理解进化路径，发现下一阶段目标。</p>
        </div>

        {/* Company selector */}
        <div className="flex gap-2 mb-8 flex-wrap">
          {companies.map((c: any) => (
            <button key={c.id} onClick={() => setSelectedCompany(c)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedCompany?.id === c.id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}>
              {c.name}
            </button>
          ))}
        </div>

        {selectedCompany && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Lifecycle Stage */}
            <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-sm font-semibold text-slate-400 uppercase mb-5">成长生命周期</h2>
              <div className="flex items-center gap-1">
                {LIFECYCLE_STEPS.map((step, i) => {
                  const Icon = step.icon;
                  const done = i < stageIndex;
                  const current = i === stageIndex;
                  return (
                    <div key={step.key} className="flex-1 flex flex-col items-center relative">
                      {i > 0 && (
                        <div className={`absolute top-5 right-1/2 w-full h-0.5 -translate-y-1/2 ${
                          done ? "bg-blue-500" : "bg-slate-700"
                        }`} />
                      )}
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center relative z-10 ${
                        done ? "bg-blue-600 text-white" :
                        current ? "bg-blue-500/20 text-blue-400 border-2 border-blue-500" :
                        "bg-slate-800 text-slate-600"
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className={`text-[10px] mt-1.5 font-medium ${
                        done ? "text-blue-400" : current ? "text-blue-300" : "text-slate-600"
                      }`}>{step.label}</span>
                      <span className="text-[9px] text-slate-600 mt-0.5 text-center leading-tight">{step.desc}</span>
                    </div>
                  );
                })}
              </div>
              <div className="mt-5 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <p className="text-xs text-blue-300">
                  当前阶段: <span className="font-bold">{LIFECYCLE_STEPS[stageIndex].label}</span> — {LIFECYCLE_STEPS[stageIndex].desc}
                </p>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">关键指标</h3>
              <div className="space-y-4">
                <MetricRow label="GEO Score" value={geoScore} max={100} color="blue" />
                <MetricRow label="证据数" value={evidenceCount} max={20} color="green" />
                <MetricRow label="关系数" value={relationshipCount} max={15} color="purple" />
                <MetricRow label="认证数" value={selectedCompany.certification_count || 0} max={10} color="amber" />
              </div>
            </div>

            {/* Evolution Timeline */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">进化时间线</h3>
              {snapLoading ? (
                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              ) : snapshots.length > 0 ? (
                <div className="space-y-3">
                  {snapshots.slice(0, 5).map((s: any, i: number) => (
                    <div key={i} className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                      <div>
                        <p className="text-xs text-slate-300">{s.snapshot_date || s.created_at || "Snapshot"}</p>
                        <p className="text-[10px] text-slate-500">Score: {s.geo_score ?? "N/A"}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">暂无进化数据。节点需要更多时间积累变化记录。</p>
              )}
            </div>

            {/* Growth Gap Analysis */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">成长分析</h3>
              <div className="space-y-3">
                {stageIndex < 5 && (
                  <div className="flex items-center gap-2 text-xs">
                    <ArrowUpRight className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-slate-300">下一阶段: <span className="font-bold text-amber-400">{LIFECYCLE_STEPS[Math.min(stageIndex + 1, 5)].label}</span></span>
                  </div>
                )}
                {evidenceCount < 3 && (
                  <div className="flex items-center gap-2 text-xs">
                    <Target className="w-3.5 h-3.5 text-red-400" />
                    <span className="text-slate-400">需要更多证据 (当前 {evidenceCount}/3)</span>
                  </div>
                )}
                {relationshipCount < 2 && (
                  <div className="flex items-center gap-2 text-xs">
                    <Target className="w-3.5 h-3.5 text-red-400" />
                    <span className="text-slate-400">需要建立关系 (当前 {relationshipCount}/2)</span>
                  </div>
                )}
                {geoScore < 30 && (
                  <div className="flex items-center gap-2 text-xs">
                    <BarChart3 className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-slate-400">GEO评分偏低，建议增加结构化数据和权威引用</span>
                  </div>
                )}
              </div>
              <div className="mt-4 p-3 bg-slate-800 rounded-lg">
                <p className="text-[10px] text-slate-500">
                  提示: 每次评分检测都会生成一份新快照。持续积累快照，系统将自动分析成长轨迹和阶段跃迁。
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricRow({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min(Math.round((value / max) * 100), 100);
  const colorMap: Record<string, string> = {
    blue: "bg-blue-500", green: "bg-green-500", purple: "bg-purple-500", amber: "bg-amber-500",
  };
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-200 font-medium">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-slate-800 rounded-full">
        <div className={`h-full rounded-full ${colorMap[color] || "bg-blue-500"}`} style={{ width: pct + "%" }} />
      </div>
    </div>
  );
}
