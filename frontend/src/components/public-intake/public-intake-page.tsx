"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  CheckCircle2,
  FileText,
  Info,
  Loader2,
  Save,
  Send,
  ShieldCheck,
  Upload,
  X,
} from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import DataSourceBadge from "@/components/app-shell/DataSourceBadge";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import RealmDrawer from "@/components/realm-owner/drawer";
import {
  fetchPublicIntakeContext,
  savePublicIntakeDraft,
  submitPublicIntake,
} from "@/lib/public-intake/api";
import {
  EMPTY_PUBLIC_INTAKE_FORM,
  formatFileSize,
  validatePublicIntake,
} from "@/lib/public-intake/form";
import type {
  PublicIntakeContext,
  PublicIntakeFormValues,
  PublicIntakePageState,
  PublicIntakeRecord,
} from "@/lib/public-intake/types";

const RELATIONSHIPS = ["企业自身", "品牌方", "产品/项目负责人", "代理或服务方", "其他"];

function metaString(record: PublicIntakeRecord | null, key: string): string {
  const value = record?.form?.[key as keyof PublicIntakeRecord["form"]];
  return typeof value === "string" ? value : "";
}

export default function PublicIntakePage({ token }: { token: string }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [context, setContext] = useState<PublicIntakeContext | null>(null);
  const [phase, setPhase] = useState<PublicIntakePageState>("loading");
  const [phaseMessage, setPhaseMessage] = useState("");
  const [form, setForm] = useState<PublicIntakeFormValues>(EMPTY_PUBLIC_INTAKE_FORM);
  const [files, setFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState("");
  const [notice, setNotice] = useState("");
  const [submitted, setSubmitted] = useState<PublicIntakeRecord | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const submittedTitleRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (phase === "submitted" && submittedTitleRef.current) {
      submittedTitleRef.current.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }, [phase]);

  useEffect(() => {
    let cancelled = false;
    fetchPublicIntakeContext(token)
      .then((data) => {
        if (cancelled) return;
        setContext(data);
        if (data.latest_submission) {
          setSubmitted(data.latest_submission);
          setPhase("submitted");
          return;
        }
        if (data.latest_draft) {
          const draft = data.latest_draft;
          setForm({
            enterpriseName: metaString(draft, "enterprise_name"),
            brandName: metaString(draft, "brand_name"),
            productOrProjectName: metaString(draft, "product_or_project_name"),
            relationship: metaString(draft, "relationship") || draft.relationship || "",
            problem: metaString(draft, "problem"),
            websiteUrl: metaString(draft, "website_url"),
            pastedText: draft.pasted_text || "",
            supplementalNotes: draft.supplemental_notes || "",
            consentDataAnalysis: Boolean(draft.form?.consent_data_analysis),
            consentUseAuthorization: Boolean(draft.form?.consent_use_authorization),
            serverStagingConsent: Boolean(draft.form?.server_staging_consent),
          });
          setPhase("draft");
          return;
        }
        setPhase("empty");
      })
      .catch((err: { status?: number; message?: string }) => {
        if (cancelled) return;
        if (err.status === 410) {
          setPhase("expired");
        } else if (err.status === 403 || err.status === 401) {
          setPhase("no-permission");
        } else {
          setPhase("error");
          setPhaseMessage(err.message || "资料提交入口加载失败");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  const allowedTypes = context?.allowed_file_types || [];
  const accept = allowedTypes.join(",");

  function update<K extends keyof PublicIntakeFormValues>(key: K, value: PublicIntakeFormValues[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  function addFiles(next: FileList | null) {
    if (!next) return;
    const merged = [...files, ...Array.from(next)].slice(0, context?.max_files || 5);
    setFiles(merged);
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function saveDraft() {
    if (!context) return;
    setServerError("");
    setNotice("");
    try {
      await savePublicIntakeDraft(token, form, files);
      const refreshed = await fetchPublicIntakeContext(token);
      setContext(refreshed);
      setFiles([]);
      setPhase(refreshed.latest_draft ? "draft" : "empty");
      setNotice("草稿已保存在安全令牌对应的 Realm 下");
    } catch (err) {
      const payload = err as { message?: string };
      setServerError(payload.message || "草稿保存失败");
    }
  }

  async function submit() {
    if (!context) return;
    const nextErrors = validatePublicIntake(form, context, files);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;
    setPhase("submitting");
    setServerError("");
    setNotice("");
    try {
      const result = await submitPublicIntake(token, form, files);
      if (result.status === "analysis_failed") {
        setPhase("error");
        setPhaseMessage("文件解析失败或没有可用文字，请补充资料后重试。");
        return;
      }
      setSubmitted(result);
      setPhase("submitted");
    } catch (err) {
      const payload = err as { status?: number; message?: string };
      setServerError(payload.message || "提交失败");
      setPhase(context.latest_draft ? "draft" : "empty");
    }
  }

  const realmName = context?.realm.display_name || "目标域";
  const missingDraftFields = [
    !form.enterpriseName.trim() && !form.brandName.trim() && !form.productOrProjectName.trim()
      ? "企业、品牌、产品或项目名称"
      : null,
    !form.relationship.trim() ? "与项目的关系" : null,
    !form.problem.trim() ? "最想解决的问题" : null,
  ].filter((item): item is string => Boolean(item));
  const latestAnalysis = submitted?.latest_analysis ?? null;
  const unknownFields = (latestAnalysis?.fields || []).filter(
    (field) => field.status === "unknown" || field.value === "待补充",
  );
  const rejectedFiles = (submitted?.file_manifest || []).filter(
    (file) => file.parse_status === "rejected" || file.parse_status === "parse_failed",
  );
  const statusItems = useMemo(
    () => [
      {
        label: "数据连接",
        value: context ? "安全令牌已绑定" : "未连接",
        tone: context ? ("success" as const) : ("warning" as const),
      },
      {
        label: "truth scope",
        value: submitted ? "observed" : "unknown",
        tone: submitted ? ("success" as const) : ("warning" as const),
      },
      {
        label: "外部 AI",
        value: context?.analysis.external_ai_ready ? "已配置" : "未配置",
        tone: context?.analysis.external_ai_ready ? ("success" as const) : ("warning" as const),
      },
      { label: "版本", value: "V10.6-R1" },
    ],
    [context, submitted],
  );

  const navRail = (
    <aside className="hidden w-52 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">公共资料提交</span>
      </div>
      <div className="px-3 py-3">
        <div className="flex items-center gap-2 rounded-md bg-[color:var(--v106-primary-weak)] px-2.5 py-2 text-sm font-medium text-[color:var(--v106-primary-strong)]">
          <FileText className="h-4 w-4" aria-hidden="true" />
          资料提交
        </div>
      </div>
      <div className="mt-auto px-4 py-3 text-[11px] leading-4 text-slate-500">
        仅开放真实资料提交入口
      </div>
    </aside>
  );

  const contextBar = (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
      <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
        公共世界 <span className="mx-1 text-slate-300">/</span> {realmName}{" "}
        <span className="mx-1 text-slate-300">/</span> 资料提交
      </div>
      <DataSourceBadge
        name="安全令牌"
        state={context ? "connected" : phase === "error" ? "blocked" : "pending"}
      />
      <button
        type="button"
        onClick={() => setDrawerOpen(true)}
        className="inline-flex h-8 items-center gap-1.5 rounded-md border border-[color:var(--v106-border)] bg-white px-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
      >
        <Info className="h-4 w-4" aria-hidden="true" />
        提交须知
      </button>
    </header>
  );

  return (
    <AppShell
      surface="public"
      featureFlags={["intake"]}
      realmContext={
        context
          ? {
              id: context.realm.realm_code,
              name: realmName,
              realmType: context.realm.realm_type,
            }
          : undefined
      }
      userContext={{ label: "匿名提交者", permissions: ["intake_submit"] }}
      navRail={navRail}
      contextBar={contextBar}
      statusStrip={<StatusStrip items={statusItems} />}
      rightDrawer={
        <RealmDrawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title="资料提交与授权"
          description="令牌由域主创建并绑定到 Realm，前端不接收或信任 realm_id。"
        >
          <div className="space-y-3">
            <p className="text-sm leading-6 text-slate-700">
              提交后资料进入该 Realm 的 Intake 队列，truth scope 为 observed，域主确认后才可用于项目。
            </p>
            <p className="text-xs leading-5 text-slate-500">
              未配置外部 AI Key 时，系统只执行真实本地结构化提取，不生成模拟 AI 分析结果。
            </p>
          </div>
        </RealmDrawer>
      }
    >
      {phase === "loading" && <ModuleState variant="loading" title="正在加载资料提交入口" />}

      {phase === "no-permission" && (
        <ModuleState
          variant="no-permission"
          title="无权使用该提交入口"
          description="令牌无效、已撤销或不属于当前 Realm。"
        />
      )}

      {phase === "expired" && (
        <ModuleState
          variant="blocked"
          title="提交令牌已过期"
          description="请联系域主重新生成有效令牌。"
        />
      )}

      {phase === "error" && (
        <ModuleState
          variant="error"
          title="资料提交入口加载失败"
          description={phaseMessage}
          actionLabel="重试"
          onAction={() => window.location.reload()}
        />
      )}

      {(phase === "empty" || phase === "draft") && context && (
        <div className="mx-auto max-w-5xl">
          <header className="mb-4">
            <h1 className="v106-page-title">向 {realmName} 提交客户资料</h1>
            <p className="mt-1 text-sm text-slate-500">
              {phase === "draft" ? "已加载安全令牌下的真实草稿" : "资料会以 observed 进入待确认队列"}
            </p>
          </header>

          {!context.analysis.external_ai_ready && (
            <div className="mb-4">
              <ModuleState
                variant="partial"
                title="外部 AI 未配置"
                description={context.analysis.notice}
                compact
              />
            </div>
          )}

          {phase === "draft" && missingDraftFields.length > 0 && (
            <div className="mb-4">
              <ModuleState
                variant="partial"
                title={`还有 ${missingDraftFields.length} 项待补充`}
                description={`缺失：${missingDraftFields.join("、")}`}
                compact
              />
            </div>
          )}

          {notice && (
            <p className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
              {notice}
            </p>
          )}

          <section className="v106-panel p-4 lg:p-5">
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
              <Field label="企业名称">
                <input
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.enterpriseName}
                  onChange={(event) => update("enterpriseName", event.target.value)}
                  placeholder="企业或主体名称"
                />
              </Field>
              <Field label="品牌名称">
                <input
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.brandName}
                  onChange={(event) => update("brandName", event.target.value)}
                  placeholder="品牌名称"
                />
              </Field>
              <Field label="产品或项目名称">
                <input
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.productOrProjectName}
                  onChange={(event) => update("productOrProjectName", event.target.value)}
                  placeholder="核心产品或项目名称"
                />
              </Field>
              <Field label="与项目的关系" error={errors.relationship}>
                <select
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.relationship}
                  onChange={(event) => update("relationship", event.target.value)}
                >
                  <option value="">请选择</option>
                  {RELATIONSHIPS.map((item) => (
                    <option key={item} value={item}>{item}</option>
                  ))}
                </select>
              </Field>
              <div className="lg:col-span-2">
                <Field label="最想解决的问题" error={errors.problem}>
                  <textarea
                    className="v106-control min-h-20 w-full resize-y px-2.5 py-2 text-sm"
                    value={form.problem}
                    onChange={(event) => update("problem", event.target.value)}
                    placeholder="描述最想解决的业务问题"
                  />
                </Field>
              </div>
              <Field label="官网或公开渠道链接" error={errors.websiteUrl}>
                <input
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.websiteUrl}
                  onChange={(event) => update("websiteUrl", event.target.value)}
                  placeholder="https://example.com"
                />
              </Field>
              <Field label="补充说明">
                <input
                  className="v106-control w-full px-2.5 py-2 text-sm"
                  value={form.supplementalNotes}
                  onChange={(event) => update("supplementalNotes", event.target.value)}
                  placeholder="补充资料说明"
                />
              </Field>
              <div className="lg:col-span-2">
                <Field label="粘贴文字">
                  <textarea
                    className="v106-control min-h-16 w-full resize-y px-2.5 py-2 text-sm"
                    value={form.pastedText}
                    onChange={(event) => update("pastedText", event.target.value)}
                    placeholder="粘贴企业、品牌、产品、客户、渠道等资料"
                  />
                </Field>
              </div>
            </div>

            <div className="mt-4">
              <input
                ref={fileInputRef}
                type="file"
                accept={accept}
                multiple
                className="sr-only"
                onChange={(event) => addFiles(event.target.files)}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-2 rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <Upload className="h-4 w-4" aria-hidden="true" />
                选择文件
              </button>
              <p className="mt-1.5 text-xs text-slate-500">
                支持 {allowedTypes.join("、")}；最多 {context.max_files} 个，单个不超过 {formatFileSize(context.max_file_bytes)}
              </p>
              {context.latest_draft?.file_manifest && context.latest_draft.file_manifest.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-slate-700">已暂存文件</p>
                  <ul className="mt-1.5 space-y-1.5">
                    {context.latest_draft.file_manifest.map((file) => (
                      <li key={file.file_id} className="flex items-center gap-2 rounded-md border border-[color:var(--v106-border)] bg-white px-2 py-1.5 text-xs">
                        <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
                        <span className="min-w-0 flex-1 truncate">{file.file_name}</span>
                        <span className="shrink-0 text-slate-400">{formatFileSize(file.size)}</span>
                        <span className="shrink-0 text-emerald-600">已暂存</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {files.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-slate-700">本次新增文件</p>
                  <ul className="mt-1.5 space-y-1.5">
                  {files.map((file, index) => (
                    <li key={`${file.name}-${index}`} className="flex items-center gap-2 rounded-md border border-[color:var(--v106-border)] bg-white px-2 py-1.5 text-xs">
                      <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
                      <span className="min-w-0 flex-1 truncate">{file.name}</span>
                      <span className="shrink-0 text-slate-400">{formatFileSize(file.size)}</span>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="shrink-0 rounded p-0.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                        aria-label={`移除 ${file.name}`}
                      >
                        <X className="h-3.5 w-3.5" aria-hidden="true" />
                      </button>
                    </li>
                  ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="mt-4 space-y-2 rounded-md border border-[color:var(--v106-border)] bg-[color:var(--v106-surface-muted)] p-3">
              <label className="flex items-start gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.consentDataAnalysis}
                  onChange={(event) => update("consentDataAnalysis", event.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-[color:var(--v106-primary)]"
                />
                同意对提交资料进行数据分析和结构化提取
              </label>
              <label className="flex items-start gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.consentUseAuthorization}
                  onChange={(event) => update("consentUseAuthorization", event.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-[color:var(--v106-primary)]"
                />
                同意授权目标域主在项目范围内使用该资料
              </label>
              <label className="flex items-start gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.serverStagingConsent}
                  onChange={(event) => update("serverStagingConsent", event.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-[color:var(--v106-primary)]"
                />
                同意将草稿和文件暂存到目标域服务器，仅用于本资料提交
              </label>
              {errors.consent && <p className="text-xs text-rose-600">{errors.consent}</p>}
            </div>

            {(errors.names || errors.files || serverError) && (
              <p className="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
                {errors.names || errors.files || serverError}
              </p>
            )}

            <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
              <button
                type="button"
                onClick={saveDraft}
                className="inline-flex items-center gap-1.5 rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
                保存草稿
              </button>
              <button
                type="button"
                onClick={submit}
                className="inline-flex items-center gap-1.5 rounded-md bg-[color:var(--v106-primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
              >
                <Send className="h-4 w-4" aria-hidden="true" />
                提交分析
              </button>
            </div>
          </section>
        </div>
      )}

      {phase === "submitting" && context && (
        <div className="mx-auto max-w-3xl">
          <ModuleState
            variant="loading"
            title="正在提交并进行本地结构化提取"
            description="请求已进入后端，等待真实解析结果。"
          />
        </div>
      )}

      {phase === "submitted" && submitted && context && (
        <div className="mx-auto max-w-3xl">
          <section className="v106-panel p-5">
            {unknownFields.length > 0 && (
              <div className="mb-4">
                <ModuleState
                  variant="partial"
                  title={`需要补充资料：${unknownFields.length} 项`}
                  description={`待补充：${unknownFields.map((field) => field.label).join("、")}`}
                  compact
                />
              </div>
            )}
            {rejectedFiles.length > 0 && (
              <div className="mb-4">
                <ModuleState
                  variant="error"
                  title="部分文件解析失败"
                  description={rejectedFiles
                    .map((file) => `${file.file_name}（${file.parse_error || file.parse_status}）`)
                    .join("；")}
                  compact
                />
              </div>
            )}
            <div className="flex items-start gap-3">
              <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald-50 text-emerald-600">
                <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
              </span>
              <div className="min-w-0">
                <h1 ref={submittedTitleRef} className="v106-page-title">资料已提交</h1>
                <p className="mt-1 text-sm text-slate-500">
                  {submitted.intake_code} · 等待域主确认
                </p>
              </div>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md border border-[color:var(--v106-border)] bg-[color:var(--v106-surface-muted)] p-3">
                <dt className="text-xs text-slate-500">处理状态</dt>
                <dd className="mt-1 font-medium text-slate-800">
                  {String(submitted.processing_status || submitted.status)}
                </dd>
              </div>
              <div className="rounded-md border border-[color:var(--v106-border)] bg-[color:var(--v106-surface-muted)] p-3">
                <dt className="text-xs text-slate-500">truth scope</dt>
                <dd className="mt-1 font-medium text-slate-800">{submitted.source_truth_status}</dd>
              </div>
            </dl>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              刷新本页后可从同一安全令牌恢复该提交状态。
            </p>
          </section>
        </div>
      )}
    </AppShell>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-700">{label}</label>
      <div className="mt-1.5">{children}</div>
      {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
    </div>
  );
}
