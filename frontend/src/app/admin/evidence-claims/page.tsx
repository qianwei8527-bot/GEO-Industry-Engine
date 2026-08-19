"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

function auth() {
  const t = localStorage.getItem("geo_token") || "";
  return { "Content-Type": "application/json", Authorization: `Bearer ${t}` };
}

export default function EvidenceClaimsReview() {
  const [claims, setClaims] = useState<any[]>([]);
  const [userId, setUserId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const me = await fetch(`${API_BASE}/auth/me`, { headers: auth() });
      if (me.ok) {
        const user = await me.json();
        setUserId(user.id);
      }
      const res = await fetch(`${API_BASE}/universe/claims/review`, { headers: auth() });
      if (!res.ok) throw new Error("无法加载 Claim 队列");
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

  async function verify(id: string) {
    setError("");
    try {
      const res = await fetch(`${API_BASE}/universe/claims/${id}/verify`, {
        method: "POST",
        headers: auth(),
        body: JSON.stringify({ verifier_id: userId, verification_method: "structured_review", verification_result: "approved" }),
      });
      if (!res.ok) throw new Error("验证失败");
      await load();
    } catch (e: any) {
      setError(e.message || "验证失败");
    }
  }

  if (loading) return <div className="text-slate-400">加载中...</div>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">EvidenceClaim 审核队列</h1>
        <p className="text-sm text-slate-500 mt-1">只审核结构化主张；Evidence verified 不等于 Claim verified。</p>
      </div>
      {error && <div className="mb-4 rounded-lg bg-rose-50 border border-rose-200 px-4 py-3 text-sm text-rose-700">{error}</div>}
      {claims.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-400">暂无待审核 Claim</div>
      ) : (
        <div className="space-y-3">
          {claims.map((c: any) => (
            <div key={c.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-medium text-slate-800">{c.claim_text}</div>
                  <div className="text-xs text-slate-400 mt-1">{c.subject_id} · {c.predicate_code} → {c.object_code}</div>
                </div>
                <button onClick={() => verify(c.id)}
                  className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs hover:bg-blue-700">验证</button>
              </div>
              <div className="text-xs text-slate-500 mt-2">evidence {c.evidence_id} · extraction {c.extraction_method}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
