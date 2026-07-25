const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return res.json();
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; name: string }) =>
      apiRequest("/auth/register", { method: "POST", body: data }),
    login: (data: { email: string; password: string }) =>
      apiRequest("/auth/login", { method: "POST", body: data }),
  },
  users: {
    me: (token: string) => apiRequest("/users/me", { token }),
    update: (data: Record<string, unknown>, token: string) =>
      apiRequest("/users/me", { method: "PUT", body: data, token }),
  },
};
