'use client';
import { api } from '@/lib/api';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Swords, TrendingUp, ArrowLeft } from 'lucide-react';

export default function CompetitorsPage() {
  const [data, setData] = useState([] as any[]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.companies.list().then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <Link href="/intelligence" className="text-sm text-slate-500 hover:text-slate-300 inline-flex items-center gap-1 mb-6"><ArrowLeft className="w-4 h-4" /> 返回产业情报</Link>
      <h1 className="text-3xl font-bold text-slate-100 mb-2 flex items-center gap-2"><Swords className="w-6 h-6 text-red-400" /> 竞争分析</h1>
      <p className="text-slate-400 mb-8">识别行业竞争对手、对比GEO表现、发现竞争差距</p>
      {loading ? <div className="text-center py-16 text-slate-500">加载中...</div> : (
        <div className="grid md:grid-cols-2 gap-4">
          {data.map((c: any) => (
            <Link key={c.id} href={"/company/" + c.id} className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-600 transition-colors">
              <div className="font-medium text-slate-200">{c.name}</div>
              <div className="text-xs text-slate-500 mt-1">GEO Score: {c.geo_score || "--"} | {c.company_size}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
