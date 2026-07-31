"use client";

import { useState } from "react";
import {
  Link2, Loader2, Search, ChevronRight, Target, Zap,
  ArrowRight, Shield, Network, History, Lightbulb, Sparkles,
  TrendingUp, Users, Building2, Bot, Landmark, Star,
  AlertCircle, CheckCircle2, Clock, Filter
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/universe";

const edgeConfig: Record<string, { color: string; bg: string; label: string }> = {
  strong: { color: "text-emerald-400", bg: "bg-emerald-500/10", label: "Strong" },
  moderate: { color: "text-amber-400", bg: "bg-amber-500/10", label: "Moderate" },
  weak: { color: "text-slate-400", bg: "bg-slate-500/10", label: "Weak" },
};

function getEdgeBadge(strength: string) {
  const cfg = edgeConfig[strength] || edgeConfig.weak;
  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded ${cfg.bg} ${cfg.color}`}>
      {strength === "strong" ? <Zap className="w-3 h-3" /> : strength === "moderate" ? <TrendingUp className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
      {cfg.label}
    </span>
  );
}

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
  switch (type) {
    case "company": return "Company";
    case "provider": return "Provider";
    case "ai_agent": return "AI Agent";
    case "government": return "Government";
    default: return type;
  }
}

export default function FutureConnectionsPage() {
  const [nodeId, setNodeId] = useState("");
  const [nodeType, setNodeType] = useState("company");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<any>(null);

  const handleDiscover = async () => {
    if (!nodeId.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/connections/${nodeType}/${nodeId}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Discovery failed");
      }
      const data = await res.json();
      setReport(data);
    } catch (e: any) {
      setError(e.message || "Connection error");
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <Link2 className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Future Connections</h1>
              <p className="text-slate-400 text-sm">Phase C4: Connection based on shared future paths</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 mb-8">
          <div className="flex gap-4 items-end flex-wrap">
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Node Type</label>
              <div className="flex gap-2">
                {["company", "provider"].map((t) => (
                  <button
                    key={t}
                    onClick={() => setNodeType(t)}
                    className={`px-4 py-2 rounded-lg text-sm transition ${nodeType === t ? "bg-purple-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"}`}
                  >
                    {getNodeTypeLabel(t)}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs text-slate-500 mb-1 block">Node ID</label>
              <input
                type="text"
                value={nodeId}
                onChange={(e) => setNodeId(e.target.value)}
                placeholder="e.g. comp-001 or prov-001"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-purple-500"
                onKeyDown={(e) => e.key === "Enter" && handleDiscover()}
              />
            </div>
            <button
              onClick={handleDiscover}
              disabled={loading || !nodeId.trim()}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Discover
            </button>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </div>

        {report && (
          <div className="space-y-6">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-purple-400" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold mb-1">{report.node_id}</h2>
                  <p className="text-slate-400 text-sm">{report.current_state || "N/A"}</p>
                  <p className="text-slate-300 text-sm mt-2">{report.summary}</p>
                  {report.target_futures && report.target_futures.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {report.target_futures.map((f: string, i: number) => (
                        <span key={i} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                          <Target className="w-3 h-3" />{f}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-2xl font-bold text-purple-400">{report.candidate_count}</div>
                  <div className="text-xs text-slate-500">Candidates</div>
                </div>
              </div>
            </div>

            {report.needs && report.needs.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Connection Needs</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {report.needs.map((need: any, i: number) => (
                    <div key={i} className="bg-slate-900/80 border border-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs px-2 py-0.5 rounded bg-red-500/10 text-red-400">{need.urgency?.toUpperCase()}</span>
                        <span className="text-xs text-slate-500">{getNodeTypeLabel(need.needed_node_type)}</span>
                      </div>
                      <p className="text-sm text-slate-300">{need.reason}</p>
                      <p className="text-xs text-slate-500 mt-1">For: {need.future_state}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {report.candidates && report.candidates.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Connection Candidates ({report.candidates.length})</h3>
                <div className="space-y-3">
                  {report.candidates.map((candidate: any, i: number) => (
                    <div key={i} className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-purple-500/30 transition group">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center">
                            {getNodeTypeIcon(candidate.node_type)}
                          </div>
                          <div>
                            <h4 className="font-semibold text-white group-hover:text-purple-300 transition">{candidate.name}</h4>
                            <p className="text-xs text-slate-500">{candidate.label}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-purple-400">{(candidate.future_alignment_score * 100).toFixed(0)}%</div>
                          <div className="text-xs text-slate-500">Alignment</div>
                        </div>
                      </div>

                      {candidate.factors && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                          {[
                            ["Capability", candidate.factors.capability_complementarity, "emerald"],
                            ["Trust", candidate.factors.trust_compatibility, "blue"],
                            ["History", candidate.factors.historical_outcome, "amber"],
                            ["Network", candidate.factors.network_position, "rose"],
                          ].map(([label, value, color]) => {
                            const colorClass = color === "emerald" ? "bg-emerald-500/10 text-emerald-400"
                              : color === "blue" ? "bg-blue-500/10 text-blue-400"
                              : color === "amber" ? "bg-amber-500/10 text-amber-400"
                              : "bg-rose-500/10 text-rose-400";
                            return (
                              <div key={label} className={`rounded-lg p-2 ${colorClass}`}>
                                <div className="text-xs opacity-70">{label}</div>
                                <div className="text-sm font-semibold">{((value as number) * 100).toFixed(0)}%</div>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-3">
                          {getEdgeBadge(candidate.edge_strength)}
                          <span className="text-slate-500 text-xs">For: {candidate.connects_to_future}</span>
                        </div>
                        <span className="text-purple-400 text-xs">{candidate.recommendation}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-slate-900/60 border border-slate-800/50 rounded-lg p-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Future Alignment Score</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs text-slate-500">
                <div><span className="text-emerald-400 font-medium">35%</span> Capability</div>
                <div><span className="text-blue-400 font-medium">25%</span> Trust</div>
                <div><span className="text-amber-400 font-medium">15%</span> History</div>
                <div><span className="text-rose-400 font-medium">15%</span> Network</div>
                <div><span className="text-purple-400 font-medium">10%</span> Path Match</div>
              </div>
            </div>
          </div>
        )}

        {!report && !loading && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-12 text-center">
            <div className="w-16 h-16 mx-auto rounded-full bg-purple-500/10 flex items-center justify-center mb-4">
              <Link2 className="w-8 h-8 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Discover Future Connections</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Enter a node ID to discover partners that can help reach future states.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
