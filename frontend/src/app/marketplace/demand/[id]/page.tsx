'use client';
import { api } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { ShoppingCart, ArrowLeft } from 'lucide-react';

export default function DemandDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState(null as any);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.marketplace.getDemand(id as string).then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, [id]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <Link href="/marketplace" className="text-sm text-slate-500 hover:text-slate-300 inline-flex items-center gap-1 mb-6"><ArrowLeft className="w-4 h-4" /> 返回交易市场</Link>
      <h1 className="text-3xl font-bold text-slate-100 mb-2 flex items-center gap-2"><ShoppingCart className="w-6 h-6 text-purple-400" /> 需求详情</h1>
      <p className="text-slate-400 mb-8">GEO产业交易市场需求信息</p>
      {loading ? <div className="text-center py-16 text-slate-500">加载中...</div> : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8">
          <div className="text-xl font-bold text-slate-100">需求 #{id}</div>
          <div className="text-sm text-slate-500 mt-2">发布方: 待确认 | 预算: 待确认</div>
        </div>
      )}
    </div>
  );
}
