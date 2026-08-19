'use client';

import { useRef, useState } from 'react';
import {
  AlertTriangle,
  FileText,
  Loader2,
  Sparkles,
  Upload,
  X,
} from 'lucide-react';
import { analyzeIntake, createIntake } from '@/lib/realm-owner/queries-v105';
import ModuleState from './module-state';

const ACCEPT = '.pdf,.docx,.xlsx,.csv,.txt,.md,.png,.jpg,.jpeg';
const MAX_FILES = 5;
const MAX_BYTES = 10 * 1024 * 1024;
const RELATIONSHIPS = ['附属关系', '自有品牌', '代运营', '其他', '待补充'];

export default function IntakeLaunchPanel({
  realmId,
  canWrite,
  onCreated,
}: {
  realmId: string;
  canWrite: boolean;
  onCreated: (intakeId: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [pastedText, setPastedText] = useState('');
  const [relationship, setRelationship] = useState('附属关系');
  const [notes, setNotes] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addFiles(next: FileList | null) {
    if (!next) return;
    const merged = [...files, ...Array.from(next)].slice(0, MAX_FILES);
    const oversized = merged.find((file) => file.size > MAX_BYTES);
    if (oversized) {
      setError(`单个文件不能超过 10MB：${oversized.name}`);
      return;
    }
    setFiles(merged);
    setError(null);
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function submit() {
    if (!canWrite) return;
    if (files.length === 0 && !pastedText.trim() && !notes.trim()) {
      setError('请至少上传一个文件，或粘贴客户资料文字。');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('realm_id', realmId);
      form.append('relationship', relationship);
      form.append('pasted_text', pastedText.trim());
      form.append('supplemental_notes', notes.trim());
      files.forEach((file) => form.append('files', file));
      const intake = await createIntake(form);
      const analyzed = await analyzeIntake(intake.id);
      if (analyzed.status === 'analysis_failed') {
        setError('资料解析失败或没有可用文字，请检查文件内容后重试。');
        return;
      }
      onCreated(intake.id);
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || '上传或分析失败，请稍后重试。');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className='realm-card p-4' aria-labelledby='intake-launch-title'>
      <header className='flex items-start gap-3'>
        <span className='inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-50 text-teal-700'>
          <Sparkles className='h-4 w-4' aria-hidden='true' />
        </span>
        <div className='min-w-0'>
          <h2 id='intake-launch-title' className='text-base font-semibold text-slate-900'>
            上传客户资料，让 AI 先分析
          </h2>
          <p className='mt-0.5 text-xs leading-5 text-slate-500'>
            AI 只提取资料中能找到的内容，找不到的标记为待补充，不会补造事实。
          </p>
        </div>
      </header>

      <div
        className={`mt-3 rounded-lg border border-dashed p-3 transition-colors ${
          dragActive ? 'border-teal-500 bg-teal-50' : 'border-slate-300 bg-slate-50'
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragActive(false);
          addFiles(event.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          type='file'
          accept={ACCEPT}
          multiple
          className='sr-only'
          onChange={(event) => addFiles(event.target.files)}
        />
        <button
          type='button'
          onClick={() => inputRef.current?.click()}
          disabled={!canWrite || submitting}
          className='inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600'
        >
          <Upload className='h-4 w-4' aria-hidden='true' />
          选择或拖拽文件
        </button>
        <p className='mt-2 text-[11px] leading-4 text-slate-500'>
          支持 PDF、DOCX、XLSX、CSV、TXT、Markdown、PNG、JPG；最多 {MAX_FILES} 个，单个不超过 10MB，上传前做基础安全扫描。
        </p>
        {files.length > 0 && (
          <ul className='mt-2 space-y-1.5'>
            {files.map((file, index) => (
              <li key={`${file.name}-${index}`} className='flex items-center gap-2 rounded-md border border-slate-200 bg-white px-2 py-1.5 text-xs text-slate-700'>
                <FileText className='h-3.5 w-3.5 shrink-0 text-slate-400' aria-hidden='true' />
                <span className='min-w-0 flex-1 truncate'>{file.name}</span>
                <span className='shrink-0 text-slate-400'>{Math.ceil(file.size / 1024)} KB</span>
                <button
                  type='button'
                  onClick={() => removeFile(index)}
                  className='shrink-0 rounded p-0.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600'
                  aria-label={`移除 ${file.name}`}
                >
                  <X className='h-3.5 w-3.5' aria-hidden='true' />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className='mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2'>
        <label className='block'>
          <span className='text-xs font-medium text-slate-700'>与品牌的关系</span>
          <select
            value={relationship}
            onChange={(event) => setRelationship(event.target.value)}
            disabled={!canWrite || submitting}
            className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
          >
            {RELATIONSHIPS.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>
        <label className='block'>
          <span className='text-xs font-medium text-slate-700'>补充说明（可选）</span>
          <input
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            disabled={!canWrite || submitting}
            placeholder='例如：客户已提供工商信息与官网'
            className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
          />
        </label>
      </div>

      <label className='mt-3 block'>
        <span className='text-xs font-medium text-slate-700'>粘贴文字（可选）</span>
        <textarea
          value={pastedText}
          onChange={(event) => setPastedText(event.target.value)}
          disabled={!canWrite || submitting}
          rows={4}
          placeholder='粘贴品牌、主体、产品、客户、地区、渠道等资料'
          className='mt-1 w-full resize-y rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
        />
      </label>

      {error && (
        <p className='mt-3 flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs leading-5 text-rose-700'>
          <AlertTriangle className='mt-0.5 h-3.5 w-3.5 shrink-0' aria-hidden='true' />
          {error}
        </p>
      )}

      <div className='mt-3 flex items-center justify-end gap-2'>
        <button
          type='button'
          onClick={submit}
          disabled={!canWrite || submitting}
          className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 ${
            canWrite ? 'bg-teal-700 text-white hover:bg-teal-800' : 'bg-slate-200 text-slate-500 cursor-not-allowed'
          }`}
        >
          {submitting ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <Sparkles className='h-4 w-4' aria-hidden='true' />}
          {submitting ? '上传并分析中' : '开始分析'}
        </button>
      </div>

      {!canWrite && (
        <div className='mt-3'>
          <ModuleState variant='blocked' title='只读视图' description='上传与分析需要域主或编辑权限。' compact />
        </div>
      )}
    </section>
  );
}
