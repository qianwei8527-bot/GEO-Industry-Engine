"use client";
import { useState, useEffect } from "react";
import {
  Brain, TrendingUp, Shield, Target, Award, AlertTriangle,
  CheckCircle, ArrowRight, ExternalLink, RefreshCw, Search,
  Lightbulb, Users, Activity, ChevronDown, ChevronUp
} from "lucide-react";

/** Reusable component for displaying Agent intelligence results. */
export default function AgentInsight({
  companyId,
  type = "diagnose",
}: {
  companyId: string;
  type?: "diagnose" | "report" | "match";
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedCites, setExpandedCites] = useState(false);

  useEffect(() => { loadData(); }, [companyId, type]);

  async function loadData() {
    setLoading(true); setError("");
    try {
      const { api } = await import("@/lib/api");
      let result: any;
      if (type === "diagnose") result = await api.agent.diagnose(companyId);
      else if (type === "report") result = await api.agent.report(companyId);
      else result = await api.agent.match({ company_id: companyId });
      setData(result);
    } catch (e: any) {
      setError(e.message || "Failed to load agent data");
    }
    setLoading(false);
  }

  if (loading) return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center">
      <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin mx-auto mb-3" />
      <p className="text-sm text-slate-400">AI analyzing enterprise data...</p>
    </div>
  );

  if (error) return (
    <div className="bg-slate-900 border border-red-900/50 rounded-lg p-6 text-center">
      <AlertTriangle className="w-6 h-6 text-red-400 mx-auto mb-2" />
      <p className="text-sm text-red-400">{error}</p>
      <button onClick={loadData} className="mt-3 px-4 py-1.5 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-300">
        Retry
      </button>
    </div>
  );

  const report = data?.report || {};
  const matchData = data?.data || {};
  const summary = data?.summary || "";
  const citations = data?.citations || [];
  const success = data?.success !== false;

  if (!success && !report && !matchData?.matches) return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center">
      <Brain className="w-8 h-8 text-slate-600 mx-auto mb-3" />
      <p className="text-sm text-slate-500">No intelligence data available for this enterprise</p>
      <p className="text-xs text-slate-600 mt-1">Run GEO detection first to generate AI insights</p>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Summary header */}
      {summary && (
        <div className="bg-gradient-to-r from-emerald-950/30 to-slate-900 border border-emerald-900/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Brain className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-emerald-300 mb-1">AI Intelligence Summary</h3>
              <p className="text-sm text-slate-300 leading-relaxed">{summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Diagnose: core findings */}
      {report.geo_score && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <MiniScoreCard icon={TrendingUp} label="GEO Score" value={report.geo_score?.overall || 0} color="emerald" />
          <MiniScoreCard icon={Target} label="Visibility" value={report.visibility?.score || 0} color="blue" />
          <MiniScoreCard icon={Shield} label="Trust" value={report.trust?.score || 0} color="amber" />
          <MiniScoreCard icon={Award} label="Evidence" value={report.evidence_summary || report.trust?.evidence_count || 0} color="purple" />
        </div>
      )}

      {/* Diagnose: issues & opportunities */}
      {report.opportunities && report.opportunities.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-yellow-400" /> Opportunities
          </h3>
          <div className="space-y-2">
            {report.opportunities.slice(0, 5).map((o: any, i: number) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <span className="text-slate-400">{o.title || o.description || o}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.risks && report.risks.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" /> Risks
          </h3>
          <div className="space-y-2">
            {report.risks.slice(0, 5).map((r: any, i: number) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5 shrink-0" />
                <span className="text-slate-400">{r.title || r.description || r}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diagnose: recommended providers */}
      {report.candidate_providers && report.candidate_providers.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400" /> Candidate Providers
          </h3>
          <div className="grid gap-3">
            {report.candidate_providers.slice(0, 3).map((p: any, i: number) => (
              <div key={i} className="bg-slate-800/40 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-slate-200">{p.entity_name || p.id}</div>
                  <div className="text-xs text-slate-500">
                    Trust: {p.trust_score || "?"} | Type: {p.provider_type || "unknown"}
                  </div>
                  {p.capabilities && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {p.capabilities.slice(0, 3).map((c: any, j: number) => (
                        <span key={j} className="px-1.5 py-0.5 bg-slate-700/50 rounded text-xs text-slate-400">
                          {c.name || c}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <a href={"/marketplace/" + (p.id)} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                  View <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Match: provider matches */}
      {matchData?.matches && matchData.matches.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Search className="w-4 h-4 text-emerald-400" /> Business Matches
          </h3>
          <div className="grid gap-3">
            {matchData.matches.map((m: any, i: number) => (
              <div key={i} className="bg-slate-800/40 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-200">Provider {m.provider_id?.slice(0, 8)}</span>
                  <span className={"text-sm font-bold " + (m.score >= 80 ? "text-emerald-400" : m.score >= 60 ? "text-yellow-400" : "text-slate-400")}>
                    {m.score}%
                  </span>
                </div>
                {m.reasons && (
                  <div className="flex flex-wrap gap-1">
                    {m.reasons.map((r: string, j: number) => (
                      <span key={j} className="px-1.5 py-0.5 bg-emerald-900/30 rounded text-xs text-emerald-400">{r}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations */}
      {citations.length > 0 && (
        <div className="border-t border-slate-800 pt-3">
          <button
            onClick={() => setExpandedCites(!expandedCites)}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-400"
          >
            <Activity className="w-3 h-3" />
            {citations.length} citations
            {expandedCites ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {expandedCites && (
            <div className="mt-2 space-y-1">
              {citations.map((c: any, i: number) => (
                <div key={i} className="text-xs text-slate-500 bg-slate-800/30 rounded px-2 py-1">
                  <span className="text-slate-400 font-medium">{c.source}</span>
                  {c.id && <span className="mx-1">| ID: {c.id}</span>}
                  {c.field && <span className="mx-1">| Field: {c.field}</span>}
                  {c.description && <span className="mx-1">| {c.description}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MiniScoreCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: number | string; color: string }) {
  const colorMap: Record<string, string> = {
    emerald: "text-emerald-400 border-emerald-800",
    blue: "text-blue-400 border-blue-800",
    amber: "text-amber-400 border-amber-800",
    purple: "text-purple-400 border-purple-800",
  };
  return (
    <div className={"bg-slate-900 border rounded-lg p-3 text-center " + (colorMap[color] || "border-slate-800")}>
      <Icon className="w-4 h-4 text-slate-500 mx-auto mb-1" />
      <div className="text-lg font-bold text-slate-200">{typeof value === "number" ? value : value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}
