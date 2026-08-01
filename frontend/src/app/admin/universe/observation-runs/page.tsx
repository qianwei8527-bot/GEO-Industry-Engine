"use client";

import { useState, useEffect } from "react";
import { Loader2, RefreshCw, Activity, Hash, AlertTriangle, CheckCircle2 } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const TOKEN = typeof window !== "undefined" ? localStorage.getItem("geo_token") : "";

export default function ObservationRunsPage() {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/universe/observation-runs`, { headers: { Authorization: `Bearer ${TOKEN}` } });
      if (!r.ok) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; }
      const d = await r.json();
      setRuns(Array.isArray(d.runs) ? d.runs : []);
    } catch { setRuns([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const statusColor: Record<string, string> = {
    completed: "bg-green-50 text-green-700",
    failed: "bg-rose-50 text-rose-600",
    running: "bg-blue-50 text-blue-600",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900 mb-1">观察运行记录</h1>
          <p className="text-sm text-slate-500">每次采集的 HTTP 状态、内容哈希、候选提取与审核入口</p>
        </div>
        <button onClick={load} className="p-2 bg-white border border-slate-200 rounded-lg"><RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? "animate-spin" : ""}`} /></button>
      </div>
      {loading ? <div className="flex items-center gap-2 text-slate-500"><Loader2 className="w-5 h-5 animate-spin" /> 加载运行...</div>
        : runs.length === 0 ? <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400">暂无运行记录</div>
        : <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs text-slate-500 uppercase">
                <tr><th className="px-4 py-3">来源</th><th className="px-4 py-3">状态</th><th className="px-4 py-3">HTTP</th><th className="px-4 py-3">内容哈希</th><th className="px-4 py-3">候选</th><th className="px-4 py-3">时间</th></tr>
              </thead>
              <tbody>
                {runs.map((r: any) => (
                  <tr key={r.run_id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-medium">{r.source_id}</td>
                    <td className="px-4 py-3"><span className={`text-xs px-2 py-1 rounded-full ${statusColor[r.status] || "bg-slate-100"}`}>{r.status}</span></td>
                    <td className="px-4 py-3">{r.http_status ?? "—"}</td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-500">{r.content_hash?.slice(0, 10) || "—"}{r.content_hash !== r.previous_content_hash && r.content_hash ? <span className="text-amber-600 ml-1">*</span> : ""}</td>
                    <td className="px-4 py-3">{r.candidates_found || 0}{r.change_created ? <CheckCircle2 className="w-3.5 h-3.5 text-green-600 inline ml-1" /> : ""}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{r.started_at?.slice(0, 19).replace("T", " ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>}
    </div>
  );
}
