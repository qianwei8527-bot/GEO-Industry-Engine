export type ApplicationSurface = "owner" | "public" | "operations" | "governance";

export interface SurfaceProtocol {
  label: string;
  protocolStatus: "implemented" | "reserved";
  navItems: Array<{
    id: string;
    label: string;
    iconKey: string;
    status: "open" | "planned" | "disabled";
  }>;
}

export const APPLICATION_SURFACES: Record<ApplicationSurface, SurfaceProtocol> = {
  owner: {
    label: "域主工作台",
    protocolStatus: "implemented",
    navItems: [
      { id: "today", label: "今日工作", iconKey: "inbox", status: "planned" },
      { id: "customers", label: "客户与定位", iconKey: "users", status: "open" },
      { id: "projects", label: "项目与计划", iconKey: "package", status: "open" },
      { id: "execution", label: "执行与问题", iconKey: "play", status: "open" },
      { id: "results", label: "结果与资产", iconKey: "database", status: "planned" },
      { id: "tools", label: "工具与连接", iconKey: "link", status: "planned" },
      { id: "policy", label: "政策与综合经营", iconKey: "scale", status: "disabled" },
      { id: "market", label: "能力市场", iconKey: "shoppingBag", status: "disabled" },
      { id: "intel", label: "行业态势", iconKey: "globe", status: "disabled" },
      { id: "collective", label: "共同治理", iconKey: "gitBranch", status: "disabled" },
    ],
  },
  public: {
    label: "公共世界与客户协作端",
    protocolStatus: "implemented",
    navItems: [
      { id: "home", label: "公开世界", iconKey: "globe", status: "open" },
      { id: "intake", label: "资料提交", iconKey: "filePlus", status: "open" },
      { id: "client", label: "客户协作", iconKey: "users", status: "open" },
      { id: "market", label: "能力市场", iconKey: "shoppingBag", status: "disabled" },
    ],
  },
  operations: {
    label: "平台运营后台",
    protocolStatus: "implemented",
    navItems: [
      { id: "overview", label: "平台总览", iconKey: "layoutDashboard", status: "open" },
      { id: "realms", label: "Realm 与用户", iconKey: "building2", status: "open" },
      { id: "runtime", label: "运行任务", iconKey: "activity", status: "open" },
      { id: "agents", label: "Agent 运行", iconKey: "bot", status: "open" },
      { id: "workflows", label: "工作流", iconKey: "workflow", status: "open" },
      { id: "connectors", label: "工具与连接", iconKey: "plugZap", status: "open" },
      { id: "capabilities", label: "Agent 与能力", iconKey: "bot", status: "open" },
      { id: "reports", label: "报告与结果", iconKey: "fileText", status: "open" },
      { id: "system", label: "系统与配置", iconKey: "settings", status: "open" },
      { id: "alerts", label: "运行告警", iconKey: "bellRing", status: "open" },
    ],
  },
  governance: {
    label: "治理审计台",
    protocolStatus: "implemented",
    navItems: [
      { id: "permissions", label: "权限策略", iconKey: "users", status: "open" },
      { id: "approvals", label: "审批中心", iconKey: "shieldCheck", status: "open" },
      { id: "realm-claims", label: "域认领审核", iconKey: "landmark", status: "open" },
      { id: "evidence", label: "Evidence 审核", iconKey: "badgeCheck", status: "open" },
      { id: "external-actions", label: "外部动作审核", iconKey: "plugZap", status: "open" },
      { id: "audit", label: "审计日志", iconKey: "fileText", status: "open" },
      { id: "risk", label: "风险控制", iconKey: "lock", status: "open" },
      { id: "retention", label: "数据保留与删除", iconKey: "trash2", status: "open" },
      { id: "collective", label: "共同治理", iconKey: "gitBranch", status: "planned" },
    ],
  },
};
