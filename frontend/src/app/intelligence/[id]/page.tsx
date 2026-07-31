'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, Lightbulb, Shield, Target, Activity, BarChart3 } from 'lucide-react';

export default function GeoIntelPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const r = await fetch('http://127.0.0.1:8080/api/v1/intelligence/benchmark/' + id);
        setData(await r.json());
      } catch (e) {}
      setLoading(false);
    }
    load();
  }, [id]);

  if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center"><div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" /></div>;
  if (!data || data.error) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500"><Activity className="w-8 h-8 mx-auto mb-2" /><p>No intelligence data</p></div>;

  const dims = data.dimensions || [];
  const roadmap = data.roadmap || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <Link href={'/company/' + id} className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-300 mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to Company
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-blue-600 flex items-center justify-center text-white text-xl font-bold">GEO</div>
          <div>
            <h1 className="text-2xl font-bold">{data.company_name}</h1>
            <p className="text-sm text-slate-400">Industry Rank: {data.rank} | {data.total_peers} peers | Top {data.percentile}%</p>
          </div>
        </div>

        {/* Industry Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <StatCard label="GEO Score" value={data.geo_score} color="text-emerald-400" />
          <StatCard label="Industry Avg" value={data.industry_stats?.avg || 0} color="text-slate-400" />
          <StatCard label="Top Score" value={data.industry_stats?.top || 0} color="text-blue-400" />
          <StatCard label="Median" value={data.industry_stats?.median || 0} color="text-purple-400" />
        </div>

        {/* Dimension Gaps */}
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Target className="w-5 h-5 text-yellow-400" /> Dimension Gap Analysis</h2>
        <div className="space-y-3 mb-8">
          {dims.map((d: any, i: number) => {
            const gapColor = d.status === 'lagging' || d.status === 'insufficient' ? 'text-red-400 border-red-900/50' : 'text-emerald-400 border-emerald-900/50';
            return (
              <div key={i} className={'bg-slate-900 border rounded-lg p-4 ' + gapColor.split(' ')[1]}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-200">{d.dimension}</span>
                  <span className={'text-xs font-semibold px-2 py-0.5 rounded-full ' + (d.status === 'lagging' || d.status === 'insufficient' ? 'bg-red-950/50 text-red-400' : 'bg-emerald-950/50 text-emerald-400')}>
                    {d.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-2">
                  <span>My: <strong className="text-slate-300">{d.my_value}</strong></span>
                  <span>Industry Avg: <strong className="text-slate-300">{d.avg_value}</strong></span>
                  <span className={gapColor.split(' ')[0]}>Gap: {d.gap > 0 ? '+' + d.gap : d.gap}</span>
                  {d.percentile !== null && <span>Percentile: {d.percentile}%</span>}
                </div>
                {d.insight && <p className="text-xs text-slate-400">{d.insight}</p>}
              </div>
            );
          })}
        </div>

        {/* Roadmap */}
        {roadmap.length > 0 && (
          <>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-400" /> 90-Day Action Roadmap</h2>
            <div className="space-y-3">
              {roadmap.map((r: any, i: number) => (
                <div key={i} className="flex items-start gap-3 bg-slate-900 border border-slate-800 rounded-lg p-4">
                  <span className={'text-xs font-bold px-2 py-1 rounded ' + (r.priority === 'P0' ? 'bg-red-950/50 text-red-400' : r.priority === 'P1' ? 'bg-yellow-950/50 text-yellow-400' : 'bg-slate-700 text-slate-400')}>
                    {r.priority}
                  </span>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-200">{r.title}</div>
                    <p className="text-xs text-slate-500 mt-1">{r.description}</p>
                    {r.timeframe_days > 0 && <span className="text-xs text-slate-600 mt-1 inline-block">{r.timeframe_days} days</span>}
                    {r.current_gap && <div className="text-xs text-red-400 mt-1">Current gap: {r.current_gap}</div>}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-center">
      <div className={'text-2xl font-bold ' + color}>{typeof value === 'number' ? Math.round(value as number) : value}</div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  );
}