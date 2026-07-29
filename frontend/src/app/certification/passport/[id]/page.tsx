'use client';
import { api } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Award, Shield, ArrowLeft } from 'lucide-react';

export default function PassportPage() {
  const { id } = useParams();
  const [data, setData] = useState(null as any);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.certification.get(id as string).then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, [id]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <Link href="/certification" className="text-sm text-slate-500 hover:text-slate-300 inline-flex items-center gap-1 mb-6"><ArrowLeft className="w-4 h-4" /> 返回认证中心</Link>
      <h1 className="text-3xl font-bold text-slate-100 mb-2 flex items-center gap-2"><Award className="w-6 h-6 text-emerald-400" /> GEO数字护照</h1>
      <p className="text-slate-400 mb-8">企业GEO身份认证凭证，记录能力、证据、信任状态</p>
      {loading ? <div className="text-center py-16 text-slate-500">加载中...</div> : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8">
          <div className="flex items-center gap-4 mb-6">
            <Shield className="w-16 h-16 text-emerald-400" />
            <div>
              <div className="text-2xl font-bold text-slate-100">GEO 数字护照</div>
              <div className="text-sm text-slate-500">ID: {id}</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-slate-500">认证状态:</span> <span className="text-yellow-400">待认证</span></div>
            <div><span className="text-slate-500">有效期:</span> <span className="text-slate-300">认证后12个月</span></div>
          </div>
        </div>
      )}
    </div>
  );
}
