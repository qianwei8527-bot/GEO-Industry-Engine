"use client";

import { useState } from "react";
import { Check, Copy, KeyRound, Loader2, Plus, Trash2 } from "lucide-react";
import {
  createRealmAuthorization,
  revokeRealmAuthorization,
} from "@/lib/realm-owner/queries";
import type { RealmAuthorizationItem } from "@/lib/realm-owner/types";
import ModuleState from "./module-state";

export default function PublicIntakeTokenPanel({
  realmId,
  authorizations,
  canWrite,
  onChanged,
}: {
  realmId: string;
  authorizations: RealmAuthorizationItem[];
  canWrite: boolean;
  onChanged: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copiedCode, setCopiedCode] = useState("");
  const [createdCode, setCreatedCode] = useState("");
  const [createdId, setCreatedId] = useState("");
  const [customerLabel, setCustomerLabel] = useState("");
  const intakeTokens = authorizations.filter((item) => item.use_scope === "intake_submission");

  function maskCode(code: string) {
    return `${code.slice(0, 8)}••••••`;
  }

  async function createToken() {
    if (!canWrite) return;
    setBusy(true);
    setError("");
    try {
      const label = customerLabel.trim() || "公共资料提交入口";
      const created = await createRealmAuthorization(realmId, {
        source_name: label,
        source_type: "intake_submission_token",
        use_scope: "intake_submission",
        grantee_type: "anonymous_intake",
        grantee_id: "public",
        valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        sensitive_level: "medium",
        data_scope: { submitter: "anonymous_intake" },
        metadata: { token_kind: "public_intake_submission", customer_label: label },
      });
      setCreatedCode(created.authorization_code || "");
      setCreatedId(created.id);
      setCustomerLabel("");
      onChanged();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "令牌创建失败");
    } finally {
      setBusy(false);
    }
  }

  async function revokeToken(id: string) {
    if (!canWrite) return;
    setBusy(true);
    setError("");
    try {
      await revokeRealmAuthorization(realmId, id, "owner disabled intake link");
      onChanged();
    } catch (err) {
      const payload = err as { message?: string };
      setError(payload.message || "令牌撤销失败");
    } finally {
      setBusy(false);
    }
  }

  async function copyCode(code: string) {
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/intake/${code}`);
      setCopiedCode(code);
      window.setTimeout(() => setCopiedCode(""), 1500);
    } catch {
      setError("复制失败，请手动复制链接");
    }
  }

  return (
    <section className="realm-card p-4" aria-labelledby="public-intake-token-title">
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-start gap-3">
          <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-700">
            <KeyRound className="h-4 w-4" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <h2 id="public-intake-token-title" className="text-base font-semibold text-slate-900">
              公共资料提交入口
            </h2>
            <p className="mt-0.5 text-xs leading-5 text-slate-500">
              令牌绑定当前 Realm，有有效期并可撤销；前端不接收 realm_id。
            </p>
          </div>
        </div>
        {canWrite && (
          <div className="flex items-center gap-2">
            <input
              value={customerLabel}
              onChange={(event) => setCustomerLabel(event.target.value)}
              placeholder="客户/用途标签"
              className="w-40 rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-xs text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
            />
            <button
              type="button"
              onClick={createToken}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
            >
              {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Plus className="h-4 w-4" aria-hidden="true" />}
              生成 30 天令牌
            </button>
          </div>
        )}
      </header>

      {!canWrite && (
        <div className="mt-3">
          <ModuleState variant="blocked" title="只读视图" description="生成和撤销提交令牌需要域主或编辑权限。" compact />
        </div>
      )}

      {error && (
        <p className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
          {error}
        </p>
      )}

      <div className="mt-3">
        {intakeTokens.length === 0 ? (
          <ModuleState
            variant="empty"
            title="尚未生成提交令牌"
            description="生成后可将安全链接发给客户或合作伙伴填写资料。"
            compact
          />
        ) : (
          <ul className="space-y-2">
            {intakeTokens.map((token) => (
              <li key={token.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  {token.source_name && (
                    <span className="rounded-md bg-blue-50 px-2 py-1 text-[11px] font-medium text-blue-700">
                      {token.source_name}
                    </span>
                  )}
                  <code className="min-w-0 flex-1 truncate rounded-md bg-white px-2.5 py-1.5 text-xs text-slate-700">
                    {token.authorization_code_masked || maskCode(token.authorization_code || "")}
                  </code>
                  <span className={`rounded-md px-2 py-1 text-[11px] font-medium ${
                    token.status === "active" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                  }`}>
                    {token.status}
                  </span>
                </div>
                {createdId === token.id && createdCode && token.status === "active" && (
                  <div className="mt-2 rounded-md border border-blue-200 bg-blue-50 p-2.5">
                    <p className="text-[11px] font-medium text-blue-800">完整链接仅展示一次</p>
                    <div className="mt-1 flex flex-wrap items-center gap-2">
                      <code className="min-w-0 flex-1 truncate text-xs text-blue-700">
                        {window.location.origin}/intake/{createdCode}
                      </code>
                      <button
                        type="button"
                        onClick={() => copyCode(createdCode)}
                        className="inline-flex items-center gap-1 rounded-md border border-blue-300 bg-white px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-100"
                      >
                        {copiedCode === createdCode
                          ? <Check className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" />
                          : <Copy className="h-3.5 w-3.5" aria-hidden="true" />}
                        复制
                      </button>
                    </div>
                  </div>
                )}
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {canWrite && token.status === "active" && (
                    <>
                      <button
                        type="button"
                        onClick={() => revokeToken(token.id)}
                        disabled={busy}
                        className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-white px-2 py-1.5 text-xs font-medium text-rose-600 hover:bg-rose-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                        撤销
                      </button>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
