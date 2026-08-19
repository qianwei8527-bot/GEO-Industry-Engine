export type CodeConnectionAuth =
  | "public"
  | "owner"
  | "operations"
  | "governance"
  | "client";

export interface CodeConnection {
  surfaceId: string;
  surfaceLabel: string;
  pageId: string;
  pageLabel: string;
  route: string;
  auth: CodeConnectionAuth;
  component: string;
  api: string[];
  status: "implemented" | "reserved" | "partial";
}

export const CODE_CONNECTIONS: CodeConnection[] = [
  // 域主工作台
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "today", pageLabel: "今日工作", route: "/realm/{realm_id}/explore", auth: "owner", component: "realm-owner-shell", api: ["/realm/{id}", "/intakes", "/geo-projects", "/issues", "/demand", "/connection"], status: "implemented" },
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "customers", pageLabel: "客户与定位", route: "/realm/{realm_id}/customers", auth: "owner", component: "realm-owner-section-page", api: ["/realm/{id}", "/intakes", "/intakes/{id}/workbench", "/intakes/{id}/profile", "/intakes/{id}/profile/confirm", "/intakes/{id}/positioning/generate", "/intakes/{id}/positioning/confirm", "/intakes/{id}/project", "/simulation/loops/run", "/simulation/loops/latest"], status: "implemented" },
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "projects", pageLabel: "项目与计划", route: "/realm/{realm_id}/projects", auth: "owner", component: "realm-owner-section-page", api: ["/realm/{id}", "/geo-projects", "/execution/projects/{id}/plan"], status: "implemented" },
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "execution", pageLabel: "执行与问题", route: "/realm/{realm_id}/execution", auth: "owner", component: "realm-owner-section-page", api: ["/realm/{id}", "/issues", "/geo-projects/{id}/tool-executions"], status: "implemented" },
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "results", pageLabel: "结果与资产", route: "/realm/{realm_id}/results", auth: "owner", component: "realm-owner-section-page", api: ["/realm/{id}", "/evidence", "/geo-projects/{id}/assets"], status: "implemented" },
  { surfaceId: "owner", surfaceLabel: "域主工作台", pageId: "tools", pageLabel: "工具与连接", route: "/realm/{realm_id}/tools", auth: "owner", component: "realm-owner-section-page", api: ["/realm/{id}/authorizations", "/realm/{id}/tool-configs", "/mcp/tools", "/agent/list"], status: "implemented" },

  // 公共世界与客户协作端
  { surfaceId: "public", surfaceLabel: "公共世界与客户协作端", pageId: "public", pageLabel: "公开世界", route: "/public", auth: "public", component: "public-world-hub", api: ["/universe/world-state/snapshots"], status: "implemented" },
  { surfaceId: "public", surfaceLabel: "公共世界与客户协作端", pageId: "intake", pageLabel: "资料提交", route: "/intake/{secure_token}", auth: "public", component: "public-intake-page", api: ["/intakes/public/{token}", "/intakes/public/{token}/draft", "/intakes/public/{token}/submissions"], status: "implemented" },
  { surfaceId: "public", surfaceLabel: "公共世界与客户协作端", pageId: "client", pageLabel: "客户协作", route: "/client", auth: "client", component: "client-collaboration", api: ["/client/projects/{token}"], status: "implemented" },
  { surfaceId: "public", surfaceLabel: "公共世界与客户协作端", pageId: "market", pageLabel: "能力市场", route: "/market", auth: "public", component: "market-placeholder", api: ["/capabilities/public"], status: "reserved" },

  // 平台运营后台
  { surfaceId: "operations", surfaceLabel: "平台运营后台", pageId: "overview", pageLabel: "平台总览", route: "/operations", auth: "operations", component: "operations-console", api: ["/admin/health", "/admin/db-stats", "/admin/configs", "/agent/list", "/mcp/tools", "/providers", "/capabilities", "/capabilities/runs", "/universe/world-state/snapshots"], status: "implemented" },
  { surfaceId: "operations", surfaceLabel: "平台运营后台", pageId: "intelligence", pageLabel: "行业态势", route: "/operations", auth: "operations", component: "operations-console", api: ["/universe/world-state/snapshots"], status: "implemented" },
  { surfaceId: "operations", surfaceLabel: "平台运营后台", pageId: "midplatform", pageLabel: "中台能力域", route: "/midplatform", auth: "operations", component: "midplatform-console", api: ["/admin/health", "/admin/db-stats"], status: "implemented" },
  { surfaceId: "operations", surfaceLabel: "平台运营后台", pageId: "backend", pageLabel: "后端基础设施", route: "/backend", auth: "operations", component: "backend-console", api: ["/admin/health", "/admin/db-stats"], status: "implemented" },

  // 治理审计台
  { surfaceId: "governance", surfaceLabel: "治理审计台", pageId: "permissions", pageLabel: "权限策略", route: "/governance", auth: "governance", component: "governance-console", api: ["/admin/health", "/admin/db-stats"], status: "implemented" },
  { surfaceId: "governance", surfaceLabel: "治理审计台", pageId: "approvals", pageLabel: "审批中心", route: "/governance", auth: "governance", component: "governance-console", api: ["/admin/approvals"], status: "implemented" },
  { surfaceId: "governance", surfaceLabel: "治理审计台", pageId: "audit", pageLabel: "审计日志", route: "/governance", auth: "governance", component: "governance-console", api: ["/admin/audit-logs"], status: "implemented" },
  { surfaceId: "governance", surfaceLabel: "治理审计台", pageId: "risk", pageLabel: "风险控制", route: "/governance", auth: "governance", component: "governance-console", api: [], status: "implemented" },
  { surfaceId: "governance", surfaceLabel: "治理审计台", pageId: "collective", pageLabel: "共同治理", route: "/governance", auth: "governance", component: "governance-console", api: [], status: "reserved" },
];

export function connectionsBySurface(surfaceId: string): CodeConnection[] {
  return CODE_CONNECTIONS.filter((item) => item.surfaceId === surfaceId);
}

export function connectionCounts() {
  const total = CODE_CONNECTIONS.length;
  const implemented = CODE_CONNECTIONS.filter((item) => item.status === "implemented").length;
  const partial = CODE_CONNECTIONS.filter((item) => item.status === "partial").length;
  const reserved = CODE_CONNECTIONS.filter((item) => item.status === "reserved").length;
  return { total, implemented, partial, reserved };
}
