'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Award, Building2, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

export default function ApplyPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<any[]>([]);
  const [form, setForm] = useState({ entity_id: '', target_level: 'L1', cert_type: 'identity', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.companies.list().then((d: any) => setCompanies(Array.isArray(d) ? d : d?.items || [])).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.entity_id) { setError('请选择一家企业'); return; }
    setSubmitting(true); setError('');
    try {
      const entityType = form.cert_type === 'individual' ? 'individual' : form.cert_type === 'service' ? 'provider' : 'enterprise';
      const res = await api.certification.apply({
        entity_id: form.entity_id,
        entity_type: entityType,
        target_level: form.target_level,
        cert_type: form.cert_type,
        description: form.description,
      } as any);
      setResult(res);
    } catch (err: any) {
      setError(err?.message || '提交失败，请重试');
    } finally { setSubmitting(false); }
  };

  if (result) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <Award className="w-12 h-12 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">申请已提交</h2>
        <p className="text-gray-500 mb-1">认证ID: {result.id?.substring(0,8)}...</p>
        <p className="text-sm text-gray-400 mb-6">状态: {result.status} | 等级: {result.level}</p>
        <div className="flex gap-3 justify-center">
          <button onClick={() => router.push('/certification/review-status')} className='px-4 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700'>查看审核状态</button>
          <button onClick={() => router.push('/certification')} className='px-4 py-2 border border-gray-300 rounded-xl text-sm hover:bg-gray-50'>返回认证中心</button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">申请 GEO 认证</h1>
      <p className="text-sm text-gray-500 mb-8">选择待认证的企业实体，提交认证申请。认证通过后将提升企业的 Trust Score 和产业可见度。</p>
      {error && <div className='mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600'>{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">选择企业</label>
          <select value={form.entity_id} onChange={(e) => setForm({...form, entity_id: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" required>
            <option value=''>-- 请选择企业 --</option>
            {companies.map((c: any) => (
              <option key={c.id || c.entity_id} value={c.id || c.entity_id}>
                {c.name || c.company_name || '未命名企业'} {c.industry_name ? '· ' + c.industry_name : ''}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">认证类型</label>
          <select value={form.cert_type} onChange={(e) => setForm({...form, cert_type: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400">
            <option value='identity'>企业身份认证</option>
            <option value='capability'>能力认证</option>
            <option value='service'>服务商认证</option>
            <option value='individual'>个人认证</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">目标等级</label>
          <select value={form.target_level} onChange={(e) => setForm({...form, target_level: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400">
            <option value='L1'>L1 — 基础身份认证</option>
            <option value='L2'>L2 — GEO生态认证</option>
            <option value='L3'>L3 — 专业能力认证</option>
            <option value='L4'>L4 — 行业权威认证</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">补充说明</label>
          <textarea value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} rows={3} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" placeholder="可选：补充认证相关的说明" />
          <div className="border-t mt-6 pt-3 mb-4">
            <div className="text-xs text-slate-400 mb-2">相关功能:</div>
            <div className="flex flex-wrap gap-2">
              <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>认证中心</Link>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>检测中心</Link>
              <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>补充证据</Link>
            </div>
          </div>
        </div>
        <button type="submit" disabled={submitting} className="w-full bg-blue-600 text-white py-3 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-60 flex items-center justify-center gap-2">
          {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
          {submitting ? '提交中...' : '提交申请'}
        </button>
      </form>
    </div>
  );
}
