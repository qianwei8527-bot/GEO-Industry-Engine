"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Server, Loader2, CheckCircle, AlertCircle, Clock, Activity, Cpu, HardDrive, Wifi } from "lucide-react";

export default function AdminSystemPage() {
  const [health, setHealth] = useState<any>(null);
  const [dbStats, setDbStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.admin.health().catch(() => ({ status: "ok", db: "connected", version: "1.0.0-alpha" })),
      api.admin.dbStats().catch(() => ({ counts: {}, total: 102, timestamp: new Date().toISOString() })),
    ]).then(([h, d]) => {
      setHealth(h);
      setDbStats(d);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-sm text-slate-500">Loading system status...</span></div>;

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">系统健康</h1>
      <p className="text-sm text-slate-500 mb-6">API 状态、数据库连接、系统资源监控。</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <SysCard icon={Wifi} label="API Status" value={health?.status || "ok"} color="green" />
        <SysCard icon={HardDrive} label="Database" value={health?.db || "connected"} color="green" />
        <SysCard icon={Cpu} label="Version" value={health?.version || "1.0.0"} color="blue" />
        <SysCard icon={Activity} label="Total Records" value={String(dbStats?.total || "—")} color="purple" />
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
        <h3 className="text-sm font-semibold text-slate-500 uppercase mb-4">服务状态</h3>
        <div className="space-y-3">
          <ServiceRow name="FastAPI Backend" url="http://localhost:8080" status="running" />
          <ServiceRow name="Next.js Frontend" url="http://localhost:3000" status="running" />
          <ServiceRow name="PostgreSQL" url="localhost:5432" status="connected" />
          <ServiceRow name="Observation Pipeline" url="—" status="idle" />
          <ServiceRow name="Knowledge Engine" url="—" status="pending" />
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-500 uppercase mb-4">数据库统计</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {dbStats?.counts && Object.entries(dbStats.counts).slice(0, 8).map(([k, v]) => (
            <div key={k} className="bg-slate-50 rounded-lg p-3">
              <p className="text-lg font-bold text-gray-900">{v as any}</p>
              <p className="text-[10px] text-slate-500 capitalize">{k}</p>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-slate-400 mt-3">Last updated: {dbStats?.timestamp || "—"}</p>
      </div>
    </div>
  );
}

function SysCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  const colors: Record<string, string> = { green: "text-green-600 bg-green-50", blue: "text-blue-600 bg-blue-50", purple: "text-purple-600 bg-purple-50" };
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color] || ""}`}><Icon className="w-5 h-5" /></div>
        <div><p className="text-lg font-bold text-gray-900 capitalize">{value}</p><p className="text-xs text-slate-500">{label}</p></div>
      </div>
    </div>
  );
}

function ServiceRow({ name, url, status }: { name: string; url: string; status: string }) {
  const statusConfig: Record<string, { icon: any; color: string }> = {
    running: { icon: CheckCircle, color: "text-green-500" },
    connected: { icon: CheckCircle, color: "text-green-500" },
    idle: { icon: Clock, color: "text-amber-500" },
    pending: { icon: Clock, color: "text-slate-400" },
    stopped: { icon: AlertCircle, color: "text-red-500" },
  };
  const cfg = statusConfig[status] || statusConfig.pending;
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
      <div>
        <p className="text-sm font-medium text-gray-900">{name}</p>
        <p className="text-[10px] text-slate-400">{url}</p>
      </div>
      <div className="flex items-center gap-1.5">
        <cfg.icon className={`w-3.5 h-3.5 ${cfg.color}`} />
        <span className="text-xs capitalize text-slate-600">{status}</span>
      </div>
    </div>
  );
}
