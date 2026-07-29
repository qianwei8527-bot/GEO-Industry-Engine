'use client';
import { useEffect, useState } from 'react';
import { Factory } from 'lucide-react';
interface IndustryItem { id: string; name: string; code: string; level: number; sort_order: number }

export default function AdminIndustriesPage() {
  const [industries, setIndustries] = useState<IndustryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/admin/industries').then(r=>r.json()).then(d=>{setIndustries(d);setLoading(false)}).catch(()=>setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400">加载中...</div>;

  return (
    <div>
      <div className="mb-6"><h1 className="text-2xl font-bold text-slate-900">行业管理</h1><p className="text-sm text-slate-500 mt-1">共 {industries.length} 个行业分类</p></div>
      <div className="grid md:grid-cols-2 gap-4">
        {industries.map(ind => (
          <div key={ind.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0"><Factory className="w-5 h-5 text-blue-500" /></div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-slate-800">{ind.name}</h3>
              <div className="flex gap-3 mt-1 text-xs text-slate-400">
                <span>Code: {ind.code}</span><span>Level: {ind.level}</span><span>Order: {ind.sort_order}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
