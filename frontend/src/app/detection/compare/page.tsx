'use client';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { authedFetch } from '@/lib/authFetch';
import { BarChart3, TrendingUp, Shield, Target, ArrowLeft, Users, Search, Brain, Activity, AlertTriangle, CheckCircle, Lightbulb, ExternalLink } from 'lucide-react';

const METRIC_LABELS: Record<string, string> = {
  visibility: 'AI Visibility',
  company_growth: 'Growth',
  competitive_position: 'Competitive',
  roadmap: 'Roadmap',
};

const METRIC_ICONS: Record<string, any> = {
  visibility: TrendingUp,
  company_growth: BarChart3,
  competitive_position: Target,
  roadmap: Shield,
};

function ComparisonInsight({ result, companyId }: { result: any; companyId: string }) {
  if (!result?.comparisons) return (
    <div className="text-center py-6 text-slate-500">
      <div className="mb-6 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800">尚未建立真实观测基线：AI 可见度对比需要至少一次真实观测样本后生成，当前不展示占位结论。</div>
      <Activity className="w-6 h-6 mx-auto mb-2" />
      <p className="text-sm">Run a comparison to see AI-generated strategic assessment</p>
    </div>
  );

  const comparisons = result.comparisons.filter((c: any) => !c.error);
  if (comparisons.length === 0) return (
    <div className="text-center py-6 text-slate-500">
      <p className="text-sm">No valid comparisons to analyze</p>
    </div>
  );

  // Count weaknesses across all competitors
  const allWeaknesses = comparisons.flatMap((c: any) =>
    (c.metrics || []).filter((m: any) => m.winner === 'competitor').map((m: any) => m.metric)
  );
  const uniqueWeaknesses: string[] = Array.from(new Set(allWeaknesses as string[]));
  const totalGaps = allWeaknesses.length;
  const hasEvidenceGaps = comparisons.some((c: any) => c.evidence_gap && c.evidence_gap.delta < 0);

  const noBaseline = !sessionStorage.getItem("geo_baseline");
  return (
    <div className="space-y-4">
      {/* Strategic Summary */}
      <div className="bg-gradient-to-r from-blue-950/30 to-slate-900 border border-blue-900/30 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-1">Strategic Assessment</h4>
            <p className="text-sm text-slate-400">
              {totalGaps === 0
                ? `You lead across all metrics. Focus on maintaining advantage through continued GEO investment.`
                : `Identified ${totalGaps} competitive gap${totalGaps > 1 ? 's' : ''} ${uniqueWeaknesses.length > 0 ? 'in ' + uniqueWeaknesses.map((w) => METRIC_LABELS[w] || w).join(', ') : ''}. ${hasEvidenceGaps ? 'Evidence gaps are weakening your trust position. ' : ''}Prioritize the actions below.`}
            </p>
          </div>
        </div>
      </div>

      {/* Action Items */}
      <div className="grid gap-2">
        {uniqueWeaknesses.length > 0 && (
          <div className="flex items-start gap-2 text-sm bg-slate-800/40 rounded-lg p-3">
            <Target className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
            <span className="text-slate-300">
              <strong className="text-emerald-400">Close the gap:</strong> Focus on improving{' '}
              {uniqueWeaknesses.map((w) => METRIC_LABELS[w] || w).join(', ')}. Explore Candidate Providers above for expert help.
            </span>
          </div>
        )}
        {hasEvidenceGaps && (
          <div className="flex items-start gap-2 text-sm bg-slate-800/40 rounded-lg p-3">
            <Shield className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
            <span className="text-slate-300">
              <strong className="text-blue-400">Build trust evidence:</strong> Add certifications, customer case studies, and third-party validations to strengthen your evidence profile.
            </span>
          </div>
        )}
        <div className="flex items-start gap-2 text-sm bg-slate-800/40 rounded-lg p-3">
          <TrendingUp className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
          <span className="text-slate-300">
            <strong className="text-purple-400">Monitor continuously:</strong> GEO scores change as competitors improve. Set up regular comparison checks to track your position.
          </span>
        </div>
      </div>

      {/* Link to full diagnosis */}
      <div className="text-center pt-2">
        <Link href={'/company/' + companyId}
          className="inline-flex items-center gap-1 text-sm text-emerald-400 hover:text-emerald-300 transition-colors">
          View full AI diagnosis <ArrowLeft className="w-3 h-3 rotate-180" />
        </Link>
      </div>
    </div>
  );
}

export default function ComparePage() {
  const params = useSearchParams();
  const companyId = params.get('company_id') || '';
  const companyName = params.get('name') || 'Your Company';

  const [companies, setCompanies] = useState<any[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    api.companies.list().then((d: any) => {
      const list = Array.isArray(d) ? d : d?.items || [];
      setCompanies(list.filter((c: any) => c.id !== companyId));
    }).catch(() => {}).finally(() => setLoading(false));
  }, [companyId]);

  async function runCompare() {
    if (!companyId || selected.length === 0) return;
    setComparing(true);
    try {
      const res = await api.agent.compare(companyId, selected);
      setResult(res);
    } catch (e: any) { alert('Compare failed: ' + e.message); }
    setComparing(false);
  }

  function toggleCompany(id: string) {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id].slice(0, 3));
  }

  if (loading) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="mb-8">
          <Link href="/detection" className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-300 mb-4">
            <ArrowLeft className="w-4 h-4" /> Back to Detection
          </Link>
          <h1 className="text-3xl font-bold mb-2">GEO Competitive Comparison</h1>
          <p className="text-slate-400">
            Compare <span className="font-semibold text-emerald-400">{companyName}</span> against industry competitors
          </p>
        </div>

        {/* Company Picker */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 mb-8">
          <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-emerald-400" /> Select Competitors (max 3)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 mb-4">
            {companies.slice(0, 12).map((c: any) => (
              <button key={c.id} onClick={() => toggleCompany(c.id)}
                className={'text-left px-4 py-2.5 rounded-lg border text-sm transition-all ' + (selected.includes(c.id) ? 'border-emerald-400 bg-emerald-950/30 text-emerald-300 font-medium' : 'border-slate-700 hover:border-slate-600 text-slate-400')}>
                {c.name || c.company_name || 'Unknown'}
              </button>
            ))}
          </div>
          <button onClick={runCompare} disabled={selected.length === 0 || comparing}
            className="px-6 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors">
            {comparing ? 'Comparing...' : 'Run Comparison'}
            <BarChart3 className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Summary Card */}
            <div className="bg-gradient-to-r from-emerald-950/30 to-slate-900 border border-emerald-900/30 rounded-lg p-6">
              <div className="flex items-start gap-3">
                <Brain className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <h2 className="text-lg font-semibold mb-1">
                    {result.company_name} — GEO Score: <span className="text-emerald-400">{result.company_overall}</span>
                  </h2>
                  <p className="text-sm text-slate-400">{result.summary}</p>
                </div>
              </div>
            </div>

            {/* Per-competitor comparison */}
            {result.comparisons?.map((comp: any, i: number) => (
              <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-6">
                <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <Search className="w-4 h-4 text-slate-500" />
                  vs {comp.competitor_name || comp.competitor_id?.slice(0, 8)}
                  {comp.error && <span className="text-xs text-red-400 ml-2">({comp.error})</span>}
                </h3>
{comp.metrics ? (
                  <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      {comp.metrics.map((m: any) => {
                        const Icon = METRIC_ICONS[m.metric] || BarChart3;
                        const deltaColor = m.winner === 'company' ? 'text-emerald-400' : m.winner === 'competitor' ? 'text-red-400' : 'text-slate-500';
                        return (
                          <div key={m.metric} className="bg-slate-800/40 rounded-lg p-4 text-center group relative">
                            <Icon className="w-5 h-5 text-slate-500 mx-auto mb-2" />
                            <div className="text-xs text-slate-500 uppercase tracking-wide">{METRIC_LABELS[m.metric] || m.metric}</div>
                            <div className="flex items-center justify-center gap-2 mt-1">
                              <span className="text-lg font-bold text-emerald-400">{m.company_score}</span>
                              <span className="text-xs text-slate-600">vs</span>
                              <span className="text-lg font-bold text-slate-400">{m.competitor_score}</span>
                            </div>
                            <div className={'text-xs font-semibold mt-1 ' + deltaColor}>
                              {m.delta > 0 ? '+' + m.delta : m.delta}
                              {m.winner === 'company' ? ' Lead' : m.winner === 'competitor' ? ' Behind' : ' Even'}
                            </div>
                            {m.explanation && (
                              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                {m.explanation}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Evidence Gap Card */}
                    {comp.evidence_gap && (
                      <div className="bg-slate-800/40 border border-slate-700 rounded-lg p-4 mb-4">
                        <h4 className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-2">
                          <AlertTriangle className="w-3 h-3 text-yellow-400" /> Evidence Gap Analysis
                        </h4>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-slate-300">{comp.evidence_gap.company_evidence_count} records (you)</span>
                          <span className="text-slate-600">vs</span>
                          <span className="text-slate-300">{comp.evidence_gap.competitor_evidence_count} records (competitor)</span>
                          <span className={'font-semibold ' + (comp.evidence_gap.delta >= 0 ? 'text-emerald-400' : 'text-red-400')}>
                            {comp.evidence_gap.delta >= 0 ? '+' + comp.evidence_gap.delta : comp.evidence_gap.delta}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">{comp.evidence_gap.insight}</p>
                      </div>
                    )}

                    {/* Candidate Providers */}
                    {comp.candidate_providers && comp.candidate_providers.length > 0 && (
                      <div className="bg-slate-800/40 border border-slate-700 rounded-lg p-4">
                        <h4 className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-2">
                          <Lightbulb className="w-3 h-3 text-yellow-400" /> Candidate Providers: Capabilities That Match Your Gaps
                        </h4>
                        <div className="grid gap-2">
                          {comp.candidate_providers.map((p: any, j: number) => (
                            <div key={j} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-4 py-2.5">
                              <div>
                                <div className="text-sm font-medium text-slate-200">{p.name}</div>
                                <div className="text-xs text-slate-500">
                                  Trust: {p.trust_score} | {p.capabilities?.join(', ') || 'Unknown capabilities'}
                                </div>
                              </div>
                              <Link href={'/marketplace/provider/' + (p.id || '')} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                                View <ExternalLink className="w-3 h-3" />
                              </Link>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-4 text-slate-500">
                    <Activity className="w-6 h-6 mx-auto mb-2" />
                    <p className="text-sm">No comparison metrics available</p>
                  </div>
                )}
              </div>
            ))}

            {/* AgentInsight - Live competitive intelligence */}
            {companyId && (
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
                <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-emerald-400" /> AI Competitive Assessment
                </h3>
                <ComparisonInsight result={result} companyId={companyId} />
              </div>
            )}
          </div>
        )}

        {!result && !loading && (
          <div className="text-center py-20 text-slate-500">
            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">Select competitors and run comparison to see GEO competitive analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}
