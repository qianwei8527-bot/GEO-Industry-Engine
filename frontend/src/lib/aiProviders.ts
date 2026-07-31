// AI Provider client ? unified access to all AI model providers.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export interface AIProviderInfo {
  id: string;
  name: string;
  default_model: string;
  capabilities: Record<string, unknown>;
}

export interface AIProvidersManifest {
  default_provider: string;
  providers: AIProviderInfo[];
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  content: string;
  model: string;
  usage: Record<string, number>;
  finish_reason: string;
}

export async function listAIProviders(): Promise<AIProvidersManifest> {
  const res = await fetch(API_BASE + "/universe/ai/providers");
  return res.json();
}

export async function aiChat(params: {
  provider?: string;
  model?: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
}): Promise<ChatResponse> {
  const res = await fetch(API_BASE + "/universe/ai/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function listProviderModels(providerId: string): Promise<{ provider: string; models: string[] }> {
  const res = await fetch(API_BASE + "/universe/ai/providers/" + providerId + "/models");
  return res.json();
}
