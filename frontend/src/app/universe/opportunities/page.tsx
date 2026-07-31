"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  Lightbulb, Loader2, TrendingUp, Compass, Target, Zap,
  ArrowRight, Sparkles, BarChart3, Globe, Star,
  ArrowUpRight, Building2, Factory
} from "lucide-react";

const OPPORTUNITY_CATEGORIES = [
  { key: "capability", label: "能力提升", desc: "基于当前GEO分数缺口推荐", icon: Target, color: "blue" },
  { key: "certification", label: "认证获取", desc: "提升Trust Score的关键路径", icon: Star, color: "amber" },
  { key: "relationship", label: "生态合作", desc: "发现高价值合作伙伴", icon: Globe, color: "green" },
  { key: "market", label: "市场机会", desc: "新出现的需求与趋势", icon: TrendingUp, color: "purple" },
];

export default function OpportunitiesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

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
    setAnalysisLoading(true);
    const rawId = (selectedCompany.id || "").replace(/^comp_/, "");
    api.decision.company(rawId)
      .then((data: any) => setAnalysis(data))
      .catch(() => setAnalysis(null))
      .finally(() => setAnalysisLoading(false));
  }, [selectedCompany]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[70vh] bg-slate-950">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">去哪里？</h1>
          <p className="text-slate-400 text-sm">基于当前位置和成长轨迹，发现未来的可能方向。</p>
        </div>

        <div className="flex gap-2 mb-8 flex-wrap">
          {companies.map((c: any) => (
            <button key={c.id} onClick={() => setSelectedCompany(c)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedCompany?.id === c.id
                  ? "bg-purple-600 text-white shadow-lg shadow-purple-500/20"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}>
              {c.name}
            </button>
          ))}
        </div>

        {selectedCompany && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current State */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Building2 className="w-5 h-5 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-400 uppercase">当前位置</h3>
              </div>
              <div className="space-y-3">
                <StateRow label="GEO Score" value={selectedCompany.geo_score || 0} max={100} />
                <StateRow label="Visibility" value={selectedCompany.visibility_score || 0} max={100} />
                <StateRow label="Trust" value={selectedCompany.trust_score || 0} max={100} />
                <StateRow label="Capability" value={selectedCompany.capability_score || 0} max={100} />
              </div>
            </div>

            {/* AI Analysis */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="text-sm font-semibold text-slate-400 uppercase">AI 洞察</h3>
              </div>
              {analysisLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-purple-500 animate-spin" />
                  <span className="text-xs text-slate-400">正在分析...</span>
                </div>
              ) : analysis ? (
                <div className="space-y-3">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {analysis.summary || analysis.recommendation || "基于当前数据分析，该节点处于成长阶段，建议重点关注能力建设和生态连接。"}
                  </p>
                  {analysis.gaps && analysis.gaps.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {analysis.gaps.slice(0, 3).map((g: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <ArrowUpRight className="w-3 h-3 text-purple-400 flex-shrink-0" />
                          <span className="text-slate-400">{g.name || g}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-xs text-slate-500">暂无AI分析数据。完成一次检测后系统将自动生成洞察。</p>
              )}
            </div>

            {/* Opportunity Categories */}
            <div className="lg:col-span-2">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">机会方向</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {OPPORTUNITY_CATEGORIES.map((cat) => {
                  const Icon = cat.icon;
                  return (
                    <div key={cat.key} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-lg bg-${cat.color}-500/10 flex items-center justify-center`}>
                            <Icon className={`w-5 h-5 text-${cat.color}-400`} />
                          </div>
                          <div>
                            <h4 className="text-sm font-medium">{cat.label}</h4>
                            <p className="text-[11px] text-slate-500 mt-0.5">{cat.desc}</p>
                          </div>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600" />
                      </div>
                      <div className="mt-4 pt-4 border-t border-slate-800">
                        {cat.key === "capability" && (
                          <p className="text-[10px] text-slate-500">
                            建议: 增加结构化数据标记 (Schema.org)、实体页建设、权威外链引用
                          </p>
                        )}
                        {cat.key === "certification" && (
                          <p className="text-[10px] text-slate-500">
                            建议: 申请行业认证、积累合规证据、建立公开信任档案
                          </p>
                        )}
                        {cat.key === "relationship" && (
                          <p className="text-[10px] text-slate-500">
                            建议: 与至少2家服务商建立合作、参与行业生态活动
                          </p>
                        )}
                        {cat.key === "market" && (
                          <p className="text-[10px] text-slate-500">
                            趋势: AI搜索优化需求上升、企业AI知识库需求增长
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StateRow({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.min(Math.round((value / max) * 100), 100);
  const barColor = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-200 font-medium">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-slate-800 rounded-full">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: pct + "%" }} />
      </div>
    </div>
  );
}
