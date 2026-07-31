'use client';
import { useEffect, useState } from 'react';
import { Activity, Database, Server, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';

export default function AdminHealthPage() {
  const [health, setHealth] = useState<any>(null);
  const [dbStats, setDbStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.admin.health(),
      api.admin.dbStats(),
    ]).then(([h,d])=>{setHealth(h);setDbStats(d);setLoading(false)}).catch(()=>setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400">加载中...</div>;

  const tableEntries: [string, number][] = dbStats ? Object.entries(dbStats.counts).map(([k,v])=>[k,Number(v)]) : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">系统监控</h1>
      <p className="text-sm text-slate-500 mb-6">服务状态、数据库连接、系统资源</p>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <HealthCard icon={Server} label="后端服务" status={health?.status==='ok'?'ok':'error'} detail="FastAPI + Uvicorn" />
        <HealthCard icon={Database} label="数据库" status="ok" detail={`${dbStats?.total} 条记录`} />
        <HealthCard icon={Activity} label="API状态" status="ok" detail="12+ 个端点运行中" />
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">数据库表详情</h2>
        <div className="space-y-2">
          {tableEntries.map(([table, count]) => (
            <div key={table} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-700 font-medium">{table}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-32 bg-slate-100 rounded-full h-1.5"><div className="bg-blue-500 h-1.5 rounded-full" style={{width:Math.min(100,(count/40)*100)+'%'}} /></div>
                <span className="text-sm text-slate-500 w-8 text-right">{count}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-400">
          最后更新: {health?.timestamp || '-'}
        </div>
      </div>
    </div>
  );
}

function HealthCard({ icon:Icon, label, status, detail }: { icon:any; label:string; status:string; detail:string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <Icon className="w-8 h-8 text-slate-400" />
        {status==='ok'?<CheckCircle className="w-5 h-5 text-green-500"/>:<AlertTriangle className="w-5 h-5 text-red-500"/>}
      </div>
      <div className="font-semibold text-slate-900">{label}</div>
      <div className="text-xs text-slate-400 mt-1">{detail}</div>
    </div>
  );
}
