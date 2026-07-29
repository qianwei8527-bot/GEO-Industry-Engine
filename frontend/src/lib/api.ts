const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

interface RequestOptions { method?: string; body?: unknown; token?: string; }
async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method, headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) { const e = await res.json().catch(() => ({ detail: "Request failed" })); throw new Error(e.detail || "Request failed"); }
  return res.json();
}

export const api = {
  auth: {
    register: (d: { email: string; password: string; name: string }) => apiRequest("/auth/register", { method: "POST", body: d }),
    login: (d: { email: string; password: string }) => apiRequest("/auth/login", { method: "POST", body: d }),
  },
  users: { me: (t: string) => apiRequest("/users/me", { token: t }) },
  entities: {
    list: (type?: string) => apiRequest("/entities/?" + (type ? "entity_type=" + type : "")),
    get: (id: string) => apiRequest("/entities/" + id),
  },
  companies: {
    list: (industry?: string) => apiRequest("/companies/?" + (industry ? "industry_id=" + industry : "")),
    get: (id: string) => apiRequest("/companies/" + id),
  },
  industries: {
    list: () => apiRequest("/industries/"),
    get: (id: string) => apiRequest("/industries/" + id),
  },
  context: {
    company: (id: string) => apiRequest("/context/company/" + id),
    industry: (id: string) => apiRequest("/context/industry/" + id),
    capability: (id: string) => apiRequest("/context/capability/" + id),
    query: (q: string, limit = 10) => apiRequest("/context/query", { method: "POST", body: { query: q, limit } }),
  },
  decision: {
    company: (id: string) => apiRequest("/decision/company/" + id),
    industry: (id: string) => apiRequest("/decision/industry/" + id),
    analyze: (q: string) => apiRequest("/decision/analyze", { method: "POST", body: { query: q } }),
  },
  evidence: {
    list: (targetId?: string) => apiRequest("/evidence/?" + (targetId ? "target_id=" + targetId : "")),
    create: (d: any) => apiRequest("/evidence/", { method: "POST", body: d }),
  },
  relationships: { list: () => apiRequest("/relationships/") },
  admin: {
    listConfigs: () => apiRequest("/admin/configs/"),
    getConfig: (name: string) => apiRequest("/admin/configs/" + name),
    saveConfig: (name: string, value: any) => apiRequest("/admin/configs/" + name, { method: "PUT", body: { name, value } }),
  },
  certification: {
    list: () => apiRequest("/certifications/"),
    get: (id: string) => apiRequest("/certifications/" + id),
    apply: (d: any) => apiRequest("/certifications/apply", { method: "POST", body: d }),
  },
  marketplace: {
    listProviders: () => apiRequest("/marketplace/providers/"),
    listDemands: () => apiRequest("/marketplace/demands/"),
    getProvider: (id: string) => apiRequest("/marketplace/providers/" + id),
    getDemand: (id: string) => apiRequest("/marketplace/demands/" + id),
  },
  agent: { analyze: (q: string) => apiRequest("/agent/analyze", { method: "POST", body: { query: q } }) },
};
