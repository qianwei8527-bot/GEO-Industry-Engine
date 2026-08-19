import type { ClientProjectContext } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export async function fetchClientProjects(token: string): Promise<ClientProjectContext> {
  const res = await fetch(`${API_BASE}/client/projects/${encodeURIComponent(token)}`);
  if (!res.ok) {
    let message = `令牌无效 (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: string };
      message = body.detail || message;
    } catch {
      // keep fallback
    }
    throw new Error(message);
  }
  return res.json() as Promise<ClientProjectContext>;
}

export async function submitClientFeedback(input: {
  token: string;
  projectId: string;
  originalText: string;
  scenario?: string;
  severity?: string;
}): Promise<{ status: string; issue_code: string }> {
  const res = await fetch(
    `${API_BASE}/client/projects/${encodeURIComponent(input.projectId)}/feedback`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: input.token,
        original_text: input.originalText,
        scenario: input.scenario,
        severity: input.severity || "medium",
      }),
    },
  );
  if (!res.ok) {
    let message = `反馈提交失败 (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: string };
      message = body.detail || message;
    } catch {
      // keep fallback
    }
    throw new Error(message);
  }
  return res.json() as Promise<{ status: string; issue_code: string }>;
}
