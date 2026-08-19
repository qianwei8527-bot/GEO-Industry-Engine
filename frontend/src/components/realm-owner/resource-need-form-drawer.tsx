"use client";

import { useState } from "react";
import { Loader2, Send } from "lucide-react";
import RealmDrawer from "./drawer";
import { createDemandEvent } from "@/lib/realm-owner/queries";
import {
  buildDemandCreateInput,
  validateResourceNeed,
} from "@/lib/realm-owner/adapter";
import type { ResourceNeedFormValues } from "@/lib/realm-owner/types";

const FLOW_STEPS = ["需求出现", "诊断决策", "解决方案", "生产交付", "分发触达", "反馈评估"];

interface ResourceNeedFormDrawerProps {
  open: boolean;
  onClose: () => void;
  realmId: string;
  onCreated: () => void;
}

const EMPTY_FORM: ResourceNeedFormValues = {
  businessGoal: "",
  flowStep: "",
  missingCapability: "",
  serviceRegion: "",
  timeRequirement: "",
  budgetRange: "",
  cooperationMode: "",
  requiredConditions: "",
  excludedConditions: "",
  sharedDataScope: "",
};

export default function ResourceNeedFormDrawer({
  open,
  onClose,
  realmId,
  onCreated,
}: ResourceNeedFormDrawerProps) {
  const [values, setValues] = useState<ResourceNeedFormValues>(EMPTY_FORM);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  function update(key: keyof ResourceNeedFormValues, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function submit() {
    const nextErrors = validateResourceNeed(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;
    setSaving(true);
    setSubmitError(null);
    try {
      await createDemandEvent(buildDemandCreateInput(values, realmId));
      setValues(EMPTY_FORM);
      onCreated();
      onClose();
    } catch (err) {
      const payload = err as { message?: string };
      setSubmitError(payload.message || "创建失败，请稍后重试。");
    } finally {
      setSaving(false);
    }
  }

  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="发布资源需求"
      description="域主确认后创建 Demand 对象；不会自动联系或承诺合作。"
      footer={
        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            取消
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Send className="h-4 w-4" aria-hidden="true" />}
            域主确认并创建
          </button>
        </div>
      }
    >
      <div className="space-y-3">
        <Field label="业务目标" required error={errors.businessGoal}>
          <input
            value={values.businessGoal}
            onChange={(event) => update("businessGoal", event.target.value)}
            placeholder="例如：让目标客户在 AI 搜索中首次被看见"
            className={inputClass(!!errors.businessGoal)}
          />
        </Field>

        <Field label="所在流程环节" required error={errors.flowStep}>
          <select
            value={values.flowStep}
            onChange={(event) => update("flowStep", event.target.value)}
            className={inputClass(!!errors.flowStep)}
          >
            <option value="">请选择</option>
            {FLOW_STEPS.map((step) => (
              <option key={step} value={step}>{step}</option>
            ))}
          </select>
        </Field>

        <Field label="缺少的能力或资源" required error={errors.missingCapability}>
          <input
            value={values.missingCapability}
            onChange={(event) => update("missingCapability", event.target.value)}
            placeholder="例如：行业专家访谈、渠道分发、内容生产"
            className={inputClass(!!errors.missingCapability)}
          />
        </Field>

        <Field label="服务地区">
          <input value={values.serviceRegion} onChange={(event) => update("serviceRegion", event.target.value)} placeholder="服务地区" className={inputClass(false)} />
        </Field>

        <Field label="时间要求">
          <input value={values.timeRequirement} onChange={(event) => update("timeRequirement", event.target.value)} placeholder="例如：30 天内" className={inputClass(false)} />
        </Field>

        <Field label="预算范围">
          <input value={values.budgetRange} onChange={(event) => update("budgetRange", event.target.value)} placeholder="预算范围" className={inputClass(false)} />
        </Field>

        <Field label="合作方式">
          <input value={values.cooperationMode} onChange={(event) => update("cooperationMode", event.target.value)} placeholder="例如：咨询、陪跑、按结果付费" className={inputClass(false)} />
        </Field>

        <Field label="必须条件">
          <input value={values.requiredConditions} onChange={(event) => update("requiredConditions", event.target.value)} placeholder="必须条件" className={inputClass(false)} />
        </Field>

        <Field label="排除条件">
          <input value={values.excludedConditions} onChange={(event) => update("excludedConditions", event.target.value)} placeholder="排除条件" className={inputClass(false)} />
        </Field>

        <Field label="允许共享的数据范围">
          <textarea
            value={values.sharedDataScope}
            onChange={(event) => update("sharedDataScope", event.target.value)}
            rows={2}
            placeholder="例如：仅共享公开信息与授权数据"
            className={inputClass(false)}
          />
        </Field>

        {submitError && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{submitError}</p>
        )}
        <p className="text-[11px] leading-5 text-slate-500">
          创建后 truth status 为 observed，不会自动验证；候选匹配会展示理由、证据、风险与未知项。
        </p>
      </div>
    </RealmDrawer>
  );
}

function Field({
  label,
  required,
  error,
  children,
}: {
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-700">
        {label}
        {required && <span className="ml-1 text-rose-500" aria-hidden="true">*</span>}
      </label>
      <div className="mt-1.5">{children}</div>
      {error && <p className="mt-1 text-[11px] text-rose-600">{error}</p>}
    </div>
  );
}

function inputClass(hasError: boolean): string {
  return `w-full rounded-lg border px-2.5 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 ${
    hasError
      ? "border-rose-300 bg-rose-50 focus:border-rose-500 focus:ring-rose-100"
      : "border-slate-300 bg-slate-50 focus:border-teal-600 focus:bg-white focus:ring-teal-100"
  }`;
}