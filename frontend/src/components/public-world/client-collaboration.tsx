"use client";

import { useState } from "react";
import { FilePlus, Link2, ShieldCheck } from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import { fetchClientProjects, submitClientFeedback } from "@/lib/client/api";
import type { ClientProjectContext } from "@/lib/client/types";

export default function ClientCollaboration() {
  const [token, setToken] = useState("");
  const [context, setContext] = useState<ClientProjectContext | null>(null);
  const [phase, setPhase] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [error, setError] = useState("");
  const [feedbackProject, setFeedbackProject] = useState("");
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackMessage, setFeedbackMessage] = useState("");

  async function connect() {
    if (!token.trim()) return;
    setPhase("loading");
    setError("");
    try {
      setContext(await fetchClientProjects(token.trim()));
      setPhase("ready");
    } catch (err) {
      setPhase("error");
      setError(err instanceof Error ? err.message : "连接失败");
    }
  }

  async function submitFeedback(projectId: string) {
    if (!feedbackText.trim()) return;
    setFeedbackMessage("");
    try {
      const result = await submitClientFeedback({
        token: token.trim(),
        projectId,
        originalText: feedbackText.trim(),
      });
      setFeedbackMessage(`已提交：${result.issue_code}`);
      setFeedbackText("");
      setFeedbackProject("");
    } catch (err) {
      setFeedbackMessage(err instanceof Error ? err.message : "提交失败");
    }
  }

  const navRail = (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <Link2 className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">客户协作</span>
      </div>
      <nav className="flex-1 px-2 py-3">
        <a href="/public" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">公开世界</a>
        <a href="/intake" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">资料提交</a>
        <a href="/client" className="mb-1 block rounded-md bg-[color:var(--v106-primary-weak)] px-2.5 py-2 text-sm font-medium text-[color:var(--v106-primary-strong)]">客户协作</a>
        <a href="/market" className="mb-1 block rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50">能力市场</a>
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[11px] text-slate-500">
        客户空间按项目隔离，不展示其他客户数据。
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="public"
      featureFlags={["client"]}
      navRail={navRail}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <span className="text-xs text-slate-500">公共世界 / 客户协作</span>
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "项目隔离", value: "仅当前项目", tone: "success" },
            { label: "权限", value: "客户令牌" },
            { label: "truth scope", value: "observed" },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-4xl">
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <FilePlus className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
            <h1 className="v106-page-title">客户协作</h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">项目进度、成果确认、问题反馈和交付，只显示与当前项目相关的数据。</p>
        </header>
        <section className="v106-panel mb-4 p-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-800">连接客户项目</h2>
          <p className="mb-3 text-xs text-slate-500">输入域主提供的客户令牌，只读取该令牌绑定的 Realm 项目。</p>
          <div className="flex flex-wrap items-center gap-2">
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="粘贴客户项目令牌"
              className="v106-control min-w-[240px] flex-1 px-3 py-2 text-sm"
            />
            <button
              type="button"
              onClick={connect}
              className="rounded-md bg-[color:var(--v106-primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
              disabled={phase === "loading" || !token.trim()}
            >
              {phase === "loading" ? "连接中…" : "连接项目"}
            </button>
          </div>
          {phase === "error" && <p className="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</p>}
        </section>

        {phase === "loading" && <ModuleState variant="loading" title="正在读取客户项目" />}
        {phase === "idle" && (
          <ModuleState
            variant="empty"
            title="尚未连接客户项目"
            description="域主创建客户令牌并绑定项目后，输入令牌即可查看项目进度和交付物。"
          />
        )}
        {phase === "ready" && context && (
          <>
            <section className="v106-panel mb-4 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h2 className="text-sm font-semibold text-slate-800">{context.realm.display_name}</h2>
                  <p className="mt-1 text-xs text-slate-500">{context.realm.realm_code} · {context.realm.realm_type} · {context.authorization.authorization_code_masked}</p>
                </div>
                <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs text-emerald-700">令牌有效</span>
              </div>
            </section>
            {context.projects.length > 0 ? (
              <>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {context.projects.map((project) => (
                    <div key={project.id} className="v106-panel p-4">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-semibold text-slate-800">{project.name}</span>
                        <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">{project.status}</span>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">{project.project_code} · {project.truth_status}</p>
                      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                        <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-2">
                          <div className="text-slate-500">资产</div>
                          <div className="mt-1 font-medium text-slate-800">{project.assets.length}</div>
                        </div>
                        <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-2">
                          <div className="text-slate-500">成果</div>
                          <div className="mt-1 font-medium text-slate-800">{project.outcomes.length}</div>
                        </div>
                      </div>
                      {project.assets.length > 0 && (
                        <div className="mt-3">
                          <div className="text-[11px] font-medium text-slate-500">交付物</div>
                          <ul className="mt-1 space-y-1 text-xs text-slate-600">
                            {project.assets.slice(0, 4).map((asset, index) => (
                              <li key={`${asset.title}-${index}`}>{asset.title} · {asset.truth_status}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {project.outcomes.length > 0 && (
                        <div className="mt-3">
                          <div className="text-[11px] font-medium text-slate-500">成果确认</div>
                          <ul className="mt-1 space-y-1 text-xs text-slate-600">
                            {project.outcomes.slice(0, 3).map((outcome, index) => (
                              <li key={`${outcome.claim_text}-${index}`}>{outcome.claim_text} · {outcome.truth_status}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <button
                        type="button"
                        onClick={() => {
                          setFeedbackProject(project.id);
                          setFeedbackMessage("");
                        }}
                        className="mt-3 rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                      >
                        反馈问题
                      </button>
                    </div>
                  ))}
                </div>
                {feedbackProject && (
                  <section className="v106-panel mt-4 p-4">
                    <h2 className="mb-2 text-sm font-semibold text-slate-800">提交问题反馈</h2>
                    <p className="mb-3 text-xs text-slate-500">反馈原文进入问题库，AI 只分类，不覆盖原文。</p>
                    <textarea
                      value={feedbackText}
                      onChange={(event) => setFeedbackText(event.target.value)}
                      placeholder="描述遇到的问题"
                      className="v106-control min-h-24 w-full px-3 py-2 text-sm"
                    />
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        onClick={() => submitFeedback(feedbackProject)}
                        className="rounded-md bg-[color:var(--v106-primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[color:var(--v106-primary-strong)] disabled:opacity-60"
                        disabled={!feedbackText.trim()}
                      >
                        提交反馈
                      </button>
                      <button
                        type="button"
                        onClick={() => setFeedbackProject("")}
                        className="rounded-md border border-[color:var(--v106-border)] bg-white px-3 py-2 text-sm text-slate-700"
                      >
                        取消
                      </button>
                    </div>
                    {feedbackMessage && <p className="mt-3 text-xs text-slate-600">{feedbackMessage}</p>}
                  </section>
                )}
              </>
            ) : (
              <ModuleState variant="empty" title="该令牌暂无项目" description="域主创建项目并绑定后，这里会出现真实项目。" />
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
