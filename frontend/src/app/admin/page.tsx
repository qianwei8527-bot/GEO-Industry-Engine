'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { LayoutDashboard, Sliders, Building2, Factory, ShieldCheck, Activity, TrendingUp, Database, FileText, Users } from 'lucide-react';

interface SystemStats { counts: Record<string,number>; total: number; timestamp: string }
interface ConfigStats { total_configs: number; categories: number; version: string }
interface ConfigMap { [cat: string]: string[] }

export default function AdminDashboard() {
  const [dbStats, setDbStats] = useState<SystemStats | null>(null);
  const [configStats, setConfigStats] = useState<ConfigStats | null>(null);
  const [configs, setConfigs] = useState<ConfigMap>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.admin.dbStats(),
      api.admin.stats(),
      api.admin.listConfigs(),
    ]).then(([db, cfg, cfgs]) => {
      setDbStats(db);
      setConfigStats(cfg);
      setConfigs(cfgs);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400">������...</div>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">GEO ����̨</h1>
        <p className="text-sm text-slate-500 mt-1">ϵͳ���á����ݹ�������Ӫ�������</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Database} label="��������" value={String(dbStats?.total ?? 0)} color="text-blue-500" bg="bg-blue-50" />
        <StatCard icon={FileText} label="�����ļ�" value={String(configStats?.total_configs ?? 0)} color="text-green-500" bg="bg-green-50" />
        <StatCard icon={Building2} label="��ҵʵ��" value={String(dbStats?.counts.companies ?? 0)} color="text-purple-500" bg="bg-purple-50" />
        <StatCard icon={ShieldCheck} label="�����" value="0" color="text-amber-500" bg="bg-amber-50" />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <QuickCard href="/admin/config" icon={Sliders} title="���ù���" desc={`${configStats?.categories ?? 0} �����࣬${configStats?.total_configs ?? 0} �� YAML �ļ�`} color="blue" />
        <QuickCard href="/admin/companies" icon={Building2} title="��ҵ����" desc={`${dbStats?.counts.companies ?? 0} �ҹ�˾��${dbStats?.counts.entities ?? 0} ��ʵ��`} color="purple" />
        <QuickCard href="/admin/industries" icon={Factory} title="��ҵ����" desc={`${dbStats?.counts.industries ?? 0} ����ҵ����`} color="green" />
      </div>

      {/* DB Table Overview */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">���ݿ������</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {dbStats && Object.entries(dbStats.counts).map(([table, count]) => (
            <div key={table} className="border border-slate-100 rounded-xl p-3 bg-slate-50">
              <div className="text-xs text-slate-400 mb-1">{table}</div>
              <div className="text-xl font-bold text-slate-800">{String(count)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Config Categories */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">���÷���</h2>
          <Link href="/admin/config" className="text-sm text-blue-600 hover:underline">����ȫ��</Link>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          {Object.entries(configs).map(([cat, files]) => (
            <div key={cat} className="border border-slate-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-2 capitalize">{cat}</h3>
              <div className="space-y-1">
                {files.map(f => (
                  <Link key={f} href={`/admin/config?cat=${cat}&file=${f.replace('.yaml','')}`}
                    className="block text-xs text-blue-600 hover:underline truncate">
                    {f.replace('.yaml','')}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon:Icon, label, value, color, bg }: { icon:any; label:string; value:string; color:string; bg:string }) {
  return <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
    <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mb-3`}>
      <Icon className={`w-5 h-5 ${color}`} />
    </div>
    <div className="text-2xl font-bold text-slate-900">{value}</div>
    <div className="text-sm text-slate-500">{label}</div>
  </div>;
}

function QuickCard({ href, icon:Icon, title, desc, color }: { href:string; icon:any; title:string; desc:string; color:string }) {
  const borderMap: Record<string,string> = { blue:'border-blue-200 hover:border-blue-400', purple:'border-purple-200 hover:border-purple-400', green:'border-green-200 hover:border-green-400' };
  const bgMap: Record<string,string> = { blue:'bg-blue-50', purple:'bg-purple-50', green:'bg-green-50' };
  return <Link href={href} className={`block bg-white border ${borderMap[color] || 'border-slate-200'} rounded-2xl p-5 shadow-sm transition-colors`}>
    <div className={`w-10 h-10 ${bgMap[color] || 'bg-slate-50'} rounded-xl flex items-center justify-center mb-3`}>
      <Icon className={`w-5 h-5 text-${color}-500`} />
    </div>
    <h3 className="font-semibold text-slate-900 mb-1">{title}</h3>
    <p className="text-xs text-slate-500">{desc}</p>
  </Link>;
}
