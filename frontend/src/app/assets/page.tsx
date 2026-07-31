"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { BarChart3, Building2, TrendingUp, Award, Shield, Globe, Loader2, Factory } from "lucide-react";

export default function AssetsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const ov = await api.graph.overview();
        setData(ov);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  const stats = data?.universe_stats || {};
  const layers = data?.layers || {};
  const industries = data?.industries || [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">GEO Data Assets</h1>
        <p className="text-slate-500 mt-1">The cumulative intelligence powering the GEO Universe.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Building2 className="w-5 h-5 text-blue-500 mb-2" />
          <div className="text-2xl font-bold text-gray-900">{stats.companies || 0}</div>
          <div className="text-xs text-slate-500">Companies</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Award className="w-5 h-5 text-green-500 mb-2" />
          <div className="text-2xl font-bold text-gray-900">{stats.providers || 0}</div>
          <div className="text-xs text-slate-500">Providers</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Shield className="w-5 h-5 text-purple-500 mb-2" />
          <div className="text-2xl font-bold text-gray-900">{stats.evidence_records || 0}</div>
          <div className="text-xs text-slate-500">Evidence Records</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Globe className="w-5 h-5 text-amber-500 mb-2" />
          <div className="text-2xl font-bold text-gray-900">{stats.relationships || 0}</div>
          <div className="text-xs text-slate-500">Relationships</div>
        </div>
      </div>

      {/* Layer Status */}
      <div className="mb-8">
        <h2 className="text-lg font-bold text-gray-900 mb-3">Universe Layer Status</h2>
        <div className="grid grid-cols-3 gap-3">
          {["rules", "node", "graph", "dynamic", "evolution", "intelligence"].map((k) => (
            <div key={k} className={`rounded-lg p-4 border ${layers[k] === "active" ? "bg-green-50 border-green-200" : "bg-slate-50 border-slate-200"}`}>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${layers[k] === "active" ? "bg-green-500" : "bg-slate-300"}`} />
                <span className="text-sm font-semibold capitalize">{k}</span>
                <span className={`text-xs ml-auto ${layers[k] === "active" ? "text-green-600" : "text-slate-400"}`}>{layers[k] || "unknown"}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Industries */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-3">Industry Distribution</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {industries.map((ind: any) => (
            <div key={ind.id} className="bg-white border border-slate-200 rounded-lg p-3 flex items-center gap-3">
              <Factory className="w-6 h-6 text-slate-400" />
              <div>
                <div className="text-sm font-semibold text-gray-900">{ind.name}</div>
                <div className="text-xs text-slate-500">{ind.company_count} companies · Code: {ind.code}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* GEO Universe Data Stats */}
      <div className="mt-8">
        <h2 className="text-lg font-bold text-gray-900 mb-3">Additional Intelligence</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
          {[
            { label: "Geo Events", val: stats.geo_events || 0, icon: TrendingUp },
            { label: "Growth Stages", val: stats.growth_stages_populated || 0, icon: BarChart3 },
            { label: "Reputations", val: stats.reputations_scored || 0, icon: Award },
            { label: "Industries", val: stats.industries || 0, icon: Factory },
            { label: "Total Relations", val: stats.relationships || 0, icon: Globe },
          ].map((item) => (
            <div key={item.label} className="bg-slate-50 rounded-lg p-3">
              <item.icon className="w-4 h-4 text-slate-400 mx-auto mb-1" />
              <div className="text-lg font-bold text-gray-900">{item.val}</div>
              <div className="text-[10px] text-slate-500">{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}