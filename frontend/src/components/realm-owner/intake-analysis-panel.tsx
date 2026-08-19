'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import {
  analyzeIntake,
  confirmIntake,
  requestIntakeChanges,
} from '@/lib/realm-owner/queries-v105';
import type { IntakeField, IntakeItem } from '@/lib/realm-owner/types';
import ModuleState from './module-state';
import TruthBadge from './truth-badge';

const STATUS_LABELS: Record<string, string> = {
  uploaded: '已上传',
  analyzing: '分析中',
  needs_confirmation: '待域主确认',
  owner_confirmed: '域主已确认',
  needs_changes: '需要修改',
  analysis_failed: '分析失败',
};

export default function IntakeAnalysisPanel({
  realmId,
  intake,
  canWrite,
  onChanged,
  onOpenManualForm,
}: {
  realmId: string;
  intake: IntakeItem | null;
  canWrite: boolean;
  onChanged: () => void;
  onOpenManualForm: () => void;
}) {
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const latest = intake?.latest_analysis ?? intake?.analyses?.[0] ?? null;
  const fields = useMemo(() => latest?.analysis_json?.fields ?? [], [latest]);

  useEffect(() => {
    if (!intake || fields.length === 0) return;
    const next: Record<string, string> = {};
    fields.forEach((field) => {
      next[field.key] = field.value;
    });
    setEdits(next);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intake?.id]);

  const unknownCount = useMemo(() => fields.filter((f) => f.status === 'unknown').length, [fields]);
  const confirmed = intake?.status === 'owner_confirmed';

  async function runAnalyze() {
    if (!intake) return;
    setBusy(true);
    setError(null);
    try {
      await analyzeIntake(intake.id);
      onChanged();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || '分析失败，请检查资料后重试。');
    } finally {
      setBusy(false);
    }
  }

  async function runConfirm() {
    if (!intake) return;
    setBusy(true);
    setError(null);
    try {
      await confirmIntake(intake.id, edits);
      onChanged();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || '确认失败，请稍后重试。');
    } finally {
      setBusy(false);
    }
  }

  async function runChanges() {
    if (!intake) return;
    setBusy(true);
    setError(null);
    try {
      await requestIntakeChanges(intake.id, '域主标记需要修改');
      onChanged();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || '操作失败，请稍后重试。');
    } finally {
      setBusy(false);
    }
  }

  if (!intake) {
    return (
      <section className='realm-card p-4' aria-labelledby='intake-analysis-title'>
        <h2 id='intake-analysis-title' className='text-base font-semibold text-slate-900'>当前分析结果与待确认项</h2>
        <div className='mt-3'>
          <ModuleState
            variant='empty'
            title='还没有客户资料'
            description='先在上方上传或粘贴客户资料，AI 会生成带来源和置信度的结构化草稿。'
            compact
          />
        </div>
      </section>
    );
  }

  return (
    <section className='realm-card p-4' aria-labelledby='intake-analysis-title'>
      <header className='flex flex-wrap items-start justify-between gap-2'>
        <div>
          <h2 id='intake-analysis-title' className='text-base font-semibold text-slate-900'>当前分析结果与待确认项</h2>
          <p className='mt-0.5 text-xs text-slate-500'>
            {intake.intake_code} · {STATUS_LABELS[intake.status] || intake.status} · AI 模式：{latest?.analysis_mode || 'local_heuristic'}
          </p>
        </div>
        {latest && (
          <span className='rounded-md bg-slate-100 px-2 py-1 text-[11px] text-slate-600'>
            版本 v{latest.version} · 待补充 {unknownCount} 项
          </span>
        )}
      </header>

      {(intake.status === 'uploaded' || intake.status === 'needs_changes') && (
        <div className='mt-3'>
          <ModuleState
            variant='empty'
            title='资料已进入，等待 AI 分析'
            description='点击“开始分析”，AI 会提取字段、保留来源并标记待补充项。'
            compact
          />
          <button
            type='button'
            onClick={runAnalyze}
            disabled={!canWrite || busy}
            className='mt-3 inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60'
          >
            {busy ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <Sparkles className='h-4 w-4' aria-hidden='true' />}
            开始分析
          </button>
        </div>
      )}

      {intake.status === 'analysis_failed' && (
        <div className='mt-3'>
          <ModuleState
            variant='error'
            title='分析失败'
            description='资料没有可用的文字内容，或解析失败。请补充可粘贴文字后重新分析。'
            actionLabel='重新尝试'
            onAction={runAnalyze}
            compact
          />
        </div>
      )}

      {fields.length > 0 && (
        <div className='mt-4 grid grid-cols-1 gap-2 md:grid-cols-2'>
          {fields.map((field) => (
            <FieldEditor
              key={field.key}
              field={field}
              value={edits[field.key] ?? field.value}
              readOnly={confirmed || !canWrite}
              onChange={(value) => setEdits((prev) => ({ ...prev, [field.key]: value }))}
            />
          ))}
        </div>
      )}

      {latest?.analysis_json?.suggested_next_steps && latest.analysis_json.suggested_next_steps.length > 0 && (
        <div className='mt-3 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2.5'>
          <p className='text-xs font-semibold text-violet-800'>AI 建议的下一步</p>
          <ol className='mt-1.5 list-decimal space-y-1 pl-4 text-[11px] leading-5 text-violet-700'>
            {latest.analysis_json.suggested_next_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {intake.file_manifest.length > 0 && (
        <div className='mt-3'>
          <p className='text-xs font-semibold text-slate-700'>资料文件</p>
          <ul className='mt-1.5 space-y-1.5'>
            {intake.file_manifest.map((file) => (
              <li key={file.file_id} className='flex items-start gap-2 rounded-md border border-slate-200 bg-slate-50 px-2.5 py-2 text-[11px] text-slate-600'>
                <FileText className='mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400' aria-hidden='true' />
                <span className='min-w-0 flex-1'>
                  <span className='block truncate font-medium text-slate-700'>{file.file_name}</span>
                  <span className='block text-slate-500'>
                    解析：{file.parse_status}{file.parse_error ? `（${file.parse_error}）` : ''} · {Math.ceil(file.size / 1024)} KB
                  </span>
                  {file.snippet && <span className='mt-0.5 block text-slate-400'>片段：{file.snippet}</span>}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <p className='mt-3 flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs leading-5 text-rose-700'>
          <AlertTriangle className='mt-0.5 h-3.5 w-3.5 shrink-0' aria-hidden='true' />
          {error}
        </p>
      )}

      <div className='mt-4 flex flex-wrap items-center gap-2'>
        {!confirmed && canWrite && fields.length > 0 && (
          <button
            type='button'
            onClick={runConfirm}
            disabled={busy}
            className='inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60'
          >
            {busy ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <CheckCircle2 className='h-4 w-4' aria-hidden='true' />}
            确认客户档案
          </button>
        )}
        {confirmed && canWrite && (
          <button
            type='button'
            onClick={runChanges}
            disabled={busy}
            className='inline-flex items-center gap-2 rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm font-medium text-amber-700 hover:bg-amber-50 disabled:opacity-60'
          >
            {busy ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <RefreshCw className='h-4 w-4' aria-hidden='true' />}
            标记需要修改
          </button>
        )}
        <button
          type='button'
          onClick={onOpenManualForm}
          className='inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'
        >
          手动补充真实输入
        </button>
      </div>
    </section>
  );
}

function FieldEditor({
  field,
  value,
  readOnly,
  onChange,
}: {
  field: IntakeField;
  value: string;
  readOnly: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <div className='rounded-lg border border-slate-200 bg-white p-2.5'>
      <div className='flex flex-wrap items-center gap-1.5'>
        <span className='text-xs font-semibold text-slate-700'>{field.label}</span>
        <TruthBadge scope={field.status} />
        <span className='rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500'>
          置信度 {Math.round(field.confidence * 100)}%
        </span>
      </div>
      {readOnly ? (
        <p className='mt-1.5 text-[13px] leading-5 text-slate-800'>{value}</p>
      ) : (
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className='mt-1.5 w-full rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-1.5 text-sm text-slate-800 focus:border-teal-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-100'
        />
      )}
      {field.source_file && (
        <p className='mt-1.5 truncate text-[10px] text-slate-400'>
          来源：{field.source_file}
          {field.source_snippet ? ` · ${field.source_snippet}` : ''}
        </p>
      )}
      <p className='mt-0.5 text-[10px] text-slate-400'>{field.notes}</p>
    </div>
  );
}
