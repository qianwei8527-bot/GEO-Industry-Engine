'use client';

import { useEffect, useState } from 'react';
import {
  BookOpen,
  ChevronDown,
  ChevronUp,
  CircleDot,
  FilePlus2,
  History,
  Loader2,
  Plus,
  Sparkles,
  TriangleAlert,
} from 'lucide-react';
import {
  classifyIssue,
  confirmIssueTemplate,
  createIssue,
  fetchIssue,
  updateIssue,
} from '@/lib/realm-owner/queries-v105';
import type { GeoProjectSummary, IssueRecordItem } from '@/lib/realm-owner/types';
import ModuleState from './module-state';

const STATUS_LABELS: Record<string, string> = {
  new: '新收集',
  triaged: '已分类',
  in_progress: '处理中',
  waiting: '等待外部',
  blocked: '受阻',
  resolved: '已解决',
  verified_resolution: '已验证',
  archived: '已归档',
};

const SEVERITY_LABELS: Record<string, string> = {
  low: '低',
  normal: '普通',
  high: '高',
  critical: '紧急',
};

function formatTime(iso?: string | null): string {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

export default function IssueLibraryPanel({
  realmId,
  canWrite,
  issues,
  projects,
  onRefreshIssues,
}: {
  realmId: string;
  canWrite: boolean;
  issues: IssueRecordItem[];
  projects: GeoProjectSummary[];
  onRefreshIssues: () => void;
}) {
  const [formOpen, setFormOpen] = useState(false);
  const [originalText, setOriginalText] = useState('');
  const [title, setTitle] = useState('');
  const [scenario, setScenario] = useState('');
  const [severity, setSeverity] = useState('normal');
  const [projectId, setProjectId] = useState('');
  const [creating, setCreating] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, IssueRecordItem>>({});
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!expandedId || details[expandedId]) return;
    let cancelled = false;
    fetchIssue(expandedId)
      .then((detail) => {
        if (!cancelled) setDetails((prev) => ({ ...prev, [expandedId]: detail }));
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [expandedId, details]);

  async function submitIssue() {
    if (!originalText.trim()) {
      setMessage('请输入问题原文');
      return;
    }
    setCreating(true);
    setMessage(null);
    try {
      await createIssue({
        realm_id: realmId,
        original_text: originalText.trim(),
        title: title.trim() || undefined,
        scenario: scenario.trim() || undefined,
        severity,
        project_id: projectId || undefined,
        source: 'owner_manual',
      });
      setOriginalText('');
      setTitle('');
      setScenario('');
      setSeverity('normal');
      setProjectId('');
      setFormOpen(false);
      onRefreshIssues();
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '保存问题失败');
    } finally {
      setCreating(false);
    }
  }

  async function runClassify(issue: IssueRecordItem) {
    setBusyId(issue.id);
    setMessage(null);
    try {
      await classifyIssue(issue.id);
      onRefreshIssues();
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || 'AI 分类失败');
    } finally {
      setBusyId(null);
    }
  }

  async function runStatusChange(issue: IssueRecordItem, status: string) {
    setBusyId(issue.id);
    setMessage(null);
    try {
      await updateIssue(issue.id, { status });
      onRefreshIssues();
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '状态更新失败');
    } finally {
      setBusyId(null);
    }
  }

  async function runTemplate(issue: IssueRecordItem, confirmed: boolean) {
    setBusyId(issue.id);
    setMessage(null);
    try {
      await confirmIssueTemplate(issue.id, confirmed);
      onRefreshIssues();
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '模板确认失败');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className='realm-card p-4' aria-labelledby='issue-library-title'>
      <header className='flex flex-wrap items-start justify-between gap-2'>
        <div>
          <h2 id='issue-library-title' className='text-base font-semibold text-slate-900'>问题收集整理库</h2>
          <p className='mt-0.5 text-xs leading-5 text-slate-500'>
            问题原文追加保存，AI 分类只是建议；方法、结论和模板都需要域主确认。
          </p>
        </div>
        {issues.length > 0 && (
          <span className='rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600'>
            {issues.length} 条记录
          </span>
        )}
      </header>

      {canWrite && (
        <div className='mt-3'>
          <button
            type='button'
            onClick={() => setFormOpen((open) => !open)}
            className='inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'
          >
            {formOpen ? <ChevronUp className='h-4 w-4' aria-hidden='true' /> : <FilePlus2 className='h-4 w-4' aria-hidden='true' />}
            {formOpen ? '收起录入' : '录入执行中的问题'}
          </button>
        </div>
      )}

      {formOpen && (
        <div className='mt-3 rounded-lg border border-teal-200 bg-teal-50/50 p-3'>
          <div className='grid grid-cols-1 gap-2 md:grid-cols-2'>
            <label className='block md:col-span-2'>
              <span className='text-xs font-medium text-slate-700'>问题原文（必填，原样保留）</span>
              <textarea
                value={originalText}
                onChange={(event) => setOriginalText(event.target.value)}
                rows={2}
                placeholder='例如：提交审批时提示权限不足，无法继续'
                className='mt-1 w-full resize-y rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              />
            </label>
            <label className='block'>
              <span className='text-xs font-medium text-slate-700'>标题（可选）</span>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder='自动取原文前 80 字'
                className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              />
            </label>
            <label className='block'>
              <span className='text-xs font-medium text-slate-700'>场景</span>
              <input
                value={scenario}
                onChange={(event) => setScenario(event.target.value)}
                placeholder='例如：执行计划第 1 步审批'
                className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              />
            </label>
            <label className='block'>
              <span className='text-xs font-medium text-slate-700'>关联项目</span>
              <select
                value={projectId}
                onChange={(event) => setProjectId(event.target.value)}
                className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              >
                <option value=''>不关联</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
            </label>
            <label className='block'>
              <span className='text-xs font-medium text-slate-700'>严重程度</span>
              <select
                value={severity}
                onChange={(event) => setSeverity(event.target.value)}
                className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              >
                {Object.entries(SEVERITY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </label>
          </div>
          <div className='mt-2 flex items-center justify-end'>
            <button
              type='button'
              onClick={submitIssue}
              disabled={creating}
              className='inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60'
            >
              {creating ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <Plus className='h-4 w-4' aria-hidden='true' />}
              保存问题
            </button>
          </div>
        </div>
      )}

      {issues.length === 0 && !formOpen ? (
        <div className='mt-3'>
          <ModuleState
            variant='empty'
            title='还没有问题记录'
            description='执行中遇到权限、数据、流程或工具问题时，先原样记录，AI 会给出分类建议。'
            compact
          />
        </div>
      ) : (
        <div className='mt-3 space-y-2.5'>
          {issues.map((issue) => (
            <IssueCard
              key={issue.id}
              issue={issue}
              detail={details[issue.id] || null}
              canWrite={canWrite}
              busy={busyId === issue.id}
              expanded={expandedId === issue.id}
              onToggle={() => setExpandedId((current) => (current === issue.id ? null : issue.id))}
              onClassify={() => void runClassify(issue)}
              onStatusChange={(status) => void runStatusChange(issue, status)}
              onTemplate={(confirmed) => void runTemplate(issue, confirmed)}
            />
          ))}
        </div>
      )}

      {message && (
        <p className='mt-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800'>
          <TriangleAlert className='mt-0.5 h-3.5 w-3.5 shrink-0' aria-hidden='true' />
          {message}
        </p>
      )}
    </section>
  );
}

function IssueCard({
  issue,
  detail,
  canWrite,
  busy,
  expanded,
  onToggle,
  onClassify,
  onStatusChange,
  onTemplate,
}: {
  issue: IssueRecordItem;
  detail: IssueRecordItem | null;
  canWrite: boolean;
  busy: boolean;
  expanded: boolean;
  onToggle: () => void;
  onClassify: () => void;
  onStatusChange: (status: string) => void;
  onTemplate: (confirmed: boolean) => void;
}) {
  const classification = issue.ai_classification;
  const confidence = classification?.confidence ? Math.round(classification.confidence * 100) : null;
  return (
    <article className='rounded-lg border border-slate-200 bg-white p-3'>
      <div className='flex flex-wrap items-start justify-between gap-2'>
        <div className='min-w-0 flex-1'>
          <div className='flex flex-wrap items-center gap-1.5'>
            <span className='text-[13px] font-semibold text-slate-800'>{issue.title || issue.original_text}</span>
            <span className='rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500'>{issue.issue_code}</span>
          </div>
          <p className='mt-1 line-clamp-2 text-[11px] leading-4 text-slate-600'>{issue.original_text}</p>
          <div className='mt-1.5 flex flex-wrap items-center gap-1.5 text-[11px]'>
            {issue.category && (
              <span className='rounded-md bg-violet-50 px-1.5 py-0.5 font-medium text-violet-700'>{issue.category}</span>
            )}
            <span className='rounded-md bg-slate-100 px-1.5 py-0.5 text-slate-600'>{SEVERITY_LABELS[issue.severity] || issue.severity}</span>
            <span className='rounded-md bg-slate-100 px-1.5 py-0.5 text-slate-600'>{STATUS_LABELS[issue.status] || issue.status}</span>
            {issue.is_template_candidate && (
              <span className='rounded-md bg-emerald-50 px-1.5 py-0.5 font-medium text-emerald-700'>模板候选</span>
            )}
            {confidence !== null && (
              <span className='text-slate-400'>AI 置信度 {confidence}%</span>
            )}
          </div>
        </div>
        <button
          type='button'
          onClick={onToggle}
          className='inline-flex h-7 shrink-0 items-center gap-1 rounded-md border border-slate-200 px-2 text-[11px] font-medium text-slate-600 hover:bg-slate-50'
          aria-expanded={expanded}
        >
          {expanded ? <ChevronUp className='h-3.5 w-3.5' aria-hidden='true' /> : <ChevronDown className='h-3.5 w-3.5' aria-hidden='true' />}
          {expanded ? '收起' : '详情'}
        </button>
      </div>

      {expanded && (
        <div className='mt-2.5 space-y-2 border-t border-slate-100 pt-2.5'>
          <div className='flex flex-wrap items-center gap-2'>
            {canWrite && (
              <>
                <select
                  value={issue.status}
                  onChange={(event) => onStatusChange(event.target.value)}
                  disabled={busy}
                  className='rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 disabled:opacity-60'
                >
                  {Object.entries(STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
                <button
                  type='button'
                  onClick={onClassify}
                  disabled={busy}
                  className='inline-flex items-center gap-1.5 rounded-lg border border-violet-300 bg-white px-2.5 py-1.5 text-xs font-medium text-violet-700 hover:bg-violet-50 disabled:opacity-60'
                >
                  {busy ? <Loader2 className='h-3.5 w-3.5 animate-spin' aria-hidden='true' /> : <Sparkles className='h-3.5 w-3.5' aria-hidden='true' />}
                  AI 重新分类
                </button>
                {!issue.is_template_candidate ? (
                  <button
                    type='button'
                    onClick={() => onTemplate(true)}
                    disabled={busy}
                    className='inline-flex items-center gap-1.5 rounded-lg border border-emerald-300 bg-white px-2.5 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-60'
                  >
                    <BookOpen className='h-3.5 w-3.5' aria-hidden='true' />
                    确认为模板
                  </button>
                ) : (
                  <button
                    type='button'
                    onClick={() => onTemplate(false)}
                    disabled={busy}
                    className='inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-60'
                  >
                    取消模板
                  </button>
                )}
              </>
            )}
          </div>

          {classification && (
            <p className='rounded bg-violet-50 px-2 py-1.5 text-[11px] leading-4 text-violet-700'>
              AI 分类建议：{classification.category}（置信度 {confidence ?? 0}%）。理由：{classification.reason || '待补充'}。
            </p>
          )}

          {issue.scenario && <p className='text-[11px] leading-4 text-slate-600'>场景：{issue.scenario}</p>}
          {issue.possible_causes && <p className='text-[11px] leading-4 text-slate-600'>可能原因：{issue.possible_causes}</p>}
          {issue.final_solution && (
            <p className='rounded bg-emerald-50 px-2 py-1.5 text-[11px] leading-4 text-emerald-800'>有效结论：{issue.final_solution}</p>
          )}
          {issue.effective_methods.length > 0 && (
            <p className='text-[11px] leading-4 text-slate-600'>有效方法：{issue.effective_methods.join('；')}</p>
          )}
          {issue.ineffective_methods.length > 0 && (
            <p className='text-[11px] leading-4 text-slate-600'>无效方法：{issue.ineffective_methods.join('；')}</p>
          )}
          {issue.recurrence_count > 0 && (
            <p className='text-[11px] leading-4 text-slate-600'>复现次数：{issue.recurrence_count}</p>
          )}

          <div>
            <p className='flex items-center gap-1 text-[11px] font-medium text-slate-500'>
              <History className='h-3 w-3' aria-hidden='true' />
              历史记录
            </p>
            {detail && detail.events.length > 0 ? (
              <ul className='mt-1 space-y-1'>
                {detail.events.map((event) => (
                  <li key={event.id} className='flex items-start gap-2 text-[11px] leading-4 text-slate-600'>
                    <CircleDot className='mt-0.5 h-3 w-3 shrink-0 text-slate-400' aria-hidden='true' />
                    <span className='min-w-0 flex-1'>
                      <span className='font-medium text-slate-700'>{event.event_type}</span>
                      {event.content ? `：${event.content}` : ''}
                    </span>
                    <span className='shrink-0 text-slate-400'>{formatTime(event.created_at)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className='mt-1 text-[11px] text-slate-400'>历史记录加载中...</p>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
