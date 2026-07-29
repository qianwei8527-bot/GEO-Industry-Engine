'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import PageHeader from '@/components/PageHeader';
import { BookOpen, Briefcase, MessageSquare, ShoppingCart, Users, Wrench } from 'lucide-react';
const categories = [
  { name: "Services", icon: Briefcase, desc: "GEO optimization, content strategy, data analysis", items: 0, color: "border-l-blue-500" },
  { name: "Tools", icon: Wrench, desc: "AI detection, scoring, monitoring tools", items: 0, color: "border-l-green-500" },
  { name: "Data", icon: BookOpen, desc: "Industry data, competitive analysis, market reports", items: 0, color: "border-l-purple-500" },
  { name: "Knowledge", icon: Users, desc: "Training, courses, consulting", items: 0, color: "border-l-amber-500" },
  { name: "Talent", icon: MessageSquare, desc: "GEO experts, project managers, engineers", items: 0, color: "border-l-red-500" },
];
export default function MarketplacePage() {
  const [data, setData] = useState([] as any[]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.companies.list().then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <PageHeader icon={ShoppingCart} title="GEO Trading Marketplace" description="Connect, transact, close the value loop" />
      <div className="grid md:grid-cols-2 gap-6">
        {categories.map((cat) => {
          const Icon = cat.icon;
          return (
            <div key={cat.name} className={"border border-gray-200 border-l-4 rounded-2xl p-6 hover:shadow-md transition-all bg-white cursor-pointer " + cat.color}>
              <div className="flex items-center gap-3 mb-3">
                <Icon className="w-8 h-8 text-gray-500" />
                <div>
                  <h3 className="font-semibold text-gray-900">{cat.name}</h3>
                  <p className="text-xs text-gray-400">{cat.items} listings</p>
                </div>
              </div>
              <p className="text-sm text-gray-500">{cat.desc}</p>
              <div className="mt-4 flex gap-2">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">Browse</span>
                <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">Post Request</span>
              </div>
            </div>
          );
        })}
      </div>
      <div className="text-center mt-8">
        <button className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700">
          <MessageSquare className="w-4 h-4" /> Post a Request
        </button>
          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看服务商认证</Link>
              <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>产业关系图</Link>
            </div>
          </div>
      </div>
    </div>
  );
}