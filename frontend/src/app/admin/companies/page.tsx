'use client';
import { useEffect, useState } from 'react';
import { Building2, Search, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

interface CompanyItem { id: string; name: string; geo_id: string; industry_id: string|null; is_verified: boolean; geo_score: number; subscription_tier: string; created_at: string }

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [filtered, setFiltered] = useState<CompanyItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/admin/companies').then(r=>r.json()).then(d=>{setCompanies(d);setFiltered(d);setLoading(false)}).catch(()=>setLoading(false));
  }, []);

  useEffect(() => {
    const q=search.toLowerCase();
    setFiltered(companies.filter(c=>c.name.toLowerCase().includes(q)||(c.geo_id||'').toLowerCase().includes(q)));
  }, [search, companies]);

  if (loading) return <div className="text-slate-400">加载中...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-slate-900">企业管理</h1><p className="text-sm text-slate-500 mt-1">共 {companies.length} 家企业实体</p></div>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input type="text" placeholder="搜索企业..." value={search} onChange={e=>setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 w-56" />
        </div>
      </div>
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr><th className="text-left px-4 py-3 text-slate-500 font-medium">企业</th><th className="text-left px-4 py-3 text-slate-500 font-medium">GEO ID</th><th className="text-left px-4 py-3 text-slate-500 font-medium">评分</th><th className="text-left px-4 py-3 text-slate-500 font-medium">认证</th><th className="text-left px-4 py-3 text-slate-500 font-medium">订阅</th><th className="text-left px-4 py-3 text-slate-500 font-medium">创建时间</th><th className="text-left px-4 py-3 text-slate-500 font-medium">操作</th></tr>
          </thead>
          <tbody>
            {filtered.map(c=>(
              <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3"><div className="flex items-center gap-2"><Building2 className="w-4 h-4 text-slate-400" /><span className="font-medium text-slate-800">{c.name}</span></div></td>
                <td className="px-4 py-3 text-slate-500 font-mono text-xs">{c.geo_id}</td>
                <td className="px-4 py-3"><span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${(c.geo_score||0)>=70?'bg-green-100 text-green-700':(c.geo_score||0)>=40?'bg-amber-100 text-amber-700':'bg-slate-100 text-slate-600'}`}>{c.geo_score||0}</span></td>
                <td className="px-4 py-3">{c.is_verified?<CheckCircle className="w-4 h-4 text-green-500"/>:<XCircle className="w-4 h-4 text-slate-300"/>}</td>
                <td className="px-4 py-3 text-slate-500 capitalize">{c.subscription_tier}</td>
                <td className="px-4 py-3 text-slate-400 text-xs">{c.created_at?.split('T')[0]}</td>
                <td className="px-4 py-3"><Link href={`/company/${c.id}`} className="text-blue-600 hover:underline text-xs">查看</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length===0 && <div className="p-8 text-center text-slate-400">没有匹配的企业</div>}
      </div>
    </div>
  );
}
