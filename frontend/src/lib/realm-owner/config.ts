import type {
  InformationCategory,
  MapMode,
  ResourceGroupType,
  StartupTaskStatus,
  TruthScope,
} from "./types";

export interface NavDefinition {
  id: string;
  label: string;
  iconKey: string;
  href: (realmId: string) => string;
  enabled: boolean;
}

export const PRIMARY_NAV_DEFS: NavDefinition[] = [
  {
    id: "today",
    label: "今日工作",
    iconKey: "inbox",
    href: (realmId) => `/realm/${realmId}/explore`,
    enabled: true,
  },
  {
    id: "customers",
    label: "客户与定位",
    iconKey: "users",
    href: (realmId) => `/realm/${realmId}/customers`,
    enabled: true,
  },
  {
    id: "projects",
    label: "项目与计划",
    iconKey: "package",
    href: (realmId) => `/realm/${realmId}/projects`,
    enabled: true,
  },
  {
    id: "execution",
    label: "执行与问题",
    iconKey: "play",
    href: (realmId) => `/realm/${realmId}/execution`,
    enabled: true,
  },
  {
    id: "results",
    label: "结果与资产",
    iconKey: "database",
    href: (realmId) => `/realm/${realmId}/results`,
    enabled: true,
  },
  {
    id: "tools",
    label: "工具与连接",
    iconKey: "link",
    href: (realmId) => `/realm/${realmId}/tools`,
    enabled: true,
  },
];

export interface StartupTaskDefinition {
  id: string;
  title: string;
  detail: string;
  defaultStatus: StartupTaskStatus;
  blockedReason: string | null;
  targetHref: string | null;
}

export const STARTUP_TASK_DEFS: StartupTaskDefinition[] = [
  {
    id: "clarify-track",
    title: "明确行业与赛道",
    detail: "记录真实试点品牌、主体、关系、产品、客户、地区、问题、渠道与转化目标，建立行业认知基线。",
    defaultStatus: "ready",
    blockedReason: null,
    targetHref: "real-input",
  },
  {
    id: "confirm-pilot",
    title: "确认首个试点关系",
    detail: "基于真实输入确定第一个试点与品牌关系；完成后解锁90天计划。",
    defaultStatus: "locked",
    blockedReason: "先补齐真实输入并建立行业认知",
    targetHref: null,
  },
  {
    id: "define-product",
    title: "定义标准GEO产品",
    detail: "把首个试点的方法沉淀为标准 GEO 产品：目标、客户、交付物与验收标准。",
    defaultStatus: "locked",
    blockedReason: "需要首个试点与真实结果作为依据",
    targetHref: null,
  },
  {
    id: "publish-demand",
    title: "发布首个资源需求",
    detail: "填写结构化资源需求，经域主确认后创建 Demand 对象并获得带证据的候选。",
    defaultStatus: "locked",
    blockedReason: "需要真实业务目标与能力缺口",
    targetHref: null,
  },
];

export const MAP_VIEW_DEFS: Array<{ id: MapMode; label: string; hint: string }> = [
  { id: "business_flow", label: "业务流程", hint: "从需求出现到反馈评估的六段业务流" },
  { id: "demand_solution", label: "需求方案", hint: "从需求捕获到试点执行的方案流" },
  { id: "resource_map", label: "资源地图", hint: "从业务目标到交付协作的资源流" },
];

export interface MapNodeDefinition {
  id: string;
  label: string;
  description: string;
  iconKey: string;
}

export const MAP_NODE_DEFS: Record<MapMode, MapNodeDefinition[]> = {
  business_flow: [
    { id: "demand", label: "需求出现", description: "真实客户需求被捕获并记录为 Demand Event。", iconKey: "search" },
    { id: "diagnosis", label: "诊断决策", description: "对需求与当前状态做诊断，形成决策依据。", iconKey: "stethoscope" },
    { id: "solution", label: "解决方案", description: "形成可执行的 GEO 解决方案与交付范围。", iconKey: "lightbulb" },
    { id: "production", label: "生产交付", description: "按项目与工作项生产内容、工具执行并交付。", iconKey: "package" },
    { id: "distribution", label: "分发触达", description: "把已发布内容分发到真实渠道与目标对象。", iconKey: "send" },
    { id: "feedback", label: "反馈评估", description: "回填监测结果并沉淀为 Evidence 与 Outcome。", iconKey: "refreshCw" },
  ],
  demand_solution: [
    { id: "capture", label: "需求捕获", description: "记录真实问题、场景与付费意愿。", iconKey: "inbox" },
    { id: "gap", label: "缺口分析", description: "分析能力缺口、证据覆盖与信任缺口。", iconKey: "gitBranch" },
    { id: "design", label: "方案设计", description: "设计解决方案与验收标准。", iconKey: "pencilRuler" },
    { id: "verify", label: "证据核验", description: "用结构化 EvidenceClaim 核验方案依据。", iconKey: "shieldCheck" },
    { id: "pilot", label: "试点执行", description: "在真实试点中执行并记录工具与结果。", iconKey: "play" },
    { id: "review", label: "反馈评估", description: "对照目标评估结果并回填可信信息流。", iconKey: "refreshCw" },
  ],
  resource_map: [
    { id: "goal", label: "业务目标", description: "明确首个试点要达成的业务目标。", iconKey: "target" },
    { id: "capability-gap", label: "能力缺口", description: "识别当前缺少的能力或资源。", iconKey: "alertTriangle" },
    { id: "need", label: "资源需求", description: "发布结构化资源需求（Demand Event）。", iconKey: "filePlus" },
    { id: "match", label: "候选匹配", description: "获取带理由、证据、风险与未知项的候选。", iconKey: "link" },
    { id: "connect", label: "连接确认", description: "域主确认后进入真实连接状态机。", iconKey: "handshake" },
    { id: "collaborate", label: "交付协作", description: "在真实协作中交付并记录结果。", iconKey: "users" },
  ],
};

export const MAP_EDGE_TRUTH_SCOPE: TruthScope = "simulation";

export const RESOURCE_GROUP_DEFS: Array<{
  type: ResourceGroupType;
  label: string;
  emptyHint: string;
}> = [
  { type: "expert", label: "行业专家", emptyHint: "暂无候选。先发布真实需求，系统再提供带证据的匹配。" },
  { type: "channel", label: "渠道资源", emptyHint: "暂无候选。渠道候选只会来自真实需求与已验证连接。" },
  { type: "delivery_partner", label: "交付伙伴", emptyHint: "暂无候选。交付伙伴必须由域主确认后进入真实连接。" },
];

export const INFORMATION_CATEGORY_DEFS: Array<{
  id: InformationCategory;
  label: string;
}> = [
  { id: "official", label: "官方规则" },
  { id: "research", label: "行业研究" },
  { id: "user_need", label: "用户需求" },
  { id: "case_method", label: "案例方法" },
];

export interface TruthScopeMeta {
  scope: TruthScope;
  label: string;
  meaning: string;
  iconKey: string;
}

export const TRUTH_SCOPE_META: TruthScopeMeta[] = [
  {
    scope: "verified",
    label: "已验证",
    meaning: "满足证据和验证规则",
    iconKey: "shieldCheck",
  },
  {
    scope: "observed",
    label: "已观察",
    meaning: "有真实记录但未完成验证",
    iconKey: "eye",
  },
  {
    scope: "inferred",
    label: "AI推断",
    meaning: "AI根据已知事实提出的推断",
    iconKey: "bot",
  },
  {
    scope: "simulation",
    label: "预演",
    meaning: "仅用于配置和未来分析",
    iconKey: "flaskConical",
  },
  {
    scope: 'unknown',
    label: '待补充',
    meaning: '资料中未发现，AI 不补造',
    iconKey: 'alertTriangle',
  },
];

export const READINESS_LABELS: Record<string, string> = {
  unknown: "未知",
  missing: "缺失",
  partial: "部分就绪",
  ready: "就绪",
  blocked: "受阻",
  stale: "已过期",
};

export const STARTUP_STATUS_LABELS: Record<StartupTaskStatus, string> = {
  locked: "未解锁",
  ready: "可开始",
  in_progress: "进行中",
  blocked: "受阻",
  needs_review: "待确认",
  completed: "已完成",
};

export const DEFAULT_NEXT_ACTION = {
  title: "确定首个真实试点与品牌关系",
  reason: "当前还没有可验证的真实试点；90天计划必须在真实试点与品牌关系明确后解锁。",
  completionCondition: "首个试点品牌、品牌关系、核心产品、目标客户与主要转化目标真实明确",
  targetHref: "real-input",
};
