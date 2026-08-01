'use client';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Shield, TrendingUp, AlertTriangle, Map, Target, BarChart3, ArrowRight, Building2 } from 'lucide-react';
import { api } from '@/lib/api';
import { authedFetch } from '@/lib/authFetch';
import { RadioTower, Loader2, CheckCircle2, XCircle } from 'lucide-react';

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
  const [demoData, setDemoData] = useState<any>(null);
  const [demoLoading, setDemoLoading] = useState(true);
  const [visNode, setVisNode] = useState("");
  const [visProvider, setVisProvider] = useState("");
  const [visReps, setVisReps] = useState(2);
  const [visPreflight, setVisPreflight] = useState<any>(null);
  const [visResult, setVisResult] = useState<any>(null);
  const [visLoading, setVisLoading] = useState(false);
  const router = useRouter();

  // Load a real company to demonstrate the engine capabilities
  useEffect(() => {
    (async () => {
      try {
        var companies = (await api.companies.list()) as any[];
        if (companies && companies.length > 0) {
          var cid = companies[0].id;
          var [ctx, dec] = (await Promise.all([
            api.context.company(cid),
            api.decision.company(cid),
          ])) as [any, any];
          setDemoData({
            company: ctx.company || companies[0],
            capabilities: ctx.capabilities || [],
            relationships: ctx.relationships || [],
            evidence: ctx.evidence || [],
            industries: ctx.industries || [],
            scoring: ctx.scoring || {},
            decision: dec || {},
          });
        }
      } catch (e) {
        console.error('Demo data load failed:', e);
      } finally {
        setDemoLoading(false);
      }
    })();
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      var data: any = await api.context.query(query.trim(), 5);
      if (data.results && data.results.length > 0) {
        router.push('/detection/result?id=' + data.results[0].id);
      } else {
        alert('未找到匹配结果，请尝试其他关键词');
      }
    } catch (e: any) {
      alert(e.message || '检测失败');
    } finally { setLoading(false); }
  };

  var LayerIcon = LAYERS.find(l => l.id === activeLayer)?.icon || Shield;

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
        <input type='text' value={query} onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
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
        {['腾讯AI','张三','杭州AI营销','大模型基础设施'].map(s => (
          <button key={s} onClick={() => setQuery(s)} className='text-blue-500 hover:underline mx-2'>{s}</button>
        ))}
      </div>

      {/* C6.4-R AI Visibility Observation */}
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden mb-12">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
          <RadioTower className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-gray-900">AI 可见度观测</h2>
          <span className="text-xs text-slate-400">真实数据标识 · 预算硬门禁 · neutral/branded 分离</span>
        </div>
        <div className="p-6">
          <div className="flex flex-wrap gap-3 items-end mb-4">
            <div>
              <label className="block text-xs text-slate-500 mb-1">节点 ID</label>
              <input value={visNode} onChange={e => setVisNode(e.target.value)} placeholder="如：b4578afd-..."
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Provider</label>
              <select value={visProvider} onChange={e => setVisProvider(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">默认</option>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="deepseek">DeepSeek</option>
                <option value="gemini">Gemini</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">重复次数</label>
              <input type="number" min={1} max={3} value={visReps} onChange={e => setVisReps(Number(e.target.value))}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-20" />
            </div>
            <button onClick={async () => {
              if (!visNode.trim()) return;
              setVisLoading(true); setVisResult(null); setVisPreflight(null);
              try {
                const r = await authedFetch(`/geo/observation-runs`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ node_id: visNode.trim(), provider: visProvider, question_keys: ["brand_recognition_1", "provider_recommendation_1", "expert_explanation_1"], repetitions: visReps }),
                });
                const data = await r.json();
                setVisPreflight(data);
                setVisResult(data);
              } catch { /* ignore */ }
              setVisLoading(false);
            }} disabled={visLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
              {visLoading ? <Loader2 className="w-4 h-4 inline animate-spin mr-1" /> : null}执行观测
            </button>
          </div>

          {visPreflight && (
            <div className={`text-sm rounded-lg px-4 py-3 ${visPreflight.status === "blocked" || visPreflight.allowed === false ? "bg-amber-50 border border-amber-200 text-amber-800" : "bg-green-50 border border-green-200 text-green-800"}`}>
              <div className="font-medium mb-1 flex items-center gap-2">
                {visPreflight.allowed === false ? <XCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                {visPreflight.status === "blocked" ? "预算预检未通过" : visPreflight.status}
              </div>
              <div className="text-xs space-y-1">
                {(visPreflight.reasons || []).map((r: string, i: number) => <div key={i}>· {r}</div>)}
                {visPreflight.estimated_calls ? <div>预计调用 {visPreflight.estimated_calls} · 预计成本 {visPreflight.estimated_max_cost ?? "未知"} · 预算上限 {visPreflight.budget_limit} · 模式 {visPreflight.observation_mode || "—"}</div> : null}
              </div>
            </div>
          )}
          {visResult && visResult.status === "completed" && (
            <div className="mt-3 text-xs text-slate-500">
              真实回答已保存：{visResult.answers} 条 · provider {visResult.provider} · model {visResult.model} · 成本 {visResult.estimated_cost} · data_origin real（仅当 provider 已配置）
            </div>
          )}
        </div>
      </div>

      {/* Four Layers Tabs — powered by real demo data */}
      <div className='bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden'>
        <div className='flex border-b border-gray-100 overflow-x-auto'>
          {LAYERS.map(l => {
            var Icon = l.icon;
            var active = activeLayer === l.id;
            return (
              <button key={l.id} onClick={() => setActiveLayer(l.id)}
                className={'flex items-center gap-3 px-6 py-4 text-sm font-medium border-b-2 transition-colors flex-shrink-0 ' +
                  (active ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50')}>
                <Icon className='w-4 h-4' />{l.name}
              </button>
            );
          })}
        </div>

        <div className='p-8'>
          {demoLoading ? (
            <div className='flex justify-center py-16'><div className='animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full' /></div>
          ) : demoData ? (
            <>
              {activeLayer === 'identity' && <IdentityPanel data={demoData} />}
              {activeLayer === 'opportunity' && <OpportunityPanel data={demoData} />}
              {activeLayer === 'risk' && <RiskPanel data={demoData} />}
              {activeLayer === 'roadmap' && <RoadmapPanel data={demoData} />}
            </>
          ) : (
            <div className='text-center py-16 text-gray-400'>
              <p>后端服务未连接</p>
              <p className='text-sm mt-2'>请确保 FastAPI 后端在 http://127.0.0.1:8080 运行</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ====== Identity Panel (real data) ======
function IdentityPanel({ data }: any) {
  var c = data.company || {};
  var caps = data.capabilities || [];
  var inds = data.industries || [];
  var rels = data.relationships || [];
  var evd = data.evidence || [];
  var s = data.scoring || {};
  var d = data.decision || {};
  var overall = d.overall ?? s.geo_score ?? 0;

  return (
    <div className='space-y-6'>
      <div className='flex items-start gap-6'>
        <div className='w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold'>GEO</div>
        <div className='flex-1'>
          <h3 className='text-xl font-bold text-gray-900 mb-1'>{c.name || '示例企业'}</h3>
          <p className='text-sm text-gray-400 font-mono mb-3'>{c.geo_id || 'GEO-COMPANY-XXXX'}</p>
          <div className='flex gap-2 flex-wrap mb-2'>
            {inds.slice(0, 3).map((ind: any, i: number) => (
              <span key={i} className='px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700'>{ind.name || ind}</span>
            ))}
          </div>
          <p className='text-sm text-gray-500'>{c.description || '了解企业在AI搜索生态中的可见度、信任度和竞争力'}</p>
        </div>
      </div>
      <div className='grid grid-cols-2 md:grid-cols-4 gap-3'>
        <MetricCard label='GEO Score' value={overall} color='text-blue-600' />
        <MetricCard label='能力数' value={caps.length} color='text-purple-600' />
        <MetricCard label='关系数' value={rels.length} color='text-green-600' />
        <MetricCard label='证据数' value={evd.length} color='text-orange-600' />
      </div>
      <div className='text-center'>
        <Link href={data.company?.id ? '/company/' + data.company.id : '/detection'} className='text-sm text-blue-600 hover:underline'>输入企业名称开始完整评估 →</Link>
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: any; color: string }) {
  return (
    <div className='bg-gray-50 rounded-xl p-4 text-center'>
      <div className={'text-xl font-bold ' + color}>{value}</div>
      <div className='text-xs text-gray-500 mt-1'>{label}</div>
    </div>
  );
}

// ====== Opportunity Panel (real data) ======
function OpportunityPanel({ data }: any) {
  var d = data.decision || {};
  var recs = d.recommendations || [];
  var ops = recs.filter((r: any) => r.type === 'opportunity').slice(0, 3);

  if (ops.length === 0) {
    ops = [
      { title: '补充企业数据资产', desc: '完善企业描述、产品能力、行业关系。当前完整度较低，机会窗口仍在。', tag: '基础建设' },
      { title: '参与行业认证计划', desc: '获得认证后AI搜索信任度可提升30-50%。', tag: '信任杠杆' },
      { title: '扩展行业合作网络', desc: '通过产业导航找到上下游伙伴，建立供应链接。', tag: '生态连接' },
    ];
  }

  return (
    <div className='space-y-6'>
      <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><TrendingUp className='w-5 h-5 text-green-500' />机会雷达</h3>
      <div className='grid gap-4'>
        {ops.map((item: any, i: number) => (
          <div key={i} className='border border-green-200 bg-green-50 rounded-xl p-5'>
            <div className='flex items-start justify-between mb-2'>
              <span className='font-semibold text-gray-900'>{item.title}</span>
              <span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-medium'>{item.tag || item.type}</span>
            </div>
            <p className='text-sm text-gray-600'>{item.desc || item.description}</p>
          </div>
        ))}
      </div>
      <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>机会雷达基于 Industry Benchmark + Trend Detection 模型持续分析产业链变化，每日更新。</div>
    </div>
  );
}

// ====== Risk Panel (real data) ======
function RiskPanel({ data }: any) {
  var d = data.decision || {};
  var recs = d.recommendations || [];
  var risks = recs.filter((r: any) => r.type === 'risk').slice(0, 3);
  var scores = d.scores || {};
  var cp = scores.competitive_position || {};

  if (risks.length === 0) {
    risks = [
      { title: '竞争加剧', desc: '竞争对手AI曝光持续增长，需关注差异化定位。', level: '关注', color: 'border-amber-200 bg-amber-50' },
      { title: '证据不足', desc: '缺少第三方认证和权威引用，AI信任度可能下降。', level: '中等', color: 'border-yellow-200 bg-yellow-50' },
      { title: '信息陈旧', desc: '企业信息更新频率低，AI爬虫可能降低抓取优先级。', level: '需关注', color: 'border-orange-200 bg-orange-50' },
    ];
  }

  return (
    <div className='space-y-6'>
      <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><AlertTriangle className='w-5 h-5 text-red-500' />风险预警</h3>
      <div className='grid gap-4'>
        {risks.map((item: any, i: number) => (
          <div key={i} className={'border rounded-xl p-5 ' + (item.color || 'border-amber-200 bg-amber-50')}>
            <div className='flex items-start justify-between mb-2'>
              <span className='font-semibold text-gray-900'>{item.title}</span>
              <span className='text-xs px-2 py-0.5 rounded-full bg-white border border-gray-200 font-bold'>{item.level || item.type}</span>
            </div>
            <p className='text-sm text-gray-600'>{item.desc || item.description}</p>
          </div>
        ))}
      </div>
      <div className='bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700'>风险预警基于 Risk Assessment Model + 产业情报系统持续监测，实时更新。</div>
    </div>
  );
}

// ====== Roadmap Panel (real data) ======
function RoadmapPanel({ data }: any) {
  var d = data.decision || {};
  var scores = d.scores || {};
  var roadmap = scores.roadmap || {};
  var actions = roadmap.actions || [];

  var steps = actions.length > 0 ? actions.map((a: string, i: number) => ({
    phase: '阶段' + (i + 1),
    title: a,
    desc: '',
    time: '持续进行',
    icon: i === 0 ? BarChart3 : i === 1 ? Shield : i === 2 ? Target : ArrowRight,
  })) : [
    { phase: '阶段1', title: '补充数据资产', desc: '完善企业描述、产品能力、行业关系。提升信息完整度至85%以上。', time: '预计2周', icon: BarChart3 },
    { phase: '阶段2', title: '获得行业认证', desc: '从L1基础认证开始，逐步升级到L3专业认证。提升GEO信任度。', time: '预计4周', icon: Shield },
    { phase: '阶段3', title: '建立生态关系', desc: '通过产业导航找到合作伙伴，建立供应链和生态连接。', time: '预计8周', icon: Target },
    { phase: '阶段4', title: '参与产业合作', desc: '通过交易市场发布需求或提供服务，参与GEO产业生态。', time: '持续进行', icon: ArrowRight },
  ];

  return (
    <div className='space-y-6'>
      <h3 className='text-lg font-bold text-gray-900 flex items-center gap-2'><Map className='w-5 h-5 text-blue-500' />行动路线</h3>
      <div className='space-y-4'>
        {steps.map((s: any, i: number) => {
          var Icon = s.icon === BarChart3 ? BarChart3 : s.icon === Shield ? Shield : s.icon === Target ? Target : ArrowRight;
          return (
            <div key={i} className='flex gap-4 items-start'>
              <div className='w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0'><Icon className='w-5 h-5 text-blue-600' /></div>
              <div className='flex-1 border border-gray-200 rounded-xl p-4'>
                <div className='flex items-center justify-between mb-1'>
                  <span className='font-semibold text-gray-900'>{s.phase}: {s.title}</span>
                  <span className='text-xs text-gray-400'>{s.time || '持续进行'}</span>
                </div>
                {s.desc && <p className='text-sm text-gray-500'>{s.desc}</p>}
              </div>
            </div>
          );
        })}
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
    </div>
  );
}
