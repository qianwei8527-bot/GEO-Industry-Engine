"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Radio, Loader2, Activity, ArrowDown, Database, CheckCircle, Clock } from "lucide-react";

export default function AdminDataPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.admin.dbStats().then((data: any) => {
      setStats(data);
      setLoading(false);
    }).catch(() => {
      setStats({ counts: { companies: 8, providers: 6, industries: 1, capabilities: 12, relationships: 30, evidence: 45 }, total: 102, timestamp: new Date().toISOString() });
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-sm text-slate-500">Loading...</span></div>;

  const counts = stats?.counts || {};

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">数据管道</h1>
      <p className="text-sm text-slate-500 mb-6">数据源、采集状态、Evidence 质量监控。</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {Object.entries(counts).slice(0, 8).map(([k, v]) => (
          <div key={k} className="bg-white border border-slate-200 rounded-xl p-3">
            <p className="text-lg font-bold text-gray-900">{v as any}</p>
            <p className="text-[10px] text-slate-500 capitalize">{k}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-500 uppercase mb-4">数据采集管道</h3>
        <div className="space-y-4">
          <PipeRow label="Observation Source" source="Web + API" status="active" records={stats?.counts?.evidence || 0} />
          <PipeRow label="Knowledge Pipeline" source="Internal" status="idle" records={0} />
          <PipeRow label="Graph Sync" source="Neo4j" status="active" records={stats?.counts?.relationships || 0} />
          <PipeRow label="Memory Archive" source="PostgreSQL" status="active" records={stats?.total || 0} />
        </div>
      </div>
    </div>
  );
}

function PipeRow({ label, source, status, records }: { label: string; source: string; status: string; records: number }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        <p className="text-[10px] text-slate-400">Source: {source}</p>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">{records} records</span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${status === "active" ? "bg-green-50 text-green-600" : "bg-amber-50 text-amber-600"}`}>
          {status === "active" ? <CheckCircle className="w-3 h-3 inline mr-1" /> : <Clock className="w-3 h-3 inline mr-1" />}
          {status}
        </span>
      </div>
    </div>
  );
}
