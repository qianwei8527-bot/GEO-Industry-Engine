'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ShieldCheck, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';

const STATUS_MAP: Record<string, { label: string; color: string; bg: string; icon: any }> = {
  pending: { label: '待审核', color: 'text-amber-600', bg: 'bg-amber-50', icon: Clock },
  ai_review: { label: 'AI初筛中', color: 'text-blue-600', bg: 'bg-blue-50', icon: ShieldCheck },
  human_review: { label: '人工复审中', color: 'text-purple-600', bg: 'bg-purple-50', icon: ShieldCheck },
  approved: { label: '已通过', color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle },
  rejected: { label: '已驳回', color: 'text-red-600', bg: 'bg-red-50', icon: XCircle },
  expired: { label: '已过期', color: 'text-gray-500', bg: 'bg-gray-50', icon: AlertTriangle },
  revoked: { label: '已撤销', color: 'text-red-600', bg: 'bg-red-50', icon: XCircle },
};

const LEVEL_LABELS: Record<string, string> = {
  L0: '未认证', L1: '基础身份认证', L2: 'GEO生态认证', L3: '专业能力认证', L4: '行业权威认证',
};

export default function ReviewStatusPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch all pending and recent certifications for review
    api.certification.list().then((d: any) => {
      const items = Array.isArray(d) ? d : d?.items || [];
      setRecords(items);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className='max-w-4xl mx-auto px-4 py-20 text-center text-slate-400'>加载认证记录中...</div>;

  return (
    <div className='max-w-4xl mx-auto px-4 py-10'>
      <div className='mb-8'>
        <h1 className='text-2xl font-bold text-gray-900 mb-1'>认证审核状态</h1>
        <p className='text-sm text-gray-500'>查看已提交的认证申请及其审核进度</p>
      </div>

      {records.length === 0 ? (
        <div className='bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm'>
          <ShieldCheck className='w-12 h-12 text-slate-300 mx-auto mb-4' />
          <p className='text-slate-500'>暂无认证记录</p>
          <Link href='/certification/apply' className='inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700'>去申请认证</Link>
        </div>
      ) : (
        <div className='space-y-3'>
          {records.map((rec: any, i: number) => {
            const statusInfo = STATUS_MAP[rec.status] || STATUS_MAP.pending;
            const StatusIcon = statusInfo.icon || Clock;
            return (
              <div key={rec.id || i} className='bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow'>
                <div className='flex items-start justify-between mb-3'>
                  <div>
                    <div className='text-sm font-semibold text-slate-800'>认证ID: {(rec.id || '').substring(0, 12)}...</div>
                    <div className='text-xs text-slate-400 mt-0.5'>实体ID: {(rec.entity_id || '').substring(0, 12)}... · 类型: {rec.entity_type || '-'}</div>
                  </div>
                  <span className={'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ' + statusInfo.bg + ' ' + statusInfo.color}>
                    <StatusIcon className='w-3.5 h-3.5' />
                    {statusInfo.label}
                  </span>
                </div>
                <div className='flex flex-wrap gap-4 text-xs text-slate-500'>
                  <span>等级: {LEVEL_LABELS[rec.level] || rec.level}</span>
                  <span>类型: {rec.cert_type || '-'}</span>
                  <span>申请时间: {rec.applied_at ? new Date(rec.applied_at).toLocaleDateString('zh-CN') : '-'}</span>
                  {rec.issued_at && <span>颁发时间: {new Date(rec.issued_at).toLocaleDateString('zh-CN')}</span>}
                  {rec.expires_at && <span>有效期至: {new Date(rec.expires_at).toLocaleDateString('zh-CN')}</span>}
                </div>
                {rec.review_comment && <div className='mt-3 p-3 bg-slate-50 rounded-lg text-xs text-slate-600'>{rec.review_comment}</div>}
              </div>
            );
          })}
        </div>
      )}

      <div className='mt-8 flex gap-3 justify-center'>
        <Link href='/certification/apply' className='px-4 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700'>新申请</Link>
        <Link href='/certification' className='px-4 py-2 border border-gray-300 rounded-xl text-sm hover:bg-gray-50'>返回认证中心</Link>
      </div>
    </div>
  );
}
