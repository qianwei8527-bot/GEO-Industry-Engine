import { authedFetch } from "@/lib/authFetch";
import { EMPTY_TOOL_CONFIG, type ToolConfigDraft } from "./tool-config";

export async function fetchToolConfigs(realmId: string): Promise<ToolConfigDraft> {
  const res = await authedFetch(`/realm/${encodeURIComponent(realmId)}/tool-configs`);
  if (!res.ok) {
    throw new Error(`配置读取失败 (${res.status})`);
  }
  const body = (await res.json()) as { configs?: Partial<ToolConfigDraft> };
  const configs = body.configs || {};
  return {
    agent: { ...EMPTY_TOOL_CONFIG.agent, ...(configs.agent || {}) },
    skill: { ...EMPTY_TOOL_CONFIG.skill, ...(configs.skill || {}) },
    workflow: { ...EMPTY_TOOL_CONFIG.workflow, ...(configs.workflow || {}) },
    mcp: { ...EMPTY_TOOL_CONFIG.mcp, ...(configs.mcp || {}) },
  };
}

export async function saveToolConfig(
  realmId: string,
  key: "agent" | "skill" | "workflow" | "mcp",
  config: ToolConfigDraft[keyof ToolConfigDraft],
): Promise<void> {
  const res = await authedFetch(`/realm/${encodeURIComponent(realmId)}/tool-configs/${key}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ config }),
  });
  if (!res.ok) {
    throw new Error(`配置保存失败 (${res.status})`);
  }
}
