export interface AgentConfigDraft {
  name: string;
  tools: string;
  budget: string;
}

export interface SkillConfigDraft {
  name: string;
  version: string;
  source: string;
}

export interface WorkflowConfigDraft {
  name: string;
  steps: string;
  approvalPoint: string;
}

export interface McpConfigDraft {
  name: string;
  tools: string;
  secretPolicy: string;
}

export interface ToolConfigDraft {
  agent: AgentConfigDraft;
  skill: SkillConfigDraft;
  workflow: WorkflowConfigDraft;
  mcp: McpConfigDraft;
}

export const EMPTY_TOOL_CONFIG: ToolConfigDraft = {
  agent: { name: "", tools: "", budget: "50" },
  skill: { name: "", version: "v0.1", source: "realm_owner" },
  workflow: { name: "", steps: "", approvalPoint: "publish" },
  mcp: { name: "", tools: "", secretPolicy: "backend_only" },
};

export function loadToolConfigDraft(realmId: string): ToolConfigDraft {
  try {
    const raw = localStorage.getItem(`heng_yu_tool_config_${realmId}`);
    if (!raw) return EMPTY_TOOL_CONFIG;
    const parsed = JSON.parse(raw) as Partial<ToolConfigDraft>;
    return {
      agent: { ...EMPTY_TOOL_CONFIG.agent, ...parsed.agent },
      skill: { ...EMPTY_TOOL_CONFIG.skill, ...parsed.skill },
      workflow: { ...EMPTY_TOOL_CONFIG.workflow, ...parsed.workflow },
      mcp: { ...EMPTY_TOOL_CONFIG.mcp, ...parsed.mcp },
    };
  } catch {
    return EMPTY_TOOL_CONFIG;
  }
}

export function saveToolConfigDraft(realmId: string, draft: ToolConfigDraft): void {
  localStorage.setItem(`heng_yu_tool_config_${realmId}`, JSON.stringify(draft));
}
