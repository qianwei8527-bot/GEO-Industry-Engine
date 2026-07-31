"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Users, Shield, Star, Award, ArrowRight, Search, Loader2, BarChart3, Eye, ChevronRight } from "lucide-react";

export default function MarketplacePage() {
  const [providers, setProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    (async () => {
      try { const data = await api.marketplace.listProviders(); setProviders(data.providers || []); }
      catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">GEO Marketplace</h1>
        <p className="text-slate-500 mt-1">Discover service providers matched to your GEO needs. You choose — we provide the evidence.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {providers.map((p: any) => (
          <div key={p.provider_id} onClick={() => setSelected(p)}
            className={`bg-white border rounded-xl p-4 cursor-pointer transition-all hover:shadow-md ${selected?.provider_id === p.provider_id ? "border-blue-400 ring-2 ring-blue-100" : "border-slate-200"}`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">{p.name}</h3>
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    {p.is_verified && <Shield className="w-3 h-3 text-green-500" />}
                    {p.is_verified ? "Verified" : "Unverified"}
                  </div>
                </div>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-bold ${(p.geo_score || 0) >= 70 ? "bg-green-50 text-green-700" : (p.geo_score || 0) >= 40 ? "bg-amber-50 text-amber-700" : "bg-red-50 text-red-700"}`}>{p.geo_score || 0}</div>
            </div>
            <div className="flex flex-wrap gap-1.5 mb-3">
              {(p.capabilities || []).slice(0, 4).map((c: any, i: number) => (
                <span key={i} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">{c.name}</span>
              ))}
              {(p.capability_count || 0) > 4 && <span className="px-2 py-0.5 text-slate-400 text-[10px]">+{p.capability_count - 4} more</span>}
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1"><Star className="w-3 h-3" /> Trust: {p.trust_score}</span>
              <span className="flex items-center gap-1"><Award className="w-3 h-3" /> {p.reputation?.level || "N/A"}</span>
              <span className="flex items-center gap-1"><BarChart3 className="w-3 h-3" /> {p.evidence_count || 0} ev</span>
            </div>
          </div>
        ))}
      </div>

      {/* Detail panel */}
      {selected && (
        <div className="mt-6 bg-white border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">{selected.name}</h2>
            <a href={`/marketplace/provider/${selected.provider_id}`} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium">
              Full Profile <ChevronRight className="w-4 h-4" />
            </a>
          </div>
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{selected.trust_score || 0}</div>
              <div className="text-xs text-slate-500">Trust Score</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{selected.geo_score || 0}</div>
              <div className="text-xs text-slate-500">GEO Score</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-purple-600">{selected.reputation?.level || "N/A"}</div>
              <div className="text-xs text-slate-500">Reputation</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-amber-600">{selected.evidence_count || 0}</div>
              <div className="text-xs text-slate-500">Evidence Records</div>
            </div>
          </div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Capabilities</h3>
          <div className="flex flex-wrap gap-2">
            {(selected.capabilities || []).map((c: any, i: number) => (
              <span key={i} className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium border border-blue-100">{c.name}</span>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-4">Note: These are candidate providers. You make your own choice based on the evidence provided.</p>
        </div>
      )}
    </div>
  );
}