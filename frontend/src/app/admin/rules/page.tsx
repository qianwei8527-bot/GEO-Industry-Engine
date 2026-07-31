"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { FileText, Loader2, Shield, CheckCircle, Clock, AlertCircle } from "lucide-react";

export default function AdminRulesPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.universe.rules().then((data: any) => {
      setRules(Array.isArray(data) ? data : (data.rules || data.items || []));
      setLoading(false);
    }).catch(() => {
      setRules([
        { id: "R01", name: "Universe First", category: "core", status: "active", summary: "Universe不是工具，不是AI聊天，不是数据库。" },
        { id: "R02", name: "Position First", category: "core", status: "active", summary: "每个节点必须先知道自己在哪里，才知道去哪里。" },
        { id: "R03", name: "Node is Life", category: "identity", status: "active", summary: "节点不是数据对象，而是有生命周期的产业生命。" },
        { id: "R04", name: "Growth Chain", category: "growth", status: "active", summary: "成长 = 学习 → 实践 → 案例 → 信任 → 生态节点" },
        { id: "R05", name: "Evidence over Claim", category: "trust", status: "active", summary: "一切信誉必须基于可验证证据。" },
        { id: "R06", name: "Connection is Value", category: "ecosystem", status: "active", summary: "孤立节点没有价值，连接创造产业意义。" },
        { id: "R07", name: "Marketplace Exit", category: "business", status: "draft", summary: "Marketplace是产业地图的自然商业出口。" },
      ]);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-sm text-slate-500">Loading rules...</span></div>;

  const statusIcon = (s: string) => s === "active" ? <CheckCircle className="w-4 h-4 text-green-500" /> : s === "draft" ? <Clock className="w-4 h-4 text-amber-500" /> : <AlertCircle className="w-4 h-4 text-red-500" />;
  const catColor = (c: string) => { const m: Record<string,string> = { core:"blue", identity:"purple", growth:"green", trust:"amber", ecosystem:"cyan", business:"pink" }; return m[c] || "slate"; };

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">规则引擎</h1>
      <p className="text-sm text-slate-500 mb-6">管理 Universe Rules — 世界的物理定律。</p>

      <div className="space-y-3">
        {rules.map((r: any, i: number) => (
          <div key={r.id || i} className="bg-white border border-slate-200 rounded-xl p-4 hover:border-slate-300 transition-all">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-slate-500" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">{r.id}</span>
                    <h3 className="text-sm font-semibold text-gray-900">{r.name}</h3>
                    <span className={`text-[10px] px-1.5 py-0.25 rounded bg-${catColor(r.category)}-50 text-${catColor(r.category)}-600`}>{r.category}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{r.summary}</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                {statusIcon(r.status)}
                <span className="text-[10px] text-slate-400 capitalize">{r.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
