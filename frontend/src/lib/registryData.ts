// Static registry data — loaded once, no Provider/Context needed.
// This avoids Next.js SSR issues with client components in server layouts.
// When the backend is available, refresh() can be called to reload from API.

export interface NodeTypeMeta {
  type_id: string;
  label: string; label_en: string;
  icon: string;
  color: string; glow: string;
  size: number; size_3d: number;
  layer: number;
  description: string;
}

const FALLBACK: Record<string, NodeTypeMeta> = {
  company: { type_id: "company", label: "企业", label_en: "Company", icon: "Building2", color: "#3b82f6", glow: "#60a5fa", size: 16, size_3d: 0.5, layer: 1, description: "" },
  provider: { type_id: "provider", label: "服务商", label_en: "Provider", icon: "Users", color: "#22c55e", glow: "#4ade80", size: 13, size_3d: 0.45, layer: 2, description: "" },
  industry: { type_id: "industry", label: "行业", label_en: "Industry", icon: "Factory", color: "#a855f7", glow: "#c084fc", size: 22, size_3d: 0.7, layer: 0, description: "" },
  capability: { type_id: "capability", label: "能力", label_en: "Capability", icon: "Target", color: "#f59e0b", glow: "#fbbf24", size: 10, size_3d: 0.35, layer: 3, description: "" },
  person: { type_id: "person", label: "人物", label_en: "Person", icon: "User", color: "#ec4899", glow: "#f472b6", size: 8, size_3d: 0.3, layer: 4, description: "" },
  product: { type_id: "product", label: "产品", label_en: "Product", icon: "Package", color: "#06b6d4", glow: "#22d3ee", size: 11, size_3d: 0.4, layer: 4, description: "" },
};

let _registry = FALLBACK;

export function getNodeType(typeId: string): NodeTypeMeta {
  const cleaned = typeId.replace(/^(comp_|prov_|ind_|cap_)/, "");
  const mapped: Record<string, string> = { company: "company", provider: "provider", industry: "industry", capability: "capability" };
  return _registry[mapped[cleaned] || cleaned] || FALLBACK.company;
}

export function getNodeColor(typeId: string, fallback = "#94a3b8"): string {
  return getNodeType(typeId).color || fallback;
}

export function getNodeGlow(typeId: string, fallback = "#94a3b8"): string {
  return getNodeType(typeId).glow || fallback;
}

export function getNodeSize(typeId: string, fallback = 14): number {
  return getNodeType(typeId).size || fallback;
}

export function getNodeLabel(typeId: string, fallback = ""): string {
  return getNodeType(typeId).label || fallback;
}

export function listNodeTypes(): NodeTypeMeta[] {
  return Object.values(_registry);
}

export async function refreshRegistry(): Promise<void> {
  try {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";
    const res = await fetch(API_BASE + "/universe/registry");
    const data = await res.json();
    if (data?.node_types) {
      const mapped: Record<string, NodeTypeMeta> = {};
      for (const [key, val] of Object.entries(data.node_types)) {
        const v = val as any;
        mapped[key] = {
          type_id: v.type_id || key,
          label: v.label || key,
          label_en: v.label_en || key,
          icon: v.icon || "",
          color: v.color || "#94a3b8",
          glow: v.glow || "#94a3b8",
          size: v.size || 14,
          size_3d: v.size_3d || 0.4,
          layer: v.layer || 99,
          description: v.description || "",
        };
      }
      _registry = mapped;
    }
  } catch {
    // Keep fallback on error
  }
}

// Auto-refresh on load
if (typeof window !== "undefined") {
  refreshRegistry();
}
