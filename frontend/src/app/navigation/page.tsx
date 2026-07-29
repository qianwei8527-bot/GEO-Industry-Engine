'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import { Compass, Layers, Globe, TrendingUp, Map, ArrowRight } from 'lucide-react';
const MAPS = [
  { id: 'ecosystem', name: '产业生态地图', desc: '9层GEO产业价值链全景', icon: 'Layers', layers: ['需求层','内容层','知识工程层','AI平台层','数据智能层','服务交付层','交易市场层','认证层','教育层'], color:'blue' },
  { id: 'business', name: '商业赚钱地图', desc: '谁买单 x 买什么 x 谁供货', icon: 'TrendingUp', layers: ['企业','个人','投资机构','政府园区'], color:'green' },
  { id: 'operation', name: '运营流程地图', desc: '8阶段GEO增长飞轮', icon: 'Map', layers: ['诊断','策略','知识建设','内容生产','发布分发','监测','优化','复购'], color:'purple' },
  { id: 'regional', name: '地域生态地图', desc: '产业地理分布与区域资源视图', icon: 'Globe', layers: ['华北','华东','华南','西南','港澳台','海外'], color:'amber' },
  { id: 'direction', name: '发展方向地图', desc: '未来趋势三线预测', icon: 'Compass', layers: ['技术路线','市场机会','生态演化'], color:'red' },
];
const iconMap: Record<string,any> = { Layers, TrendingUp, Map, Globe, Compass };
const colorMap: Record<string,string> = { blue: 'bg-blue-50 text-blue-600', green: 'bg-green-50 text-green-600', purple: 'bg-purple-50 text-purple-600', amber: 'bg-amber-50 text-amber-600', red: 'bg-red-50 text-red-600' };
export default function NavigationPage() {
  const [data, setData] = useState([] as any[]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.companies.list().then((d: any) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  return (
    <div className='max-w-7xl mx-auto px-4 py-10'>
      <div className='text-center mb-12'>
        <Compass className='w-10 h-10 text-blue-500 mx-auto mb-3' />
        <h1 className='text-4xl font-bold text-gray-900 mb-3'>GEO 产业导航</h1>
        <p className='text-lg text-gray-500 max-w-2xl mx-auto'>五张地图，一个入口。微观看清自己，宏观看懂产业。每个地图支持节点展示、关系探索和AI分析。</p>
      </div>
      <div className='grid md:grid-cols-2 lg:grid-cols-3 gap-6'>
        {MAPS.map((m) => {
          const Icon = iconMap[m.icon];
          const colorCls = colorMap[m.color] || 'bg-gray-50 text-gray-600';
          return (
            <div key={m.id} className='border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-all bg-white cursor-pointer group'>
              <div className='flex items-start justify-between mb-4'>
                <div className={'w-12 h-12 rounded-xl flex items-center justify-center '+colorCls.split(' ')[0]}>
                  {Icon && <Icon className='w-6 h-6' />}
                </div>
                <ArrowRight className='w-5 h-5 text-gray-300 group-hover:text-gray-500 transition-colors' />
              </div>
              <h3 className='font-bold text-lg text-gray-900 mb-1'>{m.name}</h3>
              <p className='text-sm text-gray-500 mb-4'>{m.desc}</p>
              <div className='flex flex-wrap gap-1.5 mb-4'>
                {m.layers.map((l:string) => (<span key={l} className='text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600'>{l}</span>))}
              </div>
              <div className='flex gap-2 pt-3 border-t border-gray-100'>
                <span className='text-xs px-3 py-1 rounded-lg bg-blue-50 text-blue-600 font-medium'>探索</span>
                <span className='text-xs px-3 py-1 rounded-lg bg-green-50 text-green-600 font-medium'>AI分析</span>
              </div>
            </div>
          );
        })}
          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看企业详情</Link>
              <Link href='/marketplace' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>发现交易机会</Link>
              <Link href='/intelligence' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>行业趋势</Link>
            </div>
          </div>
      </div>
    </div>
  );
}