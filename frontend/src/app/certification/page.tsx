'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import { Shield, User, Building2, Award, CheckCircle } from 'lucide-react';
const passportTypes = [
  { type: 'enterprise', label: '企业护照', icon: Building2, desc: '企业身份、能力、行业认证' },
  { type: 'individual', label: '个人护照', icon: User, desc: '个人专业技能、资历认证' },
  { type: 'service', label: '服务商护照', icon: Shield, desc: '服务能力、案例、信用评级' },
];
const levels = [
  { level: 'L1', label: '身份认证', desc: '基础身份信息验证', color: 'bg-gray-100 text-gray-700' },
  { level: 'L2', label: '能力认证', desc: '专业能力、技术水平证明', color: 'bg-blue-100 text-blue-700' },
  { level: 'L3', label: '行业认证', desc: '行业地位、影响力评估', color: 'bg-purple-100 text-purple-700' },
  { level: 'L4', label: '平台贡献', desc: '生态贡献、社区认可', color: 'bg-amber-100 text-amber-700' },
];
export default function CertificationPage() {
  const [companies, setCompanies] = useState([] as any[]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.companies.list().then((d: any) => { setCompanies(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="text-center mb-12">
        <Shield className="w-10 h-10 text-blue-500 mx-auto mb-3" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{'GEO 认证中心'}</h1>
        <p className="text-gray-500">{'每个参与者都有自己的 GEO 身份护照'}</p>
      </div>
      {/* Passport Types */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        {passportTypes.map((pt) => {
          const Icon = pt.icon;
          return (
            <Link key={pt.type} href={'/certification/passport/' + pt.type}
              className="border border-gray-200 rounded-2xl p-6 hover:border-blue-300 hover:shadow-md transition-all bg-white"
            >
              <Icon className="w-8 h-8 text-blue-500 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">{pt.label}</h3>
              <p className="text-sm text-gray-500">{pt.desc}</p>
            </Link>
          );
        })}
      </div>
      {/* Level System */}
      <div className="mb-12">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{'认证等级体系'}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {levels.map((l) => (
            <div key={l.level} className="border border-gray-200 rounded-xl p-4 text-center">
              <div className={'inline-block px-3 py-1 rounded-full text-xs font-semibold mb-2 ' + l.color}>{l.level}</div>
              <div className="font-medium text-gray-900 text-sm">{l.label}</div>
              <div className="text-xs text-gray-400 mt-1">{l.desc}</div>
            </div>
          ))}
        </div>
      </div>
      {/* CTA */}
      <div className="text-center">
        <Link href="/certification/apply"
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-blue-700"
        >
          <Award className="w-4 h-4" /> {'申请认证'}
        </Link>
        <p className="text-xs text-gray-400 mt-3">{'已通过认证的企业、个人、服务商将获得 GEO 信用标识'}</p>
          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/certification/apply' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>申请认证</Link>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看GEO状态</Link>
              <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>补充认证证据</Link>
            </div>
          </div>
      </div>
    </div>
  );
}