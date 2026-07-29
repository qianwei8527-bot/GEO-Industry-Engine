'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import PageHeader from '@/components/PageHeader';
import { Award, Database, FileText, TrendingUp } from 'lucide-react';
const sections = [
  { name: "AI Brand Ranking", desc: "GEO industry Alexa ranking", icon: Award, count: "1,247 entities", color: "from-blue-500 to-blue-600" },
  { name: "Industry Database", desc: "Browse companies, capabilities & relationships", icon: Database, count: "15 industries", color: "from-green-500 to-teal-500" },
  { name: "GEO Index", desc: "Industry-level score comparison & trends", icon: TrendingUp, count: "Real-time", color: "from-purple-500 to-pink-500" },
  { name: "Research Library", desc: "Reports, whitepapers, trend studies", icon: FileText, count: "0 documents", color: "from-amber-500 to-orange-500" },
];
export default function AssetsPage() {
  const [data, setData] = useState([] as any[]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.companies.list().then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <PageHeader icon={Database} title="GEO Data Asset Center" description="Accumulate industry knowledge, build digital assets" />
      <div className="grid md:grid-cols-2 gap-6">
        {sections.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.name} className="border border-gray-200 rounded-2xl overflow-hidden hover:shadow-md transition-all bg-white cursor-pointer group">
              <div className={"bg-gradient-to-r " + s.color + " p-4 flex items-center gap-3"}>
                <Icon className="w-8 h-8 text-white" />
                <div>
                  <h3 className="font-semibold text-white">{s.name}</h3>
                  <p className="text-xs text-white/80">{s.count}</p>
                </div>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-600">{s.desc}</p>
                <div className="flex items-center gap-2 mt-3">
                  <span className="text-xs text-blue-600 hover:underline">{'查看详情 →'}</span>
                </div>
              </div>
            </div>
          );
        })}
          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看评分影响</Link>
              <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>提交认证</Link>
              <Link href='/marketplace' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>展示服务</Link>
            </div>
          </div>
      </div>
    </div>
  );
}