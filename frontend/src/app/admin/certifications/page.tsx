'use client';
import { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle, XCircle, Clock, RefreshCw, ChevronDown } from 'lucide-react';
import { api } from '@/lib/api';

const STATUS_MAP: Record<string, { label: string; color: string; icon: any }> = {
  pending: { label: '待审核', color: 'text-amber-600', icon: Clock },
  ai_review: { label: 'AI初筛', color: 'text-blue-600', icon: ShieldCheck },
  human_review: { label: '人工复审', color: 'text-purple-600', icon: ShieldCheck },
  approved: { label: '已通过', color: 'text-green-600', icon: CheckCircle },
  rejected: { label: '已驳回', color: 'text-red-600', icon: XCircle },
};

const LEVEL_LABELS: Record<string, string> = {
  L0: 'L0·未认证', L1: 'L1·基础身份', L2: 'L2·生态认证', L3: 'L3·专业能力', L4: 'L4·行业权威',
};

export default function AdminCertificationsPage() {
  const [pending, setPending] = useState<any[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [message, setMessage] = useState('');

  const loadData = async () => {
    try {
      const p = await api.certification.list();
      const items = Array.isArray(p) ? p : (p as any)?.items || [];
      setPending(items.filter((r: any) => ['pending', 'ai_review', 'human_review'].includes(r.status)));
      setRecent(items.filter((r: any) => ['approved', 'rejected'].includes(r.status)).slice(0, 20));
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { loadData(); }, []);

  const handleAction = async (certId: string, action: string) => {
    setReviewing(certId); setMessage('');
    try {
      await api.certification.review(certId, action, comment);
      setMessage(action === 'approve' ? '认证已通过' : '已驳回');
      setComment('');
      await loadData();
    } catch (err: any) {
      setMessage('操作失败: ' + (err?.message || '未知错误'));
    } finally { setReviewing(null); }
  };

  if (loading) return <div className='text-slate-400 py-12 text-center'>加载认证数据中...</div>;

  const approved = recent.filter((r: any) => r.status === 'approved').length;
  const rejected = recent.filter((r: any) => r.status === 'rejected').length;

  return (
    <div>
      <div className='mb-6'>
        <h1 className='text-2xl font-bold text-slate-900'>认证审核</h1>
        <p className='text-sm text-slate-500 mt-1'>审核模式 → 审批/驳回决定一键生效</p>
        {message && <div className='mt-2 p-2 bg-blue-50 border border-blue-200 rounded-xl text-sm text-blue-700'>{message}</div>}
      </div>

      <div className='grid md:grid-cols-3 gap-4 mb-8'>
        <div className='bg-white border border-slate-200 rounded-2xl p-5 shadow-sm'>
          <div className='text-3xl font-bold text-amber-500'>{pending.length}</div>
          <div className='text-sm text-slate-500 mt-1'>待审核</div>
        </div>
        <div className='bg-white border border-slate-200 rounded-2xl p-5 shadow-sm'>
          <div className='text-3xl font-bold text-green-500'>{approved}</div>
          <div className='text-sm text-slate-500 mt-1'>已通过</div>
        </div>
        <div className='bg-white border border-slate-200 rounded-2xl p-5 shadow-sm'>
          <div className='text-3xl font-bold text-red-400'>{rejected}</div>
          <div className='text-sm text-slate-500 mt-1'>已驳回</div>
        </div>
      </div>

      {pending.length > 0 ? (
        <div className='mb-8'>
          <h2 className='text-lg font-semibold text-slate-900 mb-4'>待审核 ({pending.length})</h2>
          <div className='space-y-3'>
            {pending.map((rec: any) => {
              const s = STATUS_MAP[rec.status] || STATUS_MAP.pending;
              const StatusIcon = s.icon || Clock;
              return (
                <div key={rec.id} className='bg-white border border-slate-200 rounded-2xl p-5 shadow-sm'>
                  <div className='flex items-start justify-between mb-3'>
                    <div className='flex-1'>
                      <div className='flex items-center gap-2 mb-1'>
                        <span className='text-sm font-semibold text-slate-800'>{(rec.id || '').substring(0,12)}...</span>
                        <span className={'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ' + s.color}>{StatusIcon && <StatusIcon className='w-3 h-3' />}{s.label}</span>
                        <span className='text-xs text-slate-400'>{LEVEL_LABELS[rec.level] || rec.level}</span>
                      </div>
                      <div className='text-xs text-slate-500'>实体ID: {(rec.entity_id || '').substring(0,12)}... · 类型: {rec.entity_type} · 申请: {rec.applied_at ? new Date(rec.applied_at).toLocaleDateString('zh-CN') : '-'}</div>
                    </div>
                    <div className='flex gap-2 ml-4'>
                      <button onClick={() => handleAction(rec.id, 'approve')} disabled={reviewing === rec.id} className='px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700 disabled:opacity-50 flex items-center gap-1'><CheckCircle className='w-3.5 h-3.5' />通过</button>
                      <button onClick={() => handleAction(rec.id, 'reject')} disabled={reviewing === rec.id} className='px-3 py-1.5 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 disabled:opacity-50 flex items-center gap-1'><XCircle className='w-3.5 h-3.5' />驳回</button>
                    </div>
                  </div>
                  <div className='flex gap-2'>
                    <input value={comment} onChange={(e) => setComment((e.target as HTMLInputElement).value)} placeholder='审核意见（可选）...' className='flex-1 border border-slate-200 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-blue-400' />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className='bg-white border border-slate-200 rounded-2xl p-8 text-center mb-8 shadow-sm'>
          <ShieldCheck className='w-10 h-10 text-slate-300 mx-auto mb-3' />
          <p className='text-slate-500 text-sm'>暂无待审核的认证申请</p>
        </div>
      )}

      {recent.length > 0 && (
        <div>
          <h2 className='text-lg font-semibold text-slate-900 mb-4'>最近处理 ({recent.length})</h2>
          <div className='bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm'>
            <table className='w-full text-sm'>
              <thead className='bg-slate-50 border-b border-slate-200'>
                <tr>
                  <th className='text-left px-4 py-3 text-xs font-medium text-slate-500'>认证ID</th>
                  <th className='text-left px-4 py-3 text-xs font-medium text-slate-500'>类型</th>
                  <th className='text-left px-4 py-3 text-xs font-medium text-slate-500'>等级</th>
                  <th className='text-left px-4 py-3 text-xs font-medium text-slate-500'>状态</th>
                  <th className='text-left px-4 py-3 text-xs font-medium text-slate-500'>审核时间</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((rec: any) => {
                  const s = STATUS_MAP[rec.status] || STATUS_MAP.pending;
                  return (
                    <tr key={rec.id} className='border-b border-slate-100 last:border-0 hover:bg-slate-50'>
                      <td className='px-4 py-3 text-xs font-mono text-slate-600'>{(rec.id || '').substring(0,10)}...</td>
                      <td className='px-4 py-3 text-xs text-slate-600'>{rec.entity_type || '-'}</td>
                      <td className='px-4 py-3 text-xs text-slate-600'>{LEVEL_LABELS[rec.level] || rec.level}</td>
                      <td className='px-4 py-3'><span className={'inline-flex items-center gap-1 text-xs ' + s.color}>{s.icon && <s.icon className='w-3 h-3' />}{s.label}</span></td>
                      <td className='px-4 py-3 text-xs text-slate-400'>{rec.reviewed_at ? new Date(rec.reviewed_at).toLocaleDateString('zh-CN') : '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
