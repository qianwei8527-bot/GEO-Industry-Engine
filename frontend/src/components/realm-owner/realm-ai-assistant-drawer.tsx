"use client";

import { useEffect, useState } from "react";
import { Bot, Loader2, Send, Sparkles } from "lucide-react";
import RealmDrawer from "./drawer";
import TruthBadge from "./truth-badge";
import { fetchAgentDraft } from "@/lib/realm-owner/queries";
import type { AgentDraftResponse } from "@/lib/realm-owner/types";

interface RealmAIAssistantDrawerProps {
  open: boolean;
  onClose: () => void;
  realmId: string;
  prefilledQuery?: string;
}

export default function RealmAIAssistantDrawer({
  open,
  onClose,
  realmId,
  prefilledQuery = "",
}: RealmAIAssistantDrawerProps) {
  const [query, setQuery] = useState(prefilledQuery);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentDraftResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setQuery(prefilledQuery);
      setResult(null);
      setError(null);
    }
  }, [open, prefilledQuery]);

  async function generateDraft() {
    if (!query.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const draft = await fetchAgentDraft(query.trim(), { realm_id: realmId });
      setResult(draft);
    } catch (err) {
      const payload = err as { status?: number; message?: string };
      setError(
        payload.message ||
          "Agent 运行接口暂不可用；已记录为接口缺口，不使用假数据代替。",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="AI域主助手"
      description="AI 只生成草稿与推断，不自动联系、发布或承诺；所有输出需域主确认。"
    >
      <div className="space-y-3">
        <label className="block text-xs font-medium text-slate-700" htmlFor="ai-query">
          你要梳理什么？
        </label>
        <textarea
          id="ai-query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          rows={4}
          placeholder="例如：帮我起草首个资源需求的候选联系内容"
          className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-100"
        />

        <button
          type="button"
          onClick={generateDraft}
          disabled={!query.trim() || loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-violet-700 px-3 py-2 text-sm font-semibold text-white hover:bg-violet-800 disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-600"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Sparkles className="h-4 w-4" aria-hidden="true" />}
          生成草稿
        </button>

        {loading && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-4 text-xs text-slate-500" role="status">
            Agent 正在生成草稿，仅只读检索与推理…
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-3 text-xs leading-5 text-rose-700">
            {error}
          </div>
        )}

        {result && (
          <div className="rounded-lg border border-violet-200 bg-violet-50/50 p-3">
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-violet-600" aria-hidden="true" />
              <span className="text-xs font-semibold text-violet-800">AI 草稿</span>
              <TruthBadge scope="inferred" />
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
              {result.summary || "没有生成摘要。"}
            </p>
            {result.citations && result.citations.length > 0 && (
              <div className="mt-2 text-[11px] text-slate-500">
                引用 {result.citations.length} 项；引用内容需继续核验，不等同于已验证事实。
              </div>
            )}
          </div>
        )}

        <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
          <p className="text-[11px] leading-5 text-slate-500">
            当前没有可用的 Agent 发送接口，也不会调用外部联系动作。草稿只能保存在本会话中，域主确认后才可进入下一步。
          </p>
        </div>

        <button
          type="button"
          disabled
          aria-disabled="true"
          title="未提供发送接口，且必须由域主确认"
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-200 px-3 py-2 text-sm font-semibold text-slate-500 cursor-not-allowed"
        >
          <Send className="h-4 w-4" aria-hidden="true" />
          发送（需域主确认，当前不可用）
        </button>
      </div>
    </RealmDrawer>
  );
}