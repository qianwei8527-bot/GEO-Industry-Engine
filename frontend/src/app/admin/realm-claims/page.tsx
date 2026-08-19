"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

function auth() {
  const t = localStorage.getItem("geo_token") || "";
  return { "Content-Type": "application/json", Authorization: `Bearer ${t}` };
}

export default function RealmClaimsReview() {
  const [claims, setClaims] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/realm/claims`, { headers: auth() });
      if (!res.ok) throw new Error("无法加载认领队列");
      const data = await res.json();
      setClaims(data.claims || []);
    } catch (e: any) {
      setError(e.message || "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function decide(id: string, decision: string) {
    setError("");
    try {
      const res = await fetch(`${API_BASE}/realm/claims/${id}/decision`, {
        method: "POST",
        headers: auth(),
        body: JSON.stringify({ decision, reason: "治理员审核" }),
      });
      if (!res.ok) throw new Error("审核失败");
      await load();
    } catch (e: any) {
      setError(e.message || "审核失败");
    }
  }

  if (loading) return <div className="text-slate-400">加载中...</div>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">域认领审核队列</h1>
        <p className="text-sm text-slate-500 mt-1">已有镜像域的认领必须治理批准后才能产生控制权。</p>
      </div>
      {error && <div className="mb-4 rounded-lg bg-rose-50 border border-rose-200 px-4 py-3 text-sm text-rose-700">{error}</div>}
      {claims.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-400">暂无待审核认领</div>
      ) : (
        <div className="space-y-3">
          {claims.map((c: any) => (
            <div key={c.claim_id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-slate-800">{c.entity_name}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{c.entity_type} · {c.entity_id}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => decide(c.claim_id, "approved")}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs hover:bg-emerald-700">批准</button>
                  <button onClick={() => decide(c.claim_id, "rejected")}
                    className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-600 text-xs hover:border-rose-300 hover:text-rose-600">驳回</button>
                </div>
              </div>
              <div className="text-xs text-slate-500 mt-2">申请人 {c.claimant_id} · {c.reason || "未填写理由"}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
