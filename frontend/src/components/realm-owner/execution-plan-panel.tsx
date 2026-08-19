'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  CalendarRange,
  CheckCircle2,
  Download,
  FilePlus2,
  Loader2,
  Plus,
  RefreshCw,
  Sparkles,
  TriangleAlert,
} from 'lucide-react';
import {
  createGeoProject,
  exportExecutionPlan,
  fetchExecutionPlan,
  generateExecutionPlan,
  syncWorkItem,
  updateWorkItem,
} from '@/lib/realm-owner/queries-v105';
import type {
  ExecutionPlanView,
  GeoProjectSummary,
  IntakeItem,
  WorkPlanItem,
} from '@/lib/realm-owner/types';
import ModuleState from './module-state';
import TruthBadge from './truth-badge';

const STATUS_LABELS: Record<string, string> = {
  planned: '待启动',
  in_progress: '进行中',
  waiting: '等待中',
  blocked: '受阻',
  completed: '已完成',
  archived: '已归档',
};

function formatDate(iso?: string | null): string {
  if (!iso) return '未排期';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso.slice(0, 10);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function intakeValue(intake: IntakeItem | null, key: string): string {
  const latest = intake?.latest_analysis ?? intake?.analyses?.[0] ?? null;
  const field = latest?.analysis_json?.fields.find((item) => item.key === key);
  return field?.value || '';
}

export default function ExecutionPlanPanel({
  realmId,
  canWrite,
  projects,
  intake,
  onRefreshProjects,
}: {
  realmId: string;
  canWrite: boolean;
  projects: GeoProjectSummary[];
  intake: IntakeItem | null;
  onRefreshProjects: () => void;
}) {
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [plan, setPlan] = useState<ExecutionPlanView | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [busyItemId, setBusyItemId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [projectName, setProjectName] = useState('');
  const [objective, setObjective] = useState('');

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId) || null,
    [projects, selectedProjectId],
  );

  useEffect(() => {
    if (projects.length === 0) {
      setSelectedProjectId('');
      setPlan(null);
      return;
    }
    if (selectedProjectId && projects.some((project) => project.id === selectedProjectId)) return;
    setSelectedProjectId(projects[0].id);
  }, [projects, selectedProjectId]);

  async function loadPlan(projectId: string) {
    if (!projectId) {
      setPlan(null);
      return;
    }
    setPlanLoading(true);
    setPlanError(null);
    try {
      setPlan(await fetchExecutionPlan(projectId));
    } catch (err) {
      const payload = err as { message?: string };
      setPlanError(payload.message || '计划读取失败');
      setPlan(null);
    } finally {
      setPlanLoading(false);
    }
  }

  useEffect(() => {
    void loadPlan(selectedProjectId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId]);

  async function createProject() {
    if (!projectName.trim()) {
      setMessage('请输入项目名称');
      return;
    }
    setCreating(true);
    setMessage(null);
    try {
      const created = await createGeoProject(realmId, {
        name: projectName.trim(),
        objective: objective.trim() || undefined,
        target_brand: intakeValue(intake, 'brand_name') || undefined,
        target_product: intakeValue(intake, 'product_service') || undefined,
        target_audience: intakeValue(intake, 'target_customer') || undefined,
      });
      setSelectedProjectId(created.id);
      setFormOpen(false);
      setProjectName('');
      setObjective('');
      onRefreshProjects();
      setMessage('项目已建立，正在生成 AI 计划草稿');
      const draft = await generateExecutionPlan(created.id);
      setPlan(draft);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '创建项目失败');
    } finally {
      setCreating(false);
    }
  }

  async function regeneratePlan() {
    if (!selectedProject) return;
    const allow = window.confirm('重新生成会覆盖当前 AI 草稿（已人工编辑的任务不会被覆盖）。继续吗？');
    if (!allow) return;
    setGenerating(true);
    setMessage(null);
    try {
      setPlan(await generateExecutionPlan(selectedProject.id, true));
      setMessage('已重新生成 AI 计划草稿');
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '重新生成失败');
    } finally {
      setGenerating(false);
    }
  }

  async function updateItem(item: WorkPlanItem, data: { status?: string; progress?: number }) {
    if (!selectedProject) return;
    setBusyItemId(item.id);
    setMessage(null);
    try {
      await updateWorkItem(selectedProject.id, item.id, data);
      await loadPlan(selectedProject.id);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '任务更新失败');
    } finally {
      setBusyItemId(null);
    }
  }

  async function manualSync(item: WorkPlanItem) {
    if (!selectedProject) return;
    setBusyItemId(item.id);
    setMessage(null);
    try {
      await syncWorkItem(selectedProject.id, item.id, {
        source: 'owner_manual_sync',
        status: item.status,
        progress: item.progress,
      });
      await loadPlan(selectedProject.id);
      setMessage('已同步到执行记录');
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '同步失败');
    } finally {
      setBusyItemId(null);
    }
  }

  async function exportPlan() {
    if (!selectedProject) return;
    try {
      const csv = await exportExecutionPlan(selectedProject.id);
      const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${selectedProject.project_code || selectedProject.name}-执行计划.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      const payload = err as { message?: string };
      setMessage(payload.message || '导出失败');
    }
  }

  const aiDraftOnly =
    plan !== null &&
    plan.work_items.length > 0 &&
    plan.work_items.every(
      (item) => item.status === 'planned' && item.truth_status === 'inferred',
    );

  return (
    <section className='realm-card p-4' aria-labelledby='execution-plan-title'>
      <header className='flex flex-wrap items-start justify-between gap-2'>
        <div>
          <h2 id='execution-plan-title' className='text-base font-semibold text-slate-900'>执行计划与日程</h2>
          <p className='mt-0.5 text-xs leading-5 text-slate-500'>
            AI 只推荐计划草稿；启动、调整、同步和导出都需要域主确认。
          </p>
        </div>
        {plan && plan.reminders.length > 0 && (
          <span className='inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-2 py-1 text-[11px] font-medium text-amber-700'>
            <TriangleAlert className='h-3.5 w-3.5' aria-hidden='true' />
            {plan.reminders.length} 个提醒
          </span>
        )}
      </header>

      {projects.length === 0 && !formOpen ? (
        <div className='mt-3'>
          <ModuleState
            variant='empty'
            title='还没有执行项目'
            description='域主确认客户档案后，可建立项目并由 AI 推荐启动计划。'
            compact
          />
          {canWrite && (
            <button
              type='button'
              onClick={() => setFormOpen(true)}
              className='mt-3 inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800'
            >
              <Plus className='h-4 w-4' aria-hidden='true' />
              建立项目
            </button>
          )}
        </div>
      ) : (
        <div className='mt-3'>
          <div className='flex flex-wrap items-center gap-2'>
            <label className='flex min-w-0 flex-1 items-center gap-2'>
              <span className='shrink-0 text-xs font-medium text-slate-600'>项目</span>
              <select
                value={selectedProjectId}
                onChange={(event) => setSelectedProjectId(event.target.value)}
                className='min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
              >
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}（{project.status}）
                  </option>
                ))}
              </select>
            </label>
            {canWrite && (
              <button
                type='button'
                onClick={() => setFormOpen((open) => !open)}
                className='inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'
              >
                <FilePlus2 className='h-4 w-4' aria-hidden='true' />
                新建项目
              </button>
            )}
            {plan && plan.work_items.length > 0 && (
              <button
                type='button'
                onClick={exportPlan}
                className='inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'
              >
                <Download className='h-4 w-4' aria-hidden='true' />
                导出表格
              </button>
            )}
          </div>

          {formOpen && (
            <div className='mt-3 rounded-lg border border-teal-200 bg-teal-50/50 p-3'>
              <div className='grid grid-cols-1 gap-2 md:grid-cols-2'>
                <label className='block'>
                  <span className='text-xs font-medium text-slate-700'>项目名称</span>
                  <input
                    value={projectName}
                    onChange={(event) => setProjectName(event.target.value)}
                    placeholder='例如：恒域世界 GEO 首轮试点'
                    className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
                  />
                </label>
                <label className='block'>
                  <span className='text-xs font-medium text-slate-700'>项目目标</span>
                  <input
                    value={objective}
                    onChange={(event) => setObjective(event.target.value)}
                    placeholder='例如：建立品牌可信资产并完成首轮可见度检测'
                    className='mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100'
                  />
                </label>
              </div>
              <p className='mt-2 text-[11px] leading-4 text-slate-500'>
                创建后 AI 会基于已确认客户档案推荐计划草稿，所有任务默认标记为 inferred，不会自动执行。
              </p>
              <div className='mt-2 flex items-center justify-end gap-2'>
                <button
                  type='button'
                  onClick={() => setFormOpen(false)}
                  className='rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50'
                >
                  取消
                </button>
                <button
                  type='button'
                  onClick={createProject}
                  disabled={creating || !canWrite}
                  className='inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60'
                >
                  {creating ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <Sparkles className='h-4 w-4' aria-hidden='true' />}
                  {creating ? '创建并生成计划中' : '创建项目并生成计划草稿'}
                </button>
              </div>
            </div>
          )}

          {selectedProject && !planLoading && plan === null && (
            <div className='mt-3'>
              <ModuleState
                variant='empty'
                title='还没有计划'
                description='让 AI 根据项目目标与客户档案生成可编辑的启动计划。'
                compact
              />
              {canWrite && (
                <button
                  type='button'
                  onClick={regeneratePlan}
                  disabled={generating}
                  className='mt-3 inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60'
                >
                  {generating ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <Sparkles className='h-4 w-4' aria-hidden='true' />}
                  生成 AI 计划草稿
                </button>
              )}
            </div>
          )}

          {planLoading && (
            <div className='mt-3'>
              <ModuleState variant='loading' title='正在读取计划' />
            </div>
          )}

          {planError && !planLoading && (
            <div className='mt-3'>
              <ModuleState
                variant='error'
                title='计划读取失败'
                description={planError}
                actionLabel='重试'
                onAction={() => void loadPlan(selectedProjectId)}
                compact
              />
            </div>
          )}

          {plan && plan.work_items.length > 0 && (
            <>
              {aiDraftOnly && (
                <div className='mt-3 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2.5'>
                  <p className='text-xs leading-5 text-violet-800'>
                    <Sparkles className='mr-1 inline h-3.5 w-3.5' aria-hidden='true' />
                    AI 计划草稿已生成，所有任务等待域主确认与启动。
                  </p>
                  <button
                    type='button'
                    onClick={regeneratePlan}
                    disabled={generating || !canWrite}
                    className='inline-flex items-center gap-1.5 rounded-lg border border-violet-300 bg-white px-3 py-1.5 text-xs font-medium text-violet-700 hover:bg-violet-100 disabled:opacity-60'
                  >
                    {generating ? <Loader2 className='h-3.5 w-3.5 animate-spin' aria-hidden='true' /> : <RefreshCw className='h-3.5 w-3.5' aria-hidden='true' />}
                    重新生成草稿
                  </button>
                </div>
              )}

              <div className='mt-3 space-y-3'>
                {plan.work_items.map((item) => (
                  <WorkItemCard
                    key={item.id}
                    item={item}
                    canWrite={canWrite}
                    busy={busyItemId === item.id}
                    onStatusChange={(status) => void updateItem(item, { status })}
                    onProgressChange={(progress) => void updateItem(item, { progress })}
                    onSync={() => void manualSync(item)}
                  />
                ))}
              </div>
            </>
          )}

          {message && (
            <p className='mt-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800'>
              <TriangleAlert className='mt-0.5 h-3.5 w-3.5 shrink-0' aria-hidden='true' />
              {message}
            </p>
          )}
        </div>
      )}
    </section>
  );
}

function WorkItemCard({
  item,
  canWrite,
  busy,
  onStatusChange,
  onProgressChange,
  onSync,
}: {
  item: WorkPlanItem;
  canWrite: boolean;
  busy: boolean;
  onStatusChange: (status: string) => void;
  onProgressChange: (progress: number) => void;
  onSync: () => void;
}) {
  const [draftProgress, setDraftProgress] = useState(item.progress);

  useEffect(() => {
    setDraftProgress(item.progress);
  }, [item.progress]);

  return (
    <article className='rounded-lg border border-slate-200 bg-white p-3'>
      <div className='flex flex-wrap items-start justify-between gap-2'>
        <div className='min-w-0 flex-1'>
          <div className='flex flex-wrap items-center gap-1.5'>
            <span className='text-[13px] font-semibold text-slate-800'>{item.title}</span>
            <TruthBadge scope={item.truth_status === 'inferred' ? 'inferred' : 'observed'} />
            <span className='rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500'>{item.phase}</span>
          </div>
          {item.purpose && <p className='mt-1 text-[11px] leading-4 text-slate-600'>{item.purpose}</p>}
        </div>
        <div className='flex shrink-0 items-center gap-1.5'>
          <select
            value={item.status}
            onChange={(event) => onStatusChange(event.target.value)}
            disabled={!canWrite || busy}
            className='rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 disabled:opacity-60'
          >
            {Object.entries(STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <button
            type='button'
            onClick={onSync}
            disabled={!canWrite || busy}
            title='手动同步执行状态到后台'
            className='rounded-lg border border-slate-300 bg-white p-1.5 text-slate-600 hover:bg-slate-50 disabled:opacity-60'
          >
            {busy ? <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' /> : <RefreshCw className='h-4 w-4' aria-hidden='true' />}
          </button>
        </div>
      </div>

      <div className='mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-500'>
        <span className='inline-flex items-center gap-1'>
          <CalendarRange className='h-3 w-3' aria-hidden='true' />
          {formatDate(item.start_at)} 至 {formatDate(item.due_at)}
        </span>
        {item.owner_label && <span>负责人：{item.owner_label}</span>}
        {item.execution_mode && <span>执行方式：{item.execution_mode}</span>}
        {item.last_synced_at && <span>同步：{formatDate(item.last_synced_at)}</span>}
      </div>

      <div className='mt-2 flex items-center gap-2'>
        <span className='w-10 text-[11px] text-slate-500'>{draftProgress}%</span>
        <input
          type='range'
          min={0}
          max={100}
          step={5}
          value={draftProgress}
          disabled={!canWrite || busy}
          onChange={(event) => setDraftProgress(Number(event.target.value))}
          onMouseUp={() => onProgressChange(draftProgress)}
          onTouchEnd={() => onProgressChange(draftProgress)}
          onBlur={() => onProgressChange(draftProgress)}
          className='h-1.5 min-w-0 flex-1 accent-teal-700 disabled:opacity-60'
        />
        {item.status === 'completed' && (
          <CheckCircle2 className='h-4 w-4 shrink-0 text-emerald-600' aria-hidden='true' />
        )}
      </div>

      {item.reason && (
        <p className='mt-2 rounded bg-slate-50 px-2 py-1.5 text-[11px] leading-4 text-slate-600'>推荐原因：{item.reason}</p>
      )}
      {item.acceptance_criteria && (
        <p className='mt-1.5 text-[11px] leading-4 text-slate-500'>验收：{item.acceptance_criteria}</p>
      )}
      {item.risks.length > 0 && (
        <p className='mt-1.5 text-[11px] leading-4 text-rose-600'>风险：{item.risks.join('；')}</p>
      )}
      {item.reminders && item.reminders.length > 0 && (
        <div className='mt-1.5 flex flex-wrap gap-1.5'>
          {item.reminders.map((reminder) => (
            <span key={`${reminder.type}-${reminder.message}`} className='rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700'>
              {reminder.message}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}
