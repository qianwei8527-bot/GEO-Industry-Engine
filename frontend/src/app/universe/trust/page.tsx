"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Eye, FlaskConical, HelpCircle, Loader2, RefreshCw, Search } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export default function TrustBoundaryPage() {
  const [nodeId, setNodeId] = useState("");
  const [input, setInput] = useState("");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = (id: string) => {
    if (!id) return;
    setLoading(true);
    fetch(`${API_BASE}/universe/trust/boundary/${encodeURIComponent(id)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        setData(d);
        setNodeId(id);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetch(`${API_BASE}/companies/?limit=1`)
      .then((r) => r.json())
      .then((list: any) => {
        const arr = Array.isArray(list) ? list : (list.companies || list.items || []);
        if (arr.length > 0) {
          const id = arr[0].id || "";
          setInput(id);
          load(id);
        } else {
          setLoading(false);
        }
      })
      .catch(() => setLoading(false));
  }, []);

  const ev = data?.evidence || {};
  const ai = data?.ai_answers || {};
  const kn = data?.knowledge || {};

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="pb-8 border-b border-slate-800">
          <a href="/universe/home" className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-white mb-6 transition">
            ← Universe
          </a>
          <h1 className="text-3xl font-bold tracking-tight">Trust Boundary</h1>
          <p className="text-sm text-slate-500 mt-2">Verified / Observed / Synthetic / Unknown</p>
          <div className="mt-5 flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && load(input)}
              placeholder="Node ID"
              className="w-72 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
            />
            <button onClick={() => load(input)} className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:border-blue-500">
              <Search className="w-4 h-4 text-slate-400" />
            </button>
            <button onClick={() => load(nodeId)} className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:border-blue-500">
              <RefreshCw className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24"><Loader2 className="w-7 h-7 text-blue-400 animate-spin" /></div>
        ) : data ? (
          <div className="py-8">
            <div className="grid md:grid-cols-4 gap-4">
              <Count label="Verified Facts" value={ev.verified_facts ?? 0} color="text-emerald-400" bg="bg-emerald-500/10 border-emerald-500/25" icon={<ShieldCheck className="w-5 h-5" />} />
              <Count label="Observed Facts" value={ev.observed_facts ?? 0} color="text-amber-400" bg="bg-amber-500/10 border-amber-500/25" icon={<Eye className="w-5 h-5" />} />
              <Count label="Synthetic Data" value={(ev.synthetic_data ?? 0) + (kn.synthetic_candidates ?? 0)} color="text-rose-400" bg="bg-rose-500/10 border-rose-500/25" icon={<FlaskConical className="w-5 h-5" />} />
              <Count label="Unknown" value={ev.unknown ?? 0} color="text-slate-300" bg="bg-slate-700/20 border-slate-600/30" icon={<HelpCircle className="w-5 h-5" />} />
            </div>

            <section className="mt-10 py-6 border-b border-slate-800">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Evidence</h2>
              <div className="flex flex-wrap gap-2 text-sm">
                <Badge label="Total" value={ev.total ?? 0} />
                <Badge label="Verified" value={ev.verified_facts ?? 0} tone="emerald" />
                <Badge label="Observed" value={ev.observed_facts ?? 0} tone="amber" />
                <Badge label="Pending Review" value={ev.pending_review ?? 0} />
                <Badge label="Inferred" value={ev.inferred ?? 0} />
                <Badge label="Synthetic" value={ev.synthetic_data ?? 0} tone="rose" />
                <Badge label="Unknown" value={ev.unknown ?? 0} />
              </div>
            </section>

            <section className="mt-8 py-6 border-b border-slate-800">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">AI Answers</h2>
              <div className="flex flex-wrap gap-2 text-sm">
                <Badge label="Total" value={ai.total ?? 0} />
                <Badge label="Fake" value={ai.by_origin?.fake ?? 0} tone="rose" />
                <Badge label="Real" value={ai.by_origin?.real ?? 0} tone="emerald" />
                <Badge label="Baseline Eligible" value={ai.baseline_eligible ?? 0} tone="sky" />
              </div>
            </section>

            <section className="mt-8 py-6">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Knowledge Candidates</h2>
              <div className="flex flex-wrap gap-2 text-sm">
                <Badge label="Synthetic" value={kn.synthetic_candidates ?? 0} tone="rose" />
              </div>
            </section>
          </div>
        ) : (
          <p className="text-sm text-slate-500 py-16 text-center">无法加载信任边界。</p>
        )}
      </div>
    </div>
  );
}

function Count({ label, value, color, bg, icon }: { label: string; value: number; color: string; bg: string; icon: any }) {
  return (
    <div className={`rounded-lg border p-5 ${bg}`}>
      <div className={`flex items-center gap-2 ${color}`}>{icon}<span className="text-xs uppercase tracking-wider">{label}</span></div>
      <div className={`text-4xl font-bold mt-3 ${color}`}>{value}</div>
    </div>
  );
}

function Badge({ label, value, tone = "slate" }: { label: string; value: number; tone?: string }) {
  const tones: Record<string, string> = {
    emerald: "bg-emerald-500/10 text-emerald-300 border-emerald-500/25",
    amber: "bg-amber-500/10 text-amber-300 border-amber-500/25",
    rose: "bg-rose-500/10 text-rose-300 border-rose-500/25",
    sky: "bg-sky-500/10 text-sky-300 border-sky-500/25",
    slate: "bg-slate-800/60 text-slate-300 border-slate-700/40",
  };
  return (
    <span className={`px-3 py-1.5 rounded-lg border ${tones[tone] || tones.slate}`}>
      {label}: {value}
    </span>
  );
}
