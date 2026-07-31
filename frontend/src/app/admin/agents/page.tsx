"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Bot, Loader2, Play, Pause, Clock, CheckCircle, AlertCircle, Zap } from "lucide-react";

const MOCK_AGENTS = [
  { id: "obs-1", name: "Observation Agent", status: "running", type: "observer", lastRun: "2 min ago", taskCount: 12 },
  { id: "ana-1", name: "Analysis Agent", status: "idle", type: "analyzer", lastRun: "1 hr ago", taskCount: 8 },
  { id: "mat-1", name: "Matching Agent", status: "idle", type: "matcher", lastRun: "5 hr ago", taskCount: 3 },
  { id: "rep-1", name: "Report Agent", status: "stopped", type: "reporter", lastRun: "1 day ago", taskCount: 45 },
];

export default function AdminAgentsPage() {
  const [agents, setAgents] = useState(MOCK_AGENTS);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.admin.dbStats().then(setStats).catch(() => setStats({ counts: { agents: 4 }, total: 0 }));
  }, []);

  const statusIcon = (s: string) => {
    if (s === "running") return <Play className="w-3 h-3 text-green-500" />;
    if (s === "idle") return <Clock className="w-3 h-3 text-amber-500" />;
    return <AlertCircle className="w-3 h-3 text-red-500" />;
  };

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-2">智能体管理</h1>
      <p className="text-sm text-slate-500 mb-6">管理 Universe Agent 实例、任务队列和执行日志。</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-2xl font-bold text-gray-900">{agents.length}</p><p className="text-xs text-slate-500">Agent 总数</p></div>
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-2xl font-bold text-green-600">{agents.filter(a => a.status === "running").length}</p><p className="text-xs text-slate-500">运行中</p></div>
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-2xl font-bold text-gray-900">{agents.reduce((s, a) => s + a.taskCount, 0)}</p><p className="text-xs text-slate-500">总任务数</p></div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Agent</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">类型</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">状态</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">上次运行</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">任务</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((a) => (
              <tr key={a.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3"><div className="flex items-center gap-2"><Bot className="w-4 h-4 text-blue-500" /><span className="text-sm font-medium text-gray-900">{a.name}</span></div></td>
                <td className="px-4 py-3"><span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded">{a.type}</span></td>
                <td className="px-4 py-3"><div className="flex items-center gap-1.5">{statusIcon(a.status)}<span className="text-xs capitalize">{a.status}</span></div></td>
                <td className="px-4 py-3 text-xs text-slate-500">{a.lastRun}</td>
                <td className="px-4 py-3 text-sm">{a.taskCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
