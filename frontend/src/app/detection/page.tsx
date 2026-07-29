'use client';
import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Shield, TrendingUp, AlertTriangle, Map, Target, BarChart3, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';

const LAYERS = [
  { id: 'identity', name: '身份与位置', icon: Shield, desc: '我在AI世界中是谁？在产业中排名如何？' },
  { id: 'opportunity', name: '机会雷达', icon: TrendingUp, desc: '未来12个月我能抓住什么？行业哪里在增长？' },
  { id: 'risk', name: '风险预警', icon: AlertTriangle, desc: '谁在超越我？什么趋势在威胁我？' },
  { id: 'roadmap', name: '行动路线', icon: Map, desc: '我该做什么？分几步走？' },
] as const;

type LayerType = typeof LAYERS[number]['id'];

export default function DetectionPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeLayer, setActiveLayer] = useState<LayerType>('identity');
  const router = useRouter();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data: any = await api.context.query(query.trim(), 5);
      if (data.results && data.results.length > 0) {
        router.push('/detection/result?id=' + data.results[0].id);
      } else {
        alert('未找到匹配结果，请尝试其他关键词');
      }
    } catch (e: any) {
      alert(e.message || '检测失败');
    } finally { setLoading(false); }
  };

  const LayerIcon = LAYERS.find(l=>l.id===activeLayer)?.icon || Shield;

  return (
    <div className='max-w-5xl mx-auto px-4 py-12'>
      {/* Hero */}
      <div className='text-center mb-12'>
        <h1 className='text-4xl font-bold text-gray-900 mb-4'>GEO 产业战略评估</h1>
        <p className='text-lg text-gray-500 max-w-2xl mx-auto'>
          不只是检测AI可见度。发现你在GEO产业生态中的位置、机会、风险与成长路径。
        </p>
      </div>

      {/* Search Bar */}
      <div className='flex items-center gap-3 bg-white border border-gray-300 rounded-2xl p-3 shadow-lg mb-12'>
        <Search className='w-5 h-5 text-gray-400 ml-3' />
        <input type='text' value={query} onChange={(e)=>setQuery(e.target.value)}
          onKeyDown={(e)=>e.key==='Enter'&&handleSearch()}
          placeholder='输入企业名称、个人姓名或行业关键词开始评估'
          className='flex-1 outline-none text-base py-3' />
        <button onClick={handleSearch} disabled={loading}
          className='bg-blue-600 text-white px-6 py-3 rounded-xl text-base font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors'>
          {loading ? '评估中...' : '开始评估'}
        </button>
      </div>

      {/* Quick examples */}
      <div className='text-center mb-12 text-sm text-gray-400'>
        试试：
        {['腾讯云','张三','杭州AI营销','大模型基础设施'].map(s=>(<button key={s} onClick={()=>setQuery(s)} className='text-blue-500 hover:underline mx-2'>{s}</button>))}
      </div>

      {/* Four Layers Tabs */}
      <div className='bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden'>
        {/* Tab bar */}
        <div className='flex border-b border-gray-100 overflow-x-auto'>
          {LAYERS.map(l=>{const Icon=l.icon; const active=activeLayer===l.id; return (<button key={l.id} onClick={()=>setActiveLayer(l.id)} className={'flex items-center gap-3 px-6 py-4 text-sm font-medium border-b-2 transition-colors flex-shrink-0 '+(active?'border-blue-600 text-blue-600 bg-blue-50/50':'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>{<Icon className='w-4 h-4' />}{l.name}</button>)})}
        </div>

        {/* Panel content */}
        <div className='p-8'>
          {activeLayer==='identity' && (<IdentityPanel />)}
          {activeLayer==='opportunity' && (<OpportunityPanel />)}
          {activeLayer==='risk' && (<RiskPanel />)}
          {activeLayer==='roadmap' && (<RoadmapPanel />)}
        </div>
      </div>
    </div>
  );
}

// ====== Identity Panel ======
function IdentityPanel() {
  return (<div className='space-y-6'>
    <div className='flex items-start gap-6'>
      <div className='w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold'>GEO</div>
      <div className='flex-1'>
        <h3 className='text-xl font-bold text-gray-900 mb-1'>GEO 数字身份</h3>
        <p className='text-sm text-gray-500 mb-3'>GEO-COMPANY-XXXXXXXX</p>
        <div className='flex gap-2 mb-4'>
          <span className='inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700'>🥇 L3 专业认证</span>
          <span className='inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700'>AI基础设施</span>
          <span className='inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700'>已认证</span>
        </div>
      </div>
    </div>
    <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
      {[{label:'行业排名',value:'Top 18%',color:'text-blue-600'},{label:'AI可见度',value:'78/100',color:'text-green-600'},{label:'信任度',value:'72/100',color:'text-purple-600'},{label:'影响力',value:'65/100',color:'text-amber-600'}].map(m=>(<div key={m.label} className='bg-gray-50 rounded-xl p-4 text-center'><div className={'text-2xl font-bold '+m.color}>{m.value}</div><div className='text-xs text-gray-500 mt-1'>{m.label}</div></div>))}
    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>输入企业名称后，系统将基于 Entity + Context Engine + Decision Engine 自动生成完整数字身份画像。</div>
  </div>)
}

// ====== Opportunity Panel ======
function OpportunityPanel() {
  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><TrendingUp className='w-5 h-5 text-green-500' />机会雷达</h3>
    <div className='grid gap-4'>
      {[{title:'AI搜索优化需求增长 230%',desc:'你所在行业的AI搜索曝光需求正在爆发。提前布局知识资产可抢占先发优势。',tag:'高优先级',color:'border-green-200 bg-green-50'},{title:'关键词空白区域发现',desc:'检测到3个未被竞品覆盖的高价值关键词区域。建议立即建立内容资产。',tag:'机会窗口',color:'border-blue-200 bg-blue-50'},{title:'竞争企业正在布局方向',desc:'头部企业过去90天大幅增加AI基础设施相关内容。建议评估自身能力差距。',tag:'需关注',color:'border-amber-200 bg-amber-50'}].map((item,i)=>(<div key={i} className={'border rounded-xl p-5 '+item.color}><div className='flex items-start justify-between mb-2'><span className='font-semibold text-gray-900'>{item.title}</span><span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-medium'>{item.tag}</span></div><p className='text-sm text-gray-600'>{item.desc}</p></div>))}
    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>机会雷达基于 Industry Benchmark + Trend Detection 模型持续分析产业链变化，每日更新。</div>
  </div>)
}

// ====== Risk Panel ======
function RiskPanel() {
  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><AlertTriangle className='w-5 h-5 text-red-500' />风险预警</h3>
    <div className='grid gap-4'>
      {[{title:'竞争企业A — AI曝光 +45%',desc:'过去90天竞品A的AI搜索曝光增长45%，你仅增长3%。差距持续扩大。',level:'高风险',color:'border-red-200 bg-red-50'},{title:'行业认证门槛提升',desc:'GEO行业正在形成认证标准。未获得认证的企业将逐渐失去AI搜索信任度。',level:'中风险',color:'border-amber-200 bg-amber-50'},{title:'自身退化预警',desc:'你的AI可见度已连续45天无增长。建议未来30天内补充行业案例、技术文档和专家背书。',level:'需关注',color:'border-yellow-200 bg-yellow-50'}].map((item,i)=>(<div key={i} className={'border rounded-xl p-5 '+item.color}><div className='flex items-start justify-between mb-2'><span className='font-semibold text-gray-900'>{item.title}</span><span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-bold'>{item.level}</span></div><p className='text-sm text-gray-600'>{item.desc}</p></div>))}
    </div>
    <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>风险预警基于 Risk Assessment Model + 产业情报系统持续监测，实时更新。</div>
  </div>)
}

// ====== Roadmap Panel ======
function RoadmapPanel() {
  return (<div className='space-y-6'>
    <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><Map className='w-5 h-5 text-blue-500' />行动路线</h3>
    <div className='space-y-4'>
      {[{phase:'阶段1',title:'补充数据资产',desc:'完善企业描述、产品能力、行业关系。当前完整度 72%，缺少3项关键证据。',time:'预计2周',icon:BarChart3},{phase:'阶段2',title:'获得行业认证',desc:'从L1基础认证开始，逐步升级到L3专业认证。认证将提升GEO信任度评分。',time:'预计4周',icon:Shield},{phase:'阶段3',title:'建立生态关系',desc:'通过产业导航找到上下游合作伙伴，建立供应链关系和行业生态连接。',time:'预计8周',icon:Target},{phase:'阶段4',title:'参与产业合作',desc:'通过交易市场发布需求或提供服务，参与GEO产业生态协作。',time:'持续进行',icon:ArrowRight}].map((item,i)=>(<div key={i} className='flex gap-4 items-start'><div className='w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0'><item.icon className='w-5 h-5 text-blue-600' /></div><div className='flex-1 border border-gray-200 rounded-xl p-4'><div className='flex items-center justify-between mb-1'><span className='font-semibold text-gray-900'>{item.phase}: {item.title}</span><span className='text-xs text-gray-400'>{item.time}</span></div><p className='text-sm text-gray-500'>{item.desc}</p></div></div>))}

          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/detection/result' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看评估报告</Link>
              <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>申请认证</Link>
              <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>补充企业数据</Link>
              <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>查看产业位置</Link>
            </div>
          </div>

    </div>
  </div>)
}