"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Globe, Loader2, Activity, Eye, TrendingUp, Clock, Zap, Shield, AlertCircle } from "lucide-react";

interface UniverseOverview {
  universe_stats?: {
    industries?: number;
    companies?: number;
    relationships?: number;
    observations?: number;
  };
}

interface DbStatsPayload {
  counts?: Record<string, number>;
}

export default function AdminUniversePage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.graph.overview().catch(() => null),
      api.admin.dbStats().catch(() => null),
    ]).then(([overview, dbStats]) => {
      setStats({
        overview: ((overview ?? {}) as UniverseOverview).universe_stats || {},
        db: ((dbStats ?? {}) as DbStatsPayload).counts || {},
      });
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span className="text-sm text-slate-500">Loading...</span></div>;

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">宇宙监控</h1>
      <p className="text-sm text-slate-500 mb-6">Observation、CandidateChange、EmergingPattern、KnowledgeCandidate 实时状态。</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Globe} label="产业数" value={stats?.overview?.industries || 0} color="blue" />
        <StatCard icon={Building2} label="企业数" value={stats?.overview?.companies || 0} color="green" />
        <StatCard icon={Activity} label="关系数" value={stats?.overview?.relationships || 0} color="purple" />
        <StatCard icon={Eye} label="观察信号" value={stats?.overview?.observations || 0} color="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-500 uppercase mb-4">宇宙健康</h3>
          <div className="space-y-3">
            <HealthRow label="Observation Engine" status="running" />
            <HealthRow label="Knowledge Pipeline" status="idle" />
            <HealthRow label="Rule Engine" status="running" />
            <HealthRow label="Graph Service" status="running" />
            <HealthRow label="Memory Layer" status="active" />
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-500 uppercase mb-4">学习循环状态</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Observation → Evidence</span><span className="text-green-600 font-medium">活跃</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Evidence → CandidateChange</span><span className="text-green-600 font-medium">活跃</span></div>
            <div className="flex justify-between"><span className="text-slate-500">CandidateChange → Knowledge</span><span className="text-amber-500 font-medium">待确认</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Knowledge → Law</span><span className="text-slate-400">未启动</span></div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-700">Sprint 6.1 验证完成: Universe 首次成功发现未知概念 (AI Employee)。下一步: Knowledge Recognition Layer。</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: number; color: string }) {
  const colors: Record<string, string> = { blue: "text-blue-600 bg-blue-50", green: "text-green-600 bg-green-50", purple: "text-purple-600 bg-purple-50", amber: "text-amber-600 bg-amber-50" };
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color] || ""}`}><Icon className="w-5 h-5" /></div>
        <div><p className="text-2xl font-bold text-gray-900">{value}</p><p className="text-xs text-slate-500">{label}</p></div>
      </div>
    </div>
  );
}

function HealthRow({ label, status }: { label: string; status: string }) {
  const statusColors: Record<string, string> = { running: "text-green-600", active: "text-green-600", idle: "text-amber-500", stopped: "text-red-500" };
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-slate-700">{label}</span>
      <span className={`text-xs font-medium px-2 py-1 rounded-full bg-slate-100 ${statusColors[status] || "text-slate-500"}`}>{status}</span>
    </div>
  );
}

import { Building2 } from "lucide-react";
