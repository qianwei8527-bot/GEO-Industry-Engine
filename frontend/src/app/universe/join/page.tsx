"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Building2, MapPin, Boxes, FileCheck2, Target, Rocket, ArrowLeft,
  ArrowRight, Save, Loader2, CheckCircle2, AlertCircle, Sparkles,
  Plus, Trash2, Info, Globe, Shield, Clock, ChevronRight,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const STEP_META = [
  { key: "identity", label: "企业身份", icon: Building2 },
  { key: "industry", label: "行业位置", icon: MapPin },
  { key: "capabilities", label: "产品与能力", icon: Boxes },
  { key: "evidence", label: "证据与背书", icon: FileCheck2 },
  { key: "goals", label: "目标与问题", icon: Target },
  { key: "confirm", label: "确认与激活", icon: Rocket },
];

export default function JoinPage() {
    const [authChecked, setAuthChecked] = useState(false);
  const [authOk, setAuthOk] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("geo_token");
    if (!token) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; }
    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (!r.ok) { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); return; } setAuthOk(true); setAuthChecked(true); })
      .catch(() => { window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); });
  }, []);

const [step, setStep] = useState(0);
  const [config, setConfig] = useState<any>(null);
  const [industries, setIndustries] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [data, setData] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [activating, setActivating] = useState(false);
  const [validation, setValidation] = useState<any>(null);
  const [activation, setActivation] = useState<any>(null);
  const [error, setError] = useState("");
  const [savedAt, setSavedAt] = useState("");
  const [dirty, setDirty] = useState(false);

  // Load config + industries
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/universe/onboarding/config`).then(r => r.json()),
      fetch(`${API_BASE}/industries/`).then(r => r.json()).catch(() => []),
    ]).then(([cfg, inds]) => {
      setConfig(cfg);
      setIndustries(Array.isArray(inds) ? inds : (inds.industries || []));
      // Create draft session
      const key = `join-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      fetch(`${API_BASE}/universe/onboarding`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idempotency_key: key }),
      }).then(r => r.json()).then(s => setSessionId(s.session_id)).catch(() => setError("无法创建入驻会话"));
    }).catch(() => setError("无法加载入驻配置"));
  }, []);

  const saveDraft = useCallback(async (nextData: any, nextStep: number) => {
    if (!sessionId) return;
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/universe/onboarding/${sessionId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: nextData, current_step: nextStep + 1 }),
      });
      if (res.ok) {
        setSavedAt(new Date().toLocaleTimeString());
        setDirty(false);
      }
    } catch { /* autosave is best-effort */ }
    setSaving(false);
  }, [sessionId]);

  const update = (key: string, value: any) => {
    const next = { ...data, [key]: value };
    setData(next);
    setDirty(true);
    // Debounced autosave
    window.clearTimeout((window as any).__joinSaveTimer);
    (window as any).__joinSaveTimer = window.setTimeout(() => saveDraft(next, step), 800);
  };

  const next = async () => {
    if (step === 5) return;
    await saveDraft(data, step + 1);
    setStep(step + 1);
    setValidation(null);
  };

  const prev = () => {
    if (step === 0) return;
    setStep(step - 1);
    setValidation(null);
  };

  const handleValidate = async () => {
    if (!sessionId) return;
    setValidating(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/universe/onboarding/${sessionId}/validate`, { method: "POST" });
      const v = await res.json();
      setValidation(v);
    } catch (e: any) { setError(e.message || "校验失败"); }
    setValidating(false);
  };

  const handleActivate = async () => {
    if (!sessionId) return;
    setActivating(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/universe/onboarding/${sessionId}/activate`, { method: "POST" });
      const result = await res.json();
      setActivation(result);
      if (result.activation_status === "completed" && result.home_url) {
        setTimeout(() => { window.location.href = result.home_url; }, 1800);
      } else if (result.activation_status === "failed") {
        setError(result.error || "激活失败，请重试");
      }
    } catch (e: any) { setError(e.message || "激活失败"); }
    setActivating(false);
  };

  const products = data.products || [];
  const evidenceItems = data.evidence_items || [];
  const evidenceTypes = config?.evidence_types || [];
  const stepFields = (config?.steps || [])[step]?.fields || [];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <Rocket className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">入驻 Universe</h1>
            <p className="text-sm text-slate-400">填写企业资料，让节点真正活起来</p>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            {savedAt ? `已保存 ${savedAt}` : "自动保存"}
          </div>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-1 mb-8">
          {STEP_META.map((s, i) => {
            const Icon = s.icon;
            const active = i === step;
            const done = i < step;
            return (
              <button key={s.key} onClick={() => i < step && setStep(i)}
                className={`flex-1 flex flex-col items-center gap-1.5 relative ${i < step ? "cursor-pointer" : "cursor-default"}`}>
                {i > 0 && <div className={`absolute top-4 left-0 right-1/2 h-0.5 ${done ? "bg-blue-500" : "bg-slate-800"}`} />}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center relative z-10 ${
                  active ? "bg-blue-600 text-white" : done ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-500"
                }`}>
                  {done ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                </div>
                <span className={`text-[10px] ${active ? "text-white" : done ? "text-emerald-400" : "text-slate-600"}`}>
                  {s.label}
                </span>
              </button>
            );
          })}
        </div>

        {error && (
          <div className="mb-4 px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-sm text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {/* Step content */}
        {!activating && !activation && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 md:p-8">
            {step === 0 && (
              <div className="space-y-5">
                <StepTitle icon={Building2} title="企业身份" desc="让 Universe 认识你是谁" />
                <FormField label="企业名称" required hint="工商注册名称或常用品牌名" example="如：星辰AI营销科技"
                  value={data.company_name || ""} onChange={v => update("company_name", v)} />
                <FormField label="企业简介" required hint="一句话说明你做什么" example="专注GEO与AI搜索优化的营销科技服务商" textarea
                  value={data.description || ""} onChange={v => update("description", v)} />
                <div className="grid grid-cols-2 gap-4">
                  <FormField label="所在地区" value={data.region || ""} onChange={v => update("region", v)} placeholder="如：上海" />
                  <FormField label="成立时间" value={data.founded_year || ""} onChange={v => update("founded_year", v)} placeholder="如：2019" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <SelectField label="企业规模" options={["1-50人", "50-200人", "200-500人", "500-2000人", "2000人以上"]}
                    value={data.company_size || ""} onChange={v => update("company_size", v)} />
                  <SelectField label="当前发展阶段" options={["初创期", "成长期", "成熟期", "转型期"]}
                    value={data.development_stage || ""} onChange={v => update("development_stage", v)} />
                </div>
                <FormField label="官网" value={data.website || ""} onChange={v => update("website", v)} placeholder="https://" />
                <FormField label="联系方式" value={data.contact_email || ""} onChange={v => update("contact_email", v)} placeholder="邮箱或电话" />
              </div>
            )}

            {step === 1 && (
              <div className="space-y-5">
                <StepTitle icon={MapPin} title="行业位置" desc="告诉 Universe 你身处哪个世界" />
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">一级行业 <span className="text-rose-400">*</span></label>
                  <select value={data.industry_id || ""} onChange={e => update("industry_id", e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                    <option value="">选择行业</option>
                    {industries.map((ind: any) => <option key={ind.id} value={ind.id}>{ind.name}</option>)}
                  </select>
                </div>
                <FormField label="二级行业" value={data.sub_industry || ""} onChange={v => update("sub_industry", v)} placeholder="如：AI营销" />
                <FormField label="细分赛道" value={data.track || ""} onChange={v => update("track", v)} placeholder="如：AI搜索优化" />
                <FormField label="目标市场" value={data.target_market || ""} onChange={v => update("target_market", v)} placeholder="如：toB 企业客户" />
                <FormField label="服务区域" value={data.service_region || ""} onChange={v => update("service_region", v)} placeholder="如：全国" />
                <FormField label="当前自我定位" value={data.self_positioning || ""} onChange={v => update("self_positioning", v)}
                  placeholder="如：GEO领域的新锐服务商" />
              </div>
            )}

            {step === 2 && (
              <div className="space-y-5">
                <StepTitle icon={Boxes} title="产品与能力" desc="你提供什么，能解决什么问题" />
                {products.map((p: any, i: number) => (
                  <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3 relative">
                    <button onClick={() => update("products", products.filter((_: any, j: number) => j !== i))}
                      className="absolute top-3 right-3 text-slate-500 hover:text-rose-400 transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <div className="grid grid-cols-2 gap-3">
                      <FormField label="产品/服务名称" required value={p.name || ""} onChange={v => {
                        const next = [...products]; next[i] = { ...next[i], name: v }; update("products", next);
                      }} />
                      <FormField label="产品类型" value={p.product_type || ""} onChange={v => {
                        const next = [...products]; next[i] = { ...next[i], product_type: v }; update("products", next);
                      }} placeholder="服务/工具/数据" />
                    </div>
                    <FormField label="核心能力" required value={p.core_capability || ""} onChange={v => {
                      const next = [...products]; next[i] = { ...next[i], core_capability: v }; update("products", next);
                    }} placeholder="如：AI内容优化" />
                    <div className="grid grid-cols-2 gap-3">
                      <FormField label="目标客户" value={p.target_customer || ""} onChange={v => {
                        const next = [...products]; next[i] = { ...next[i], target_customer: v }; update("products", next);
                      }} />
                      <FormField label="交付方式" value={p.delivery_method || ""} onChange={v => {
                        const next = [...products]; next[i] = { ...next[i], delivery_method: v }; update("products", next);
                      }} />
                    </div>
                    <FormField label="差异化优势" value={p.differentiator || ""} onChange={v => {
                      const next = [...products]; next[i] = { ...next[i], differentiator: v }; update("products", next);
                    }} />
                  </div>
                ))}
                <button onClick={() => update("products", [...products, {}])}
                  className="w-full py-3 border-2 border-dashed border-slate-700 rounded-lg text-sm text-slate-400 hover:border-blue-500 hover:text-blue-400 transition flex items-center justify-center gap-2">
                  <Plus className="w-4 h-4" /> 添加产品/服务
                </button>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-5">
                <StepTitle icon={FileCheck2} title="证据与背书" desc="提交可验证的资料，信誉由证据产生" />
                <div className="flex items-start gap-2 px-4 py-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300">
                  <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  提交的内容默认为自我申报，不会自动标记为已验证。信誉只由证据和事件计算，不能手动填写。
                </div>
                {evidenceItems.map((ev: any, i: number) => (
                  <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3 relative">
                    <button onClick={() => update("evidence_items", evidenceItems.filter((_: any, j: number) => j !== i))}
                      className="absolute top-3 right-3 text-slate-500 hover:text-rose-400 transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1.5">证据类型 <span className="text-rose-400">*</span></label>
                        <select value={ev.evidence_type || ""} onChange={e => {
                          const next = [...evidenceItems]; next[i] = { ...next[i], evidence_type: e.target.value }; update("evidence_items", next);
                        }} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
                          <option value="">选择类型</option>
                          {evidenceTypes.map((t: any) => <option key={t.id} value={t.id}>{t.label}</option>)}
                        </select>
                      </div>
                      <FormField label="标题" required value={ev.title || ""} onChange={v => {
                        const next = [...evidenceItems]; next[i] = { ...next[i], title: v }; update("evidence_items", next);
                      }} />
                    </div>
                    <FormField label="来源 URL" required value={ev.source_url || ""} onChange={v => {
                      const next = [...evidenceItems]; next[i] = { ...next[i], source_url: v }; update("evidence_items", next);
                    }} placeholder="https://" />
                    <div className="grid grid-cols-2 gap-3">
                      <FormField label="来源名称" value={ev.source_name || ""} onChange={v => {
                        const next = [...evidenceItems]; next[i] = { ...next[i], source_name: v }; update("evidence_items", next);
                      }} placeholder="如：官网、某媒体" />
                      <FormField label="发生时间" value={ev.occurred_at || ""} onChange={v => {
                        const next = [...evidenceItems]; next[i] = { ...next[i], occurred_at: v }; update("evidence_items", next);
                      }} placeholder="如：2026-01" />
                    </div>
                  </div>
                ))}
                <button onClick={() => update("evidence_items", [...evidenceItems, {}])}
                  className="w-full py-3 border-2 border-dashed border-slate-700 rounded-lg text-sm text-slate-400 hover:border-blue-500 hover:text-blue-400 transition flex items-center justify-center gap-2">
                  <Plus className="w-4 h-4" /> 添加证据
                </button>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-5">
                <StepTitle icon={Target} title="目标与问题" desc="告诉 Universe 你想走向哪里" />
                <FormField label="当前最重要的问题" value={data.key_problem || ""} onChange={v => update("key_problem", v)}
                  placeholder="如：AI搜索中几乎看不到我们" textarea />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <FormField label="未来30天目标" value={data.goal_30d || ""} onChange={v => update("goal_30d", v)} />
                  <FormField label="未来90天目标" value={data.goal_90d || ""} onChange={v => update("goal_90d", v)} />
                  <FormField label="未来180天目标" value={data.goal_180d || ""} onChange={v => update("goal_180d", v)} />
                </div>
                <FormField label="希望连接的资源" value={data.connection_wants || ""} onChange={v => update("connection_wants", v)}
                  placeholder="如：数据服务商、行业认证机构" />
                <FormField label="希望避免的风险" value={data.risk_to_avoid || ""} onChange={v => update("risk_to_avoid", v)}
                  placeholder="如：低价竞争、供应链不稳定" />
              </div>
            )}

            {step === 5 && (
              <div className="space-y-5">
                <StepTitle icon={Rocket} title="确认与激活" desc="检查资料，确认后 Universe 将为你创建节点" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <SummaryItem label="企业名称" value={data.company_name} icon={Building2} />
                  <SummaryItem label="行业" value={industries.find((i: any) => i.id === data.industry_id)?.name || "未选择"} icon={MapPin} />
                  <SummaryItem label="产品/能力" value={`${(data.products || []).length} 项`} icon={Boxes} />
                  <SummaryItem label="证据" value={`${(data.evidence_items || []).length} 条`} icon={FileCheck2} />
                  <SummaryItem label="30天目标" value={data.goal_30d || "未填写"} icon={Target} />
                  <SummaryItem label="将运行" value="身份→位置→信誉→未来→连接" icon={Sparkles} />
                </div>

                {!validation && (
                  <button onClick={handleValidate} disabled={validating}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
                    {validating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                    校验资料
                  </button>
                )}

                {validation && (
                  <div className="space-y-3">
                    {validation.valid ? (
                      <div className="px-4 py-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-sm text-emerald-300 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" /> 资料完整，可以激活节点
                      </div>
                    ) : (
                      <div className="px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-sm text-rose-300">
                        <div className="flex items-center gap-2 mb-1"><AlertCircle className="w-4 h-4" /> 还有 {validation.issues.length} 项需要补充</div>
                        <ul className="list-disc list-inside text-xs space-y-1 mt-2">
                          {validation.issues.slice(0, 5).map((iss: any, i: number) => (
                            <li key={i}>{iss.message}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {(validation.warnings || []).map((w: any, i: number) => (
                      <div key={i} className="px-4 py-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300 flex items-start gap-2">
                        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" /> {w.message}
                      </div>
                    ))}
                    <div className="px-4 py-3 bg-slate-800/60 rounded-lg text-xs text-slate-400 flex items-center gap-2">
                      <Clock className="w-4 h-4" /> 数据完整度 {Math.round((validation.data_quality || 0) * 100)}%
                      {validation.missing_evidence?.length > 0 && (
                        <span className="ml-auto">缺：{validation.missing_evidence.slice(0, 3).join("、")}</span>
                      )}
                    </div>
                    {validation.valid && (
                      <button onClick={handleActivate} disabled={activating}
                        className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2">
                        {activating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
                        确认并激活节点
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Activation progress */}
        {activating && !activation && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
            <Rocket className="w-10 h-10 text-blue-400 mx-auto mb-4 animate-pulse" />
            <h2 className="text-lg font-semibold mb-2">正在激活节点...</h2>
            <p className="text-sm text-slate-400 mb-6">Universe 正在运行完整的生命周期分析</p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              {(config?.activation_stages || []).map((s: any) => (
                <span key={s.id} className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-400 animate-pulse">
                  {s.label}
                </span>
              ))}
            </div>
          </div>
        )}

        {activation && activation.activation_status === "completed" && (
          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-8 text-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">节点已入驻 Universe</h2>
            <p className="text-sm text-slate-300 mb-6">即将进入你的 Universe Home...</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-w-lg mx-auto text-left">
              {Object.entries(activation.lifecycle || {}).map(([k, v]: any) => (
                <div key={k} className="flex items-center gap-2 px-3 py-2 bg-slate-800/60 rounded-lg text-xs">
                  {v.status === "completed"
                    ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    : <AlertCircle className="w-3.5 h-3.5 text-rose-400" />}
                  <span className="text-slate-300">{k}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Nav buttons */}
        {!activating && !activation && (
          <div className="flex items-center justify-between mt-6">
            <button onClick={prev} disabled={step === 0}
              className="px-5 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800 transition flex items-center gap-2 disabled:opacity-30">
              <ArrowLeft className="w-4 h-4" /> 上一步
            </button>
            {step < 5 ? (
              <button onClick={next}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition flex items-center gap-2">
                下一步 <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button onClick={() => { saveDraft(data, 6); setStep(0); }}
                className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition flex items-center gap-2">
                <Save className="w-4 h-4" /> 返回修改
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StepTitle({ icon: Icon, title, desc }: { icon: any; title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 mb-1">
      <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-blue-400" />
      </div>
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-xs text-slate-500">{desc}</p>
      </div>
    </div>
  );
}

function FormField({ label, value, onChange, required, hint, example, placeholder, textarea }: {
  label: string; value: string; onChange: (v: string) => void;
  required?: boolean; hint?: string; example?: string; placeholder?: string; textarea?: boolean;
}) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1.5">
        {label} {required && <span className="text-rose-400">*</span>}
        {hint && <span className="ml-2 text-[10px] text-slate-600">{hint}</span>}
      </label>
      {textarea ? (
        <textarea value={value} onChange={e => onChange(e.target.value)} placeholder={example || placeholder}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500 min-h-[72px]" />
      ) : (
        <input value={value} onChange={e => onChange(e.target.value)} placeholder={example || placeholder}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500" />
      )}
    </div>
  );
}

function SelectField({ label, options, value, onChange }: {
  label: string; options: string[]; value: string; onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1.5">{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
        <option value="">请选择</option>
        {options.map((o: string) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function SummaryItem({ label, value, icon: Icon }: { label: string; value: string; icon: any }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-4">
      <div className="flex items-center gap-2 text-xs text-slate-500 mb-1.5">
        <Icon className="w-3.5 h-3.5" /> {label}
      </div>
      <p className="text-sm font-medium text-slate-200">{value || "未填写"}</p>
    </div>
  );
}
