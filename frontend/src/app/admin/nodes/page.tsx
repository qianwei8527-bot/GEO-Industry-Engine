"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Database, Loader2, Search, Building2, Factory, Users, Filter } from "lucide-react";

export default function AdminNodesPage() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  useEffect(() => {
    Promise.all([
      api.companies.list("").catch(() => []),
      api.marketplace.listProviders().catch(() => []),
      api.industries.list().catch(() => []),
    ]).then(([comp, prov, ind]: [any, any, any]) => {
      const all = [
        ...(Array.isArray(comp) ? comp : (comp.companies || comp.items || [])).map((c: any) => ({ ...c, _type: "企业" })),
        ...(Array.isArray(prov) ? prov : (prov.providers || prov.items || [])).map((p: any) => ({ ...p, _type: "服务商" })),
        ...(Array.isArray(ind) ? ind : (ind.industries || ind.items || [])).map((i: any) => ({ ...i, _type: "行业" })),
      ];
      setNodes(all);
      setLoading(false);
    });
  }, []);

  const filtered = nodes.filter((n: any) => {
    const name = (n.name || "").toLowerCase();
    const matchesSearch = !search || name.includes(search.toLowerCase());
    const matchesType = typeFilter === "all" || n._type === typeFilter;
    return matchesSearch && matchesType;
  });

  if (loading) return <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-sm text-slate-500">Loading nodes...</span></div>;

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">节点管理</h1>
      <p className="text-sm text-slate-500 mb-6">管理所有 Universe 节点: 企业、服务商、行业、能力。</p>

      <div className="flex gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input type="text" placeholder="搜索节点..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-blue-500" />
        </div>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
          <option value="all">全部类型</option>
          <option value="企业">企业</option>
          <option value="服务商">服务商</option>
          <option value="行业">行业</option>
        </select>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">名称</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">类型</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">GEO Score</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">证据</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">关系</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 20).map((n: any, i: number) => (
              <tr key={n.id || i} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{n.name}</td>
                <td className="px-4 py-3"><span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded">{n._type}</span></td>
                <td className="px-4 py-3 text-sm">{n.geo_score ?? "-"}</td>
                <td className="px-4 py-3 text-sm">{n.evidence_count ?? "-"}</td>
                <td className="px-4 py-3 text-sm">{n.relationship_count ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-400 mt-3">共 {filtered.length} 个节点</p>
    </div>
  );
}
