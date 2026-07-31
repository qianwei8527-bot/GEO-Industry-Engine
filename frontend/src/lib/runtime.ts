// Runtime Engine client ? single entry point for all configuration.
// Queries the backend Runtime endpoint and caches locally.
// All other frontend modules should use this instead of hardcoding.

import { refreshRegistry } from "./registryData";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export interface RuntimeState {
  registry: Record<string, any>;
  rules: { count: number; categories: Record<string, string[]> };
  scoring: { available: string[] };
  plugins: {
    views: string[];
    agents: string[];
    observations: string[];
    renderers: string[];
    ai_providers: string[];
  };
}

let _runtimeCache: RuntimeState | null = null;

export async function getRuntime(): Promise<RuntimeState> {
  if (_runtimeCache) return _runtimeCache;
  try {
    const res = await fetch(API_BASE + "/universe/runtime");
    _runtimeCache = await res.json();
    // Also refresh the registry data module
    await refreshRegistry();
    return _runtimeCache!;
  } catch {
    // Return a minimal fallback
    return {
      registry: {},
      rules: { count: 0, categories: {} },
      scoring: { available: [] },
      plugins: { views: [], agents: [], observations: [], renderers: [], ai_providers: [] },
    };
  }
}

export function invalidateRuntime(): void {
  _runtimeCache = null;
}

// Auto-load on client
if (typeof window !== "undefined") {
  getRuntime();
}
