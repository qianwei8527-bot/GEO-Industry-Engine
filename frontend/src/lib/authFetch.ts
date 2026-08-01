"use client";

// C6.4 Gate 0: safe automatic refresh token renewal.
// Single refresh lock, one retry, never logs tokens, clears session on failure.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let refreshPromise: Promise<string | null> | null = null;
let refreshAttempts = 0;

export function getToken(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("geo_token") || "";
}

export function clearSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("geo_token");
  localStorage.removeItem("geo_refresh_token");
  const next = window.location.pathname;
  window.location.href = "/login?next=" + encodeURIComponent(next);
}

async function refreshToken(): Promise<string | null> {
  const rt = typeof window !== "undefined" ? localStorage.getItem("geo_refresh_token") : "";
  if (!rt) return null;
  if (refreshAttempts >= 1) return null;
  refreshAttempts += 1;
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!res.ok) { clearSession(); return null; }
    const data = await res.json();
    localStorage.setItem("geo_token", data.access_token);
    if (data.refresh_token) localStorage.setItem("geo_refresh_token", data.refresh_token);
    refreshAttempts = 0;
    return data.access_token;
  } catch {
    clearSession();
    return null;
  }
}

export async function authedFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (res.status === 401 && token) {
    // Single-flight refresh lock
    if (!refreshPromise) {
      refreshPromise = refreshToken().finally(() => { refreshPromise = null; });
    }
    const newToken = await refreshPromise;
    if (!newToken) return res;
    headers["Authorization"] = `Bearer ${newToken}`;
    return fetch(API_BASE + path, { ...options, headers });
  }
  return res;
}
