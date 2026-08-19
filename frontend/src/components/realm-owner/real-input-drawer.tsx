"use client";

import { useState } from "react";
import { Loader2, Save } from "lucide-react";
import RealmDrawer from "./drawer";
import { submitRealmEvidence } from "@/lib/realm-owner/queries";

interface RealInputDrawerProps {
  open: boolean;
  onClose: () => void;
  realmId: string;
  onSaved: () => void;
}

interface RealInputFields {
  brand: string;
  entity: string;
  relationship: string;
  product: string;
  customer: string;
  region: string;
  problem: string;
  channel: string;
  conversionGoal: string;
}

const FIELD_DEFS: Array<{ key: keyof RealInputFields; label: string; placeholder: string }> = [
  { key: "brand", label: "试点品牌", placeholder: "真实品牌名称" },
  { key: "entity", label: "主体", placeholder: "企业或主体名称" },
  { key: "relationship", label: "关系", placeholder: "与品牌的关系" },
  { key: "product", label: "产品", placeholder: "核心产品/服务" },
  { key: "customer", label: "客户", placeholder: "目标客户" },
  { key: "region", label: "地区", placeholder: "服务地区" },
  { key: "problem", label: "问题", placeholder: "要解决的真实问题" },
  { key: "channel", label: "渠道", placeholder: "主要渠道" },
  { key: "conversionGoal", label: "转化目标", placeholder: "主要转化目标" },
];

const EMPTY_FIELDS: RealInputFields = {
  brand: "",
  entity: "",
  relationship: "",
  product: "",
  customer: "",
  region: "",
  problem: "",
  channel: "",
  conversionGoal: "",
};

export default function RealInputDrawer({ open, onClose, realmId, onSaved }: RealInputDrawerProps) {
  const [values, setValues] = useState<RealInputFields>(EMPTY_FIELDS);
  const [unknowns, setUnknowns] = useState<Partial<Record<keyof RealInputFields, boolean>>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update(key: keyof RealInputFields, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function toggleUnknown(key: keyof RealInputFields) {
    setUnknowns((prev) => ({ ...prev, [key]: !prev[key] }));
    if (!unknowns[key]) setValues((prev) => ({ ...prev, [key]: "" }));
  }

  async function save() {
    const known = FIELD_DEFS.filter((field) => values[field.key].trim());
    const unknown = FIELD_DEFS.filter((field) => unknowns[field.key]);
    if (known.length === 0 && unknown.length === 0) {
      setError("至少填写一项真实输入，或选择“不知道”以记录缺口。");
      return;
    }
    setSaving(true);
    setError(null);
    const knownClaims = known.map((field) => `${field.label}：${values[field.key].trim()}`);
    const gapClaims = unknown.map((field) => `${field.label}待补齐`);
    const claim = [...knownClaims, ...(gapClaims.length ? [`缺口：${gapClaims.join("；")}`] : [])].join("；");
    try {
      await submitRealmEvidence(realmId, {
        claim,
        source_url: `urn:realm-owner-input:${realmId}`,
        source_name: "域主真实输入表单",
        source_type: "owner_form",
        truth_status: "observed",
      });
      setValues(EMPTY_FIELDS);
      setUnknowns({});
      onSaved();
      onClose();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "保存失败，请稍后重试。");
    } finally {
      setSaving(false);
    }
  }

  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="补齐真实输入"
      description="填写真实试点资料；“不知道”会记录为缺口，不会由 AI 自动补成事实。"
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
            onClick={save}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Save className="h-4 w-4" aria-hidden="true" />}
            保存为已观察
          </button>
        </div>
      }
    >
      <div className="space-y-3">
        <p className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-[11px] leading-5 text-blue-700">
          保存后记录为 observed，不自动验证；只有通过现有验证流程才会升级为 verified。
        </p>

        {FIELD_DEFS.map((field) => (
          <div key={field.key} className="rounded-lg border border-slate-200 p-2.5">
            <div className="flex items-center justify-between gap-2">
              <label htmlFor={`real-${field.key}`} className="text-xs font-medium text-slate-700">
                {field.label}
              </label>
              <label className="inline-flex items-center gap-1 text-[11px] text-slate-500">
                <input
                  type="checkbox"
                  checked={Boolean(unknowns[field.key])}
                  onChange={() => toggleUnknown(field.key)}
                  className="h-3.5 w-3.5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                />
                不知道
              </label>
            </div>
            {unknowns[field.key] ? (
              <p className="mt-1.5 text-[11px] text-slate-500">已记录为缺口：{field.label} 待补齐</p>
            ) : (
              <input
                id={`real-${field.key}`}
                value={values[field.key]}
                onChange={(event) => update(field.key, event.target.value)}
                placeholder={field.placeholder}
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-1.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-100"
              />
            )}
          </div>
        ))}

        {error && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</p>
        )}
      </div>
    </RealmDrawer>
  );
}