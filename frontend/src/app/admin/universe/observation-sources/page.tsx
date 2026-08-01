"use client";

import { useState, useEffect } from "react";
import { Loader2, RefreshCw, Play, Pause, Globe, ShieldCheck, Clock } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const TOKEN = typeof window !== "undefined" ? localStorage.getItem("geo_token") : "";

export default function ObservationSourcesPage() {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/universe/observation-sources`, { headers: { Authorization: `Bearer ${TOKEN}` } });
      if (!r.ok) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; }
      const d = await r.json();
      setSources(Array.isArray(d.sources) ? d.sources : []);
    } catch { setSources([]); }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const act = async (sid: string, action: "enable" | "disable" | "run") => {
    setBusy(sid + action);
    await fetch(`${API_BASE}/universe/observation-sources/${sid}/${action}`, { method: "POST", headers: { Authorization: `Bearer ${TOKEN}` } });
    await load();
    setBusy("");
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900 mb-1">外部观察来源</h1>
          <p className="text-sm text-slate-500">白名单来源 · 外部内容只产生候选变化，永不直接成为事实</p>
        </div>
        <button onClick={load} className="p-2 bg-white border border-slate-200 rounded-lg"><RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? "animate-spin" : ""}`} /></button>
      </div>

      {loading ? <div className="flex items-center gap-2 text-slate-500"><Loader2 className="w-5 h-5 animate-spin" /> 加载来源...</div>
        : sources.length === 0 ? <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400">暂无来源</div>
        : <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sources.map((s: any) => (
              <div key={s.source_id} className="bg-white border border-slate-200 rounded-xl p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center"><Globe className="w-4 h-4 text-blue-600" /></div>
                    <div>
                      <h3 className="font-medium text-gray-900">{s.name}</h3>
                      <p className="text-xs text-slate-500">{s.source_type} · {s.trust_tier} · 节点 {s.node_id?.slice(0, 8) || "全局"}</p>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${s.enabled && !s.paused ? "bg-green-50 text-green-700" : s.paused ? "bg-rose-50 text-rose-600" : "bg-slate-100 text-slate-500"}`}>
                    {s.paused ? "已暂停" : s.enabled ? "启用" : "停用"}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-500 mb-3">
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> 每 {s.schedule_minutes || 1440} 分钟</span>
                  <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> 连续失败 {s.consecutive_failures || 0}</span>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => act(s.source_id, "run")} disabled={!!busy} className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs"><Play className="w-3 h-3 inline mr-1" />运行</button>
                  {s.enabled && !s.paused
                    ? <button onClick={() => act(s.source_id, "disable")} className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-xs"><Pause className="w-3 h-3 inline mr-1" />停用</button>
                    : <button onClick={() => act(s.source_id, "enable")} className="px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-xs">启用</button>}
                </div>
              </div>
            ))}
          </div>}
    </div>
  );
}
