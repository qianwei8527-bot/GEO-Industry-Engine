// Plugin SDK client ? frontend plugin manifest loader.
// Queries the backend plugin registry and provides typed access.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export interface PluginDef {
  plugin_id: string;
  enabled: boolean;
  class: string;
}

export interface PluginManifest {
  version: string;
  plugins: {
    view_plugins: Record<string, PluginDef>;
    observation_plugins: Record<string, PluginDef>;
    agent_plugins: Record<string, PluginDef>;
    renderer_plugins: Record<string, PluginDef>;
  };
  loaded_count: {
    views: number;
    observations: number;
    agents: number;
    renderers: number;
  };
}

let _manifest: PluginManifest | null = null;

export async function getPluginManifest(): Promise<PluginManifest> {
  if (_manifest) return _manifest;
  try {
    const res = await fetch(API_BASE + "/universe/plugins");
    _manifest = await res.json();
    return _manifest!;
  } catch {
    return {
      version: "0.0.0",
      plugins: { view_plugins: {}, observation_plugins: {}, agent_plugins: {}, renderer_plugins: {} },
      loaded_count: { views: 0, observations: 0, agents: 0, renderers: 0 },
    };
  }
}

export function invalidatePlugins(): void {
  _manifest = null;
}

// Auto-load on client
if (typeof window !== "undefined") {
  getPluginManifest();
}
