"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Boxes,
  CheckCircle2,
  Compass,
  FileText,
  Layers,
  Play,
  Settings,
  ShieldCheck,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import AppShell from "@/components/app-shell/AppShell";
import StatusStrip from "@/components/app-shell/StatusStrip";
import ModuleState from "@/components/realm-owner/module-state";
import type {
  ApplicationSurface,
  BaseEntry,
  CapabilityEntry,
  PanoramaFixture,
  PanoramaFixtureRegistry,
  PanoramaPage,
  PanoramaRegistry,
  PageTemplate,
} from "@/lib/panorama/types";

type MockState = "normal" | "loading" | "empty" | "partial" | "blocked" | "error" | "no-permission";

const SURFACE_LABEL: Record<ApplicationSurface, string> = {
  panorama: "全景设计模式",
  owner: "域主工作台",
  public: "公共世界与客户协作端",
  operations: "平台运营后台",
  governance: "治理审计台",
  midplatform: "中台能力域",
  backend: "技术底座",
};

const TEMPLATE_META: Record<PageTemplate, { label: string; icon: LucideIcon }> = {
  workbench: { label: "工作页面", icon: Play },
  list: { label: "列表页面", icon: FileText },
  detail: { label: "详情/展示页面", icon: Compass },
  config: { label: "配置页面", icon: Settings },
  management: { label: "管理页面", icon: ShieldCheck },
  canvas: { label: "探索画布", icon: Boxes },
};

const MOCK_STATES: Array<{ id: MockState; label: string }> = [
  { id: "normal", label: "normal" },
  { id: "loading", label: "loading" },
  { id: "empty", label: "empty" },
  { id: "partial", label: "partial" },
  { id: "blocked", label: "blocked" },
  { id: "error", label: "error" },
  { id: "no-permission", label: "no_permission" },
];

export default function PanoramaExplorer({
  registry,
  fixtures,
  capabilityMap,
}: {
  registry: PanoramaRegistry;
  fixtures: PanoramaFixtureRegistry;
  capabilityMap: {
    midplatforms: CapabilityEntry[];
    bases: BaseEntry[];
    page_to_capability: Record<string, string[]>;
  };
}) {
  const [currentPageId, setCurrentPageId] = useState(registry.pages[0]?.page_id || "owner-today");
  const [mockState, setMockState] = useState<MockState>("normal");
  const [notice, setNotice] = useState("");
  const [simulated, setSimulated] = useState<string[]>([]);

  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("page");
    if (requested && registry.pages.some((item) => item.page_id === requested)) {
      setCurrentPageId(requested);
    }
  }, [registry.pages]);

  const page = registry.pages.find((item) => item.page_id === currentPageId) || registry.pages[0];
  const fixture = fixtures.fixtures.find((item) => item.page_id === page.page_id);
  const surfaceLabel = SURFACE_LABEL[page.application_surface] || page.application_surface;
  const templateMeta = TEMPLATE_META[page.template];
  const TemplateIcon = templateMeta.icon;
  const capabilities = (capabilityMap.page_to_capability[page.page_id] || [])
    .map((id) => capabilityMap.midplatforms.find((item) => item.capability_id === id))
    .filter(Boolean) as CapabilityEntry[];

  const grouped = useMemo(() => {
    const result = new Map<string, PanoramaPage[]>();
    for (const item of registry.pages) {
      const list = result.get(item.application_surface) || [];
      list.push(item);
      result.set(item.application_surface, list);
    }
    return Array.from(result.entries());
  }, [registry.pages]);

  function simulate(label: string) {
    setNotice(`模拟操作：${label}，仅改变本地状态，不发送真实写请求。`);
    setSimulated((prev) => [label, ...prev].slice(0, 5));
  }

  function renderTemplate() {
    if (mockState !== "normal") {
      const map: Record<string, { variant: "loading" | "empty" | "partial" | "blocked" | "error" | "no-permission"; title: string; description: string }> = {
        loading: { variant: "loading", title: "正在加载全景骨架", description: "本地 Mock 加载态，不调用真实接口。" },
        empty: { variant: "empty", title: "尚无真实数据", description: "当前为 Fixture 空状态，接入 Adapter 后显示真实数据。" },
        partial: { variant: "partial", title: "资料不完整", description: "缺少字段保持 unknown，不自动补造。" },
        blocked: { variant: "blocked", title: "流程阻塞", description: "模拟阻塞状态，等待真实流程解除。" },
        error: { variant: "error", title: "加载失败", description: "本地 Mock 错误态，可重试。" },
        "no-permission": { variant: "no-permission", title: "无权限访问", description: "不展示内容，不泄露对象是否存在。" },
      };
      const meta = map[mockState];
      return <ModuleState variant={meta.variant} title={meta.title} description={meta.description} />;
    }
    if (page.template === "workbench") {
      return (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {["待确认", "执行中", "待连接", "主线"].map((label, index) => (
              <div key={label} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="text-[11px] text-slate-500">{label}</div>
                <div className="mt-1 text-2xl font-bold text-slate-900">{["2", "3", "1", "4"][index]}</div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <SkeletonPanel title="今日主线" note="Fixture 模拟">
              <SkeletonRow tone="amber" title="客户档案待确认" desc="AI 已整理，域主确认后进入计划" badge="去确认" />
              <SkeletonRow tone="green" title="执行计划运行中" desc="8 个任务 · 当前 30%" badge="查看" />
              <SkeletonRow tone="green" title="问题库收到新建议" desc="AI 分类 · 原文保留" badge="查看" />
            </SkeletonPanel>
            <SkeletonPanel title="最近连接" note="Fixture 模拟">
              <SkeletonRow tone="green" title="Mock 示例输入" desc="客户资料 · 已连接" badge="fixture" />
              <SkeletonRow tone="amber" title="行业认知" desc="待补齐 Fixture 证据" badge="unknown" />
              <SkeletonRow tone="red" title="资源需求" desc="尚未发布" badge="blocked" />
            </SkeletonPanel>
          </div>
          <button type="button" onClick={() => simulate("确认客户档案")} className="rounded-md bg-[color:var(--v106-primary)] px-3 py-2 text-xs font-semibold text-white">
            模拟确认
          </button>
        </div>
      );
    }
    if (page.template === "list") {
      return (
        <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
          <div className="mb-2 text-sm font-semibold text-slate-800">Fixture 列表</div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-left text-xs">
              <thead>
                <tr className="border-b border-[color:var(--v106-border)] text-slate-500">
                  <th className="py-2 pr-3 font-medium">名称</th>
                  <th className="py-2 pr-3 font-medium">状态</th>
                  <th className="py-2 pr-3 font-medium">truth</th>
                  <th className="py-2 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {["Fixture 项 A", "Fixture 项 B", "Fixture 项 C"].map((name, index) => (
                  <tr key={name} className="border-b border-[color:var(--v106-border)] last:border-0">
                    <td className="py-2 pr-3 text-slate-800">{name}</td>
                    <td className="py-2 pr-3 text-slate-500">{["正常", "待补充", "阻塞"][index]}</td>
                    <td className="py-2 pr-3 text-slate-500">simulation</td>
                    <td className="py-2">
                      <button type="button" onClick={() => simulate(`查看 ${name}`)} className="rounded border border-[color:var(--v106-border)] px-2 py-1 text-[11px] text-slate-600">
                        模拟操作
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }
    if (page.template === "detail") {
      return (
        <div className="space-y-3">
          <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <Sparkles className="h-4 w-4 text-[color:var(--v106-primary)]" aria-hidden="true" />
              {page.title} · 设计目标
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-600">当前为脱机设计预览，展示页面结构、数据接口位置和用户路径。</p>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {["输入", "输出", "依赖能力"].map((label) => (
              <div key={label} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="text-[11px] font-medium text-slate-500">{label}</div>
                <div className="mt-1 text-xs leading-5 text-slate-700">
                  {label === "依赖能力" ? capabilities.map((item) => item.name).join("、") : "Fixture 模拟输入输出，待真实 Adapter 接入"}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }
    if (page.template === "config") {
      return (
        <div className="space-y-3">
          {["连接名称", "权限范围", "风险等级", "人工确认"].map((label, index) => (
            <div key={label} className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-[color:var(--v106-border)] bg-white p-3">
              <span className="text-xs font-medium text-slate-700">{label}</span>
              <span className="rounded-md bg-slate-100 px-2 py-1 text-[11px] text-slate-500">{["Fixture 连接", "Realm 范围", index === 2 ? "中" : "开启"][index]}</span>
            </div>
          ))}
          <button type="button" onClick={() => simulate("保存配置")} className="rounded-md bg-[color:var(--v106-primary)] px-3 py-2 text-xs font-semibold text-white">
            模拟保存
          </button>
        </div>
      );
    }
    if (page.template === "management") {
      return (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {["总数", "待处理", "已确认", "风险"].map((label, index) => (
              <div key={label} className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
                <div className="text-[11px] text-slate-500">{label}</div>
                <div className="mt-1 text-xl font-bold text-slate-900">{["12", "3", "8", "1"][index]}</div>
              </div>
            ))}
          </div>
          <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
            <div className="text-xs font-semibold text-slate-700">管理列表</div>
            {["Fixture 策略 A", "Fixture 策略 B", "Fixture 策略 C"].map((item) => (
              <div key={item} className="mt-2 flex items-center justify-between gap-2 rounded-md bg-slate-50 px-3 py-2">
                <span className="text-xs text-slate-700">{item}</span>
                <button type="button" onClick={() => simulate(`审批 ${item}`)} className="rounded bg-emerald-600 px-2 py-1 text-[11px] text-white">模拟审批</button>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return (
      <div className="rounded-md border border-dashed border-[color:var(--v106-border)] bg-white p-4">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-800">
          <Layers className="h-4 w-4 text-[color:var(--v106-primary)]" aria-hidden="true" />
          探索画布骨架
        </div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
          {["主体", "关系", "事件", "缺口"].map((item, index) => (
            <button key={item} type="button" onClick={() => simulate(`展开 ${item}`)} className="min-h-20 rounded-md border border-[color:var(--v106-border)] bg-slate-50 p-3 text-left">
              <div className="text-xs font-medium text-slate-700">{item}</div>
              <div className="mt-1 text-[11px] text-slate-500">Fixture 节点 {index + 1}</div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  const navRail = (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-[color:var(--v106-border)] bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-[color:var(--v106-border)] px-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[color:var(--v106-primary)] text-white">
          <Boxes className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-bold text-slate-900">恒域世界全景</span>
      </div>
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        {grouped.map(([surface, pages]) => (
          <div key={surface} className="mb-3">
            <div className="px-2 py-1 text-[11px] font-semibold text-slate-500">{SURFACE_LABEL[surface as ApplicationSurface]}</div>
            {pages.map((item) => (
              <button
                key={item.page_id}
                type="button"
                onClick={() => {
                  setCurrentPageId(item.page_id);
                  setMockState("normal");
                  setNotice("");
                }}
                className={`mb-0.5 flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-xs ${
                  currentPageId === item.page_id
                    ? "bg-[color:var(--v106-primary-weak)] font-medium text-[color:var(--v106-primary-strong)]"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <span className="min-w-0 flex-1 truncate">{item.title}</span>
                <span className={`shrink-0 rounded px-1 py-0.5 text-[9px] ${item.feature_flag === "open" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                  {item.feature_flag}
                </span>
              </button>
            ))}
          </div>
        ))}
      </nav>
      <div className="border-t border-[color:var(--v106-border)] px-4 py-3 text-[10px] leading-4 text-slate-500">
        全景骨架 · Fixture 模拟 · 不发送真实写请求 · R1-R3 真实功能保留
      </div>
    </aside>
  );

  return (
    <AppShell
      surface="owner"
      featureFlags={["panorama", ...registry.application_surfaces]}
      navRail={navRail}
      userContext={{ label: "全景设计者", permissions: ["panorama_read"] }}
      contextBar={
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-[color:var(--v106-border)] bg-white px-4 lg:px-6">
          <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
            恒域世界全景 <span className="mx-1 text-slate-300">/</span> {surfaceLabel} <span className="mx-1 text-slate-300">/</span> {page.title}
          </div>
          <a href="/v106-all-pages-design-preview" className="rounded-md border border-[color:var(--v106-border)] px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50">
            返回设计预览
          </a>
        </header>
      }
      statusStrip={
        <StatusStrip
          items={[
            { label: "数据模式", value: page.data_mode, tone: "warning" },
            { label: "实现状态", value: page.implementation_status },
            { label: "模板", value: templateMeta.label },
            { label: "Feature Flag", value: page.feature_flag },
          ]}
        />
      }
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <TemplateIcon className="h-5 w-5 text-[color:var(--v106-primary)]" aria-hidden="true" />
                <h1 className="v106-page-title">{page.title}</h1>
              </div>
              <p className="mt-1 text-sm text-slate-500">{page.next_realization_task}</p>
            </div>
            <span className="rounded-md bg-amber-50 px-2 py-1 text-[11px] font-medium text-amber-700">Mock / 脱机预览 / 非生产数据</span>
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {[
              `dataMode=${page.data_mode}`,
              `implementationStatus=${page.implementation_status}`,
              `fixture=${fixture?.fixture_id || "missing"}`,
              `template=${page.template}`,
              `truthScope=${fixture?.truth_scope || "simulation"}`,
              `route=${page.route}`,
            ].map((text) => (
              <span key={text} className="break-all rounded-md bg-white px-2 py-1 text-[10px] text-slate-600 ring-1 ring-[color:var(--v106-border)]">
                {text}
              </span>
            ))}
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="text-[11px] text-slate-500">Mock 状态切换：</span>
            {MOCK_STATES.map((state) => (
              <button
                key={state.id}
                type="button"
                onClick={() => setMockState(state.id)}
                className={`rounded-md border px-2 py-1 text-[11px] ${mockState === state.id ? "border-teal-600 bg-teal-50 text-teal-700" : "border-[color:var(--v106-border)] bg-white text-slate-600"}`}
              >
                {state.label}
              </button>
            ))}
          </div>
        </header>
        {notice && (
          <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">{notice}</div>
        )}
        {fixture && (
          <div className="mb-3 rounded-md border border-slate-200 bg-white p-3 text-[11px] leading-5 text-slate-600">
            Fixture：{fixture.fixture_id} · 场景：{fixture.scenario} · 来源：{fixture.source_label} · 生成时间：{fixture.generated_at}
          </div>
        )}
        {renderTemplate()}
        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
            <div className="mb-2 text-xs font-semibold text-slate-700">依赖能力</div>
            <div className="space-y-1">
              {capabilities.length === 0 && <div className="text-[11px] text-slate-500">无依赖能力</div>}
              {capabilities.map((capability) => (
                <div key={capability.capability_id} className="rounded-md bg-slate-50 px-2 py-1.5 text-[11px] text-slate-600">
                  {capability.name} · {capability.status}
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
            <div className="mb-2 text-xs font-semibold text-slate-700">本地模拟记录</div>
            {simulated.length === 0 && <div className="text-[11px] text-slate-500">尚无模拟操作</div>}
            <ul className="space-y-1">
              {simulated.map((item) => (
                <li key={item} className="flex items-center gap-2 text-[11px] text-slate-600">
                  <CheckCircle2 className="h-3 w-3 text-emerald-600" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function SkeletonPanel({ title, note, children }: { title: string; note: string; children: ReactNode }) {
  return (
    <div className="rounded-md border border-[color:var(--v106-border)] bg-white p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="text-sm font-semibold text-slate-800">{title}</div>
        <span className="text-[11px] text-slate-500">{note}</span>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function SkeletonRow({ tone, title, desc, badge }: { tone: string; title: string; desc: string; badge: string }) {
  return (
    <div className="flex items-center gap-2 rounded-md bg-slate-50 px-3 py-2">
      <span className={`h-2 w-2 shrink-0 rounded-full ${tone === "amber" ? "bg-amber-500" : tone === "red" ? "bg-rose-500" : "bg-emerald-500"}`} />
      <div className="min-w-0 flex-1">
        <div className="truncate text-xs font-medium text-slate-800">{title}</div>
        <div className="truncate text-[11px] text-slate-500">{desc}</div>
      </div>
      <span className="shrink-0 rounded bg-white px-1.5 py-0.5 text-[10px] text-slate-500 ring-1 ring-[color:var(--v106-border)]">{badge}</span>
    </div>
  );
}
