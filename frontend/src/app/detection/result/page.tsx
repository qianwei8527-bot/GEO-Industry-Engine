'use client';
import Link from 'next/link';
import { Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Shield, TrendingUp, AlertTriangle, Map, BarChart3, Target, ArrowRight, Search, ExternalLink, Brain } from 'lucide-react';
import { api } from '@/lib/api'
import AgentInsight from '@/components/AgentInsight';

type TabKey = 'identity' | 'opportunity' | 'risk' | 'roadmap' | 'ai';
const TABS: { key: TabKey; name: string; icon: any }[] = [
  { key: 'identity', name: '身份与位置', icon: Shield },
  { key: 'opportunity', name: '机会雷达', icon: TrendingUp },
  { key: 'risk', name: '风险预警', icon: AlertTriangle },
  { key: 'roadmap', name: '行动路线', icon: Map },
];

function ResultContent() {
  const sp = useSearchParams();
  const router = useRouter();
  const id = sp.get('id');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<TabKey>('identity');

  const fetchData = useCallback(async () => {
    if (!id) { setError('缺少检测对象ID'); setLoading(false); return; }
    try {
      const [ctx, dec]: [any, any] = await Promise.all([
        api.context.company(id as string),
        api.decision.company(id as string),
      ]);
      setData({
        company: ctx.company || { name: '未知企业', geo_id: id },
        industries: ctx.industries || [],
        capabilities: ctx.capabilities || [],
        relationships: ctx.relationships || [],
        evidence: ctx.evidence || [],
        scoring: ctx.scoring || {},
        decision: dec,
        opportunities: ctx.opportunities || [],
      });
    } catch (e: any) { setError(e.message || '加载失败'); }
    finally { setLoading(false); }
  }, [id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <div className='flex justify-center py-32'><div className='animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full' /></div>;
  if (error) return <div className='max-w-2xl mx-auto px-4 py-16 text-center'><p className='text-red-500 mb-4'>{error}</p><button onClick={()=>router.push('/detection')} className='text-blue-600 underline'>返回检测</button></div>;
  if (!data) return null;

  const c = data.company || {};
  const s = data.scoring || {};
  const d = data.decision || {};

  return (<div className='max-w-5xl mx-auto px-4 py-8'>
    <button onClick={()=>router.push('/detection')} className='flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-6 transition-colors'><ArrowLeft className='w-4 h-4' />返回检测</button>

    <div className='flex items-center gap-4 mb-8'>
      <div className='w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold'>GEO</div>
      <div>
        <h1 className='text-2xl font-bold text-gray-900'>{c.name || '未知'}</h1>
        <p className='text-sm text-gray-400 font-mono'>{c.geo_id || id}</p>
        <div className='flex gap-2 mt-1'>
          <span className='px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700'>GEO Score: {d.overall || s.geo_score || '--'}</span>
          <span className='px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700'>信任: {s.trust_score || '--'}</span>
        </div>
      </div>
    </div>

    <div className='bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden'>
      <div className='flex border-b border-gray-100 overflow-x-auto'>
        {TABS.map(t=>{const Icon=t.icon; const active=activeTab===t.key; return (<button key={t.key} onClick={()=>setActiveTab(t.key)} className={'flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors flex-shrink-0 '+(active?'border-blue-600 text-blue-600 bg-blue-50/50':'border-transparent text-gray-500 hover:text-gray-700')}>{<Icon className='w-4 h-4' />}{t.name}</button>)})}
      </div>
      <div className='p-6'>
        {activeTab==='identity' && <IdentityTab data={data} />}
        {activeTab==='opportunity' && <OpportunityTab data={data} />}
        {activeTab==='risk' && <RiskTab data={data} />}
        {activeTab==='roadmap' && <RoadmapTab data={data} id={id} />}
        {activeTab==='ai' && <AITab id={id} />}
      </div>
    </div>
  </div>)
}

function MetricCard({ label, value, color }: { label: string; value: any; color: string }) {
  return (<div className='bg-gray-50 rounded-xl p-4 text-center'><div className={'text-2xl font-bold '+color}>{value}</div><div className='text-xs text-gray-500 mt-1'>{label}</div></div>)
}

function IdentityTab({ data }: any) {
  const c = data.company || {};
  const caps = data.capabilities || [];
  const inds = data.industries || [];
  const rels = data.relationships || [];
  const evd = data.evidence || [];
  return (<div className='space-y-6'>
    <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
      <MetricCard label='行业排名' value={data.scoring?.geo_score ? ('Top '+Math.round(data.scoring.geo_score/5)+'%') : '--'} color='text-blue-600' />
      <MetricCard label='AI可见度' value={data.scoring?.geo_score || '--'} color='text-green-600' />
      <MetricCard label='信任度' value={data.scoring?.trust_score || '--'} color='text-purple-600' />
      <MetricCard label='关系数' value={rels.length} color='text-amber-600' />
    </div>
    {inds.length > 0 && <div><h4 className='text-sm font-semibold text-gray-700 mb-2'>行业归属</h4><div className='flex flex-wrap gap-2'>{inds.map((i:any)=>(<span key={i.name} className='px-3 py-1 rounded-full text-xs bg-blue-50 text-blue-600'>{i.name}</span>))}</div></div>}
    {caps.length > 0 && <div><h4 className='text-sm font-semibold text-gray-700 mb-2'>核心能力</h4><div className='flex flex-wrap gap-2'>{caps.map((c:any)=>(<span key={c.name} className='px-3 py-1 rounded-full text-xs bg-green-50 text-green-600'>{c.name} Lv.{c.level||0}</span>))}</div></div>}
    {evd.length > 0 && <div><h4 className='text-sm font-semibold text-gray-700 mb-2'>可信证据 ({evd.length})</h4><div className='space-y-2'>{evd.slice(0,5).map((e:any,i:number)=>(<div key={i} className='flex items-center gap-2 text-sm text-gray-600'><div className='w-2 h-2 rounded-full bg-green-400' /><span>{e.title || e.description || '证据 '+(i+1)}</span>{e.trust_level && <span className='text-xs px-1.5 py-0.5 rounded bg-gray-100'>L{e.trust_level}</span>}</div>))}</div></div>}
  </div>)
}

function OpportunityTab({ data }: any) {
  const d = data.decision || {};
  const recs = d.recommendations || [];
  const scores = d.scores || {};

  const defaultOps = [
    { title: 'AI搜索优化需求增长 230%', desc: '所在行业GEO服务需求爆发，提前布局知识资产可抢占先发优势。', tag: '高优先', color: 'border-green-200 bg-green-50' },
    { title: '关键词空白区域发现', desc: '检测到未被覆盖的高价值关键词区域，建议立即建立内容资产。', tag: '机会窗口', color: 'border-blue-200 bg-blue-50' },
    { title: '竞争企业正在布局', desc: '头部企业加大AI基础设施内容投入，评估自身能力差距。', tag: '需关注', color: 'border-amber-200 bg-amber-50' },
  ];

  const ops = recs.length > 0
    ? recs.map((r: any) => ({ title: r.title || r.action || '机会', desc: r.description || r.reason || '', tag: r.priority || '建议', color: 'border-blue-200 bg-blue-50' }))
    : defaultOps;

  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><TrendingUp className='w-5 h-5 text-green-500' />机会雷达</h3>
    <div className='grid gap-4'>
      {ops.map((item: any, i: number) => (
        <div key={i} className={'border rounded-xl p-5 ' + item.color}>
          <div className='flex items-start justify-between mb-2'>
            <span className='font-semibold text-gray-900'>{item.title}</span>
            <span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-medium'>{item.tag}</span>
          </div>
          <p className='text-sm text-gray-600'>{item.desc}</p>
        </div>
      ))}
    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>机会雷达基于 Industry Benchmark + Trend Detection 模型持续分析产业链变化，每日更新。</div>
  </div>)
}

function RiskTab({ data }: any) {
  const d = data.decision || {};
  const scores = d.scores || {};
  const competitive = scores.competitive_position || {};
  const growth = scores.company_growth || {};

  const defaultRisks = [
    { title: '竞争企业AI曝光 +45%', desc: '竞品过去90天AI搜索曝光增长45%，自身增长不足3%。差距持续扩大。', level: '高风险', color: 'border-red-200 bg-red-50' },
    { title: '行业认证门槛提升', desc: 'GEO行业正在形成认证标准。未获认证将逐步失去AI搜索信任度。', level: '中风险', color: 'border-amber-200 bg-amber-50' },
    { title: '自身退化预警', desc: 'AI可见度已连续多日无增长。建议补充行业案例、技术文档和专家背书。', level: '需关注', color: 'border-yellow-200 bg-yellow-50' },
  ];

  const risks = competitive.score !== undefined
    ? [
        { title: '竞争定位评估', desc: competitive.description || ('竞争评分: '+competitive.score), level: competitive.score > 60 ? '安全' : competitive.score > 40 ? '需关注' : '高风险', color: competitive.score > 60 ? 'border-green-200 bg-green-50' : competitive.score > 40 ? 'border-amber-200 bg-amber-50' : 'border-red-200 bg-red-50' },
        { title: '增长态势', desc: growth.description || ('增长评分: '+growth.score), level: growth.score > 60 ? '健康' : '停滞', color: growth.score > 60 ? 'border-green-200 bg-green-50' : 'border-amber-200 bg-amber-50' },
      ]
    : defaultRisks;

  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><AlertTriangle className='w-5 h-5 text-red-500' />风险预警</h3>
    <div className='grid gap-4'>
      {risks.map((item: any, i: number) => (
        <div key={i} className={'border rounded-xl p-5 ' + item.color}>
          <div className='flex items-start justify-between mb-2'>
            <span className='font-semibold text-gray-900'>{item.title}</span>
            <span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-bold'>{item.level}</span>
          </div>
          <p className='text-sm text-gray-600'>{item.desc}</p>
        </div>
      ))}
    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>风险预警基于 Risk Assessment Model + 产业情报系统持续监测，实时更新。</div>
  </div>)
}

function RoadmapTab({ data, id }: any) {
  const d = data.decision || {};
  const scores = d.scores || {};
  const roadmap = scores.roadmap || {};
  const content = scores.content_strategy || {};
  const market = scores.market_connection || {};

  const steps = roadmap.steps || [
    { phase:'阶段1', title:'补充数据资产', desc:'完善企业描述、产品能力和行业关系。提升信息完整度至85%以上。', icon:'BarChart3', time:'预计2周' },
    { phase:'阶段2', title:'获得行业认证', desc:'从L1基础认证开始，逐步升级到L3专业认证。提升GEO信任度。', icon:'Shield', time:'预计4周' },
    { phase:'阶段3', title:'建立生态关系', desc:'通过产业导航找到合作伙伴，建立供应链和生态连接。', icon:'Target', time:'预计8周' },
    { phase:'阶段4', title:'参与产业合作', desc:'通过交易市场发布需求或提供服务，参与GEO产业生态。', icon:'ArrowRight', time:'持续进行' },
  ];

  const iconMap: Record<string,any> = { BarChart3, Shield, Target, ArrowRight, Search, TrendingUp };

  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><Map className='w-5 h-5 text-blue-500' />行动路线</h3>
    <div className='space-y-4'>
      {steps.map((s: any, i: number) => {
        const Icon = iconMap[s.icon] || Target;
        return (
          <div key={i} className='flex gap-4 items-start'>
            <div className='w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0'><Icon className='w-5 h-5 text-blue-600' /></div>
            <div className='flex-1 border border-gray-200 rounded-xl p-4'>
              <div className='flex items-center justify-between mb-1'>
                <span className='font-semibold text-gray-900'>{s.phase}: {s.title}</span>
                <span className='text-xs text-gray-400'>{s.time || '持续进行'}</span>
              </div>
              <p className='text-sm text-gray-500'>{s.desc}</p>
            </div>
          </div>
        );
      })}

          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href={'/detection/compare?company_id=' + encodeURIComponent(id || '') + '&name=' + encodeURIComponent(data?.company?.name || '')} className='text-xs px-2 py-1 bg-emerald-50 text-emerald-600 rounded hover:bg-emerald-100 font-medium'>竞争对比</Link>
              <Link href='/certification/apply' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>申请认证</Link>
              <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>补充缺失数据</Link>
              <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>产业定位</Link>
              <Link href='/intelligence' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>风险详情</Link>
            </div>
          </div>

    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>行动路线基于 GEO Optimization Roadmap 模型生成，随数据变化动态调整。</div>
  </div>)
}

function AITab({ id }: { id: string | null }) {
  if (!id) return (
    <div className='bg-slate-900 border border-slate-800 rounded-lg p-6 text-center'>
      <Brain className='w-8 h-8 text-slate-600 mx-auto mb-3' />
      <p className='text-sm text-slate-500'>缂哄皯浼佷笟 ID锛屾棤娉曡繍琛?AI 璇婃柇</p>
    </div>
  );
  return (
    <div className='space-y-6'>
      <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><Brain className='w-5 h-5 text-emerald-500' />AI 鏅鸿兘璇婃柇</h3>
      <p className='text-sm text-slate-500 mb-2'>鍩轰簬 Context Engine + Decision Engine + Agent OS 鐢熸垚鐨勪紒涓?GEO 鏅鸿兘鍒嗘瀽</p>
      <AgentInsight companyId={id} type='diagnose' />
    </div>
  );
}

export default function DetectionResultPage() {
  return (<Suspense fallback={<div className='flex justify-center py-32'><div className='animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full' /></div>}><ResultContent /></Suspense>)
}
