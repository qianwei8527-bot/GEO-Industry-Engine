"use client";

import { useState, useEffect } from "react";
import {
  Loader2, RefreshCw, CheckCircle2, XCircle, ArrowRight, Shield,
  AlertTriangle, FileSearch, Layers, Scale, User, Clock, ChevronRight,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const STATUS_COLORS: Record<string, string> = {
  OBSERVED: "bg-slate-100 text-slate-600",
  PENDING_REVIEW: "bg-amber-50 text-amber-700",
  APPROVED: "bg-blue-50 text-blue-700",
  APPLYING: "bg-indigo-50 text-indigo-700",
  APPLIED: "bg-green-50 text-green-700",
  REJECTED: "bg-rose-50 text-rose-700",
  FAILED: "bg-red-50 text-red-700",
  SUPERSEDED: "bg-slate-100 text-slate-500",
};

const IMPACT_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-50 text-amber-700",
  high: "bg-rose-50 text-rose-700",
};

export default function AdminChangesPage() {
    const [authChecked, setAuthChecked] = useState(false);
  const [authOk, setAuthOk] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("geo_token");
    if (!token) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; }
    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (!r.ok) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; } setAuthOk(true); setAuthChecked(true); })
      .catch(() => { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); });
  }, []);

const [changes, setChanges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [reason, setReason] = useState("");
  const [actingId, setActingId] = useState("");
  const [actor, setActor] = useState("admin");

  const load = async () => {
    setLoading(true);
    try {
      const qs = filter ? `?status=${filter}` : "";
      const res = await fetch(`${API_BASE}/universe/changes${qs}`);
      const data = await res.json();
      setChanges(Array.isArray(data.changes) ? data.changes : []);
    } catch { setChanges([]); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [filter]);

  const act = async (id: string, action: "approve" | "reject" | "apply", reasonText = "") => {
    setActingId(id);
    try {
      await fetch(`${API_BASE}/universe/changes/${id}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor, reason: reasonText || reason || "管理员操作" }),
      });
      setReason("");
      await load();
    } catch { /* surface next load */ }
    setActingId("");
  };

  const changeLabel: Record<string, string> = {
    user_evidence: "新增证据",
    evidence_verification_change: "证据验证变化",
    profile_update: "企业资料更新",
    admin_observation: "管理员产业观察",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900 mb-1">变化审核</h1>
          <p className="text-sm text-slate-500">C6.1 持续学习循环 — 每个变化必须有来源、影响范围和审核记录</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-slate-100 rounded-lg p-0.5">
            {["", "PENDING_REVIEW", "APPROVED", "APPLIED", "REJECTED"].map(s => (
              <button key={s} onClick={() => setFilter(s)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${filter === s ? "bg-white shadow text-slate-800" : "text-slate-500"}`}>
                {s === "" ? "全部" : s.replace("_", " ")}
              </button>
            ))}
          </div>
          <button onClick={load} className="p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50">
            <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-500"><Loader2 className="w-5 h-5 animate-spin" /> 加载变化...</div>
      ) : changes.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400">
          暂无变化。新观察进入后会在审核队列中显示。
        </div>
      ) : (
        <div className="space-y-4">
          {changes.map((c: any) => (
            <div key={c.id} className="bg-white border border-slate-200 rounded-xl p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                    <FileSearch className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{c.signal_label || changeLabel[c.change_type] || c.change_type}</h3>
                    <p className="text-xs text-slate-500">节点 {c.node_id?.slice(0, 8)} · {changeLabel[c.change_type] || c.change_type} · 来源 {c.source}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[c.review_status] || ""}`}>{c.review_status}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${IMPACT_COLORS[c.impact_level] || ""}`}>{c.impact_level} 影响</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-[10px] text-slate-500 uppercase mb-1">变化前后</p>
                  <div className="flex items-center gap-2 text-xs">
                    <pre className="flex-1 bg-white border border-slate-200 rounded p-2 text-[10px] overflow-auto max-h-20">{JSON.stringify(c.before_value || {}, null, 2)}</pre>
                    <ArrowRight className="w-3 h-3 text-slate-400" />
                    <pre className="flex-1 bg-blue-50 border border-blue-200 rounded p-2 text-[10px] overflow-auto max-h-20 text-blue-900">{JSON.stringify(c.proposed_value || {}, null, 2)}</pre>
                  </div>
                </div>
                <div className="space-y-2 text-xs">
                  <Row label="置信度" value={`${Math.round((c.confidence_level || 0) * 100)}%`} />
                  <Row label="证据" value={c.evidence_summary || "无摘要"} />
                  <Row label="受影响引擎" value={(c.affected_engines || []).join(", ") || "无"} />
                  <Row label="适用规则" value={(c.applicable_rules || []).join(", ") || "无"} />
                  <Row label="来源 ID" value={c.source_id || "—"} />
                  {c.rejection_reason && <Row label="拒绝理由" value={c.rejection_reason} color="text-rose-600" />}
                </div>
              </div>

              {c.review_status === "PENDING_REVIEW" && (
                <div className="flex items-center gap-2 border-t border-slate-100 pt-3">
                  <input value={reason} onChange={e => setReason(e.target.value)} placeholder="操作理由（必填）"
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-blue-400" />
                  <button onClick={() => act(c.id, "approve", "批准")} disabled={!!actingId}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 批准
                  </button>
                  <button onClick={() => act(c.id, "reject", "拒绝")} disabled={!!actingId}
                    className="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg text-xs font-medium flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> 拒绝
                  </button>
                </div>
              )}
              {c.review_status === "APPROVED" && (
                <div className="flex items-center gap-2 border-t border-slate-100 pt-3">
                  <button onClick={() => act(c.id, "apply", "应用")} disabled={!!actingId}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium flex items-center gap-1">
                    <Shield className="w-3.5 h-3.5" /> 应用变化
                  </button>
                  <span className="text-xs text-slate-400">批准人：{c.actor_id}</span>
                </div>
              )}
              {c.applied_result && (
                <div className="mt-3 px-3 py-2 bg-slate-50 rounded-lg text-[10px] text-slate-500">
                  应用结果：{JSON.stringify(c.applied_result)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-slate-400 flex-shrink-0">{label}</span>
      <span className={`text-right ${color || "text-slate-700"}`}>{value}</span>
    </div>
  );
}
