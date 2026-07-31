"use client";

import { useState, useEffect, createContext, useContext } from "react";
import { api } from "./api";

// ─── Types ─────────────────────────────────────────────────

export interface NodeTypeMeta {
  type_id: string;
  label: string;
  label_en: string;
  icon: string;
  color: string;
  glow: string;
  size: number;
  size_3d: number;
  layer: number;
  description: string;
  capabilities: string[];
  lifecycle_stages: string[];
}

export interface RelationshipTypeMeta {
  type_id: string;
  label: string;
  label_en: string;
  color: string;
  bidirectional: boolean;
  allowed_pairs: string[][];
}

export interface ViewMeta {
  view_id: string;
  label: string;
  label_en: string;
  question: string;
  question_en: string;
  icon: string;
  description: string;
  layout_2d: string;
  layout_3d: string;
}

export interface LifecycleStageMeta {
  key: string;
  label: string;
  label_en: string;
  icon: string;
  order: number;
  description: string;
}

export interface CapabilityMeta {
  id: string;
  label: string;
  label_en: string;
  category: string;
  description: string;
}

export interface UniverseRegistry {
  version: string;
  description: string;
  node_types: Record<string, NodeTypeMeta>;
  relationship_types: Record<string, RelationshipTypeMeta>;
  views: Record<string, ViewMeta>;
  lifecycle: LifecycleStageMeta[];
  capabilities: CapabilityMeta[];
}

// ─── Context ────────────────────────────────────────────────

const RegistryContext = createContext<UniverseRegistry | null>(null);

export function useRegistry(): UniverseRegistry | null {
  return useContext(RegistryContext);
}

// ─── Provider ───────────────────────────────────────────────

export function UniverseRegistryProvider({ children }: { children: React.ReactNode }) {
  const [registry, setRegistry] = useState<UniverseRegistry | null>(null);

  useEffect(() => {
    // Use the existing api client pattern
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";
    fetch(API_BASE + "/universe/registry")
      .then((res) => res.json())
      .then((data) => setRegistry(data))
      .catch(() => {
        // Fallback: inline minimal registry for offline dev
        setRegistry(getFallbackRegistry());
      });
  }, []);

  return (
    <RegistryContext.Provider value={registry}>
      {children}
    </RegistryContext.Provider>
  );
}

// ─── Hook: useNodeType ──────────────────────────────────────

export function useNodeType(typeId: string): NodeTypeMeta | undefined {
  const registry = useRegistry();
  if (!registry) return undefined;
  // Try exact match first, then try without prefix (comp_ -> company)
  const result = registry.node_types[typeId];
  if (result) return result;
  const cleaned = typeId.replace(/^(comp_|prov_|ind_|cap_)/, "");
  const mapped: Record<string, string> = {
    company: "company", provider: "provider",
    industry: "industry", capability: "capability",
  };
  return registry.node_types[mapped[cleaned] || cleaned];
}

// ─── Hook: useNodeColor ─────────────────────────────────────

export function useNodeColor(typeId: string, fallback = "#94a3b8"): string {
  const meta = useNodeType(typeId);
  return meta?.color || fallback;
}

export function useNodeGlow(typeId: string, fallback = "#94a3b8"): string {
  const meta = useNodeType(typeId);
  return meta?.glow || fallback;
}

export function useNodeSize(typeId: string, fallback = 14): number {
  const meta = useNodeType(typeId);
  return meta?.size || fallback;
}

export function useNodeLabel(typeId: string, fallback = ""): string {
  const meta = useNodeType(typeId);
  return meta?.label || fallback;
}

export function useViews(): ViewMeta[] {
  const registry = useRegistry();
  if (!registry) return [];
  return Object.values(registry.views);
}

// ─── Fallback registry (offline dev) ────────────────────────

function getFallbackRegistry(): UniverseRegistry {
  return {
    version: "fallback",
    description: "Minimal fallback registry",
    node_types: {
      company: { type_id: "company", label: "企业", label_en: "Company", icon: "Building2", color: "#3b82f6", glow: "#60a5fa", size: 16, size_3d: 0.5, layer: 1, description: "", capabilities: [], lifecycle_stages: [] },
      provider: { type_id: "provider", label: "服务商", label_en: "Provider", icon: "Users", color: "#22c55e", glow: "#4ade80", size: 13, size_3d: 0.45, layer: 2, description: "", capabilities: [], lifecycle_stages: [] },
      industry: { type_id: "industry", label: "行业", label_en: "Industry", icon: "Factory", color: "#a855f7", glow: "#c084fc", size: 22, size_3d: 0.7, layer: 0, description: "", capabilities: [], lifecycle_stages: [] },
      capability: { type_id: "capability", label: "能力", label_en: "Capability", icon: "Target", color: "#f59e0b", glow: "#fbbf24", size: 10, size_3d: 0.35, layer: 3, description: "", capabilities: [], lifecycle_stages: [] },
      person: { type_id: "person", label: "人物", label_en: "Person", icon: "User", color: "#ec4899", glow: "#f472b6", size: 8, size_3d: 0.3, layer: 4, description: "", capabilities: [], lifecycle_stages: [] },
      product: { type_id: "product", label: "产品", label_en: "Product", icon: "Package", color: "#06b6d4", glow: "#22d3ee", size: 11, size_3d: 0.4, layer: 4, description: "", capabilities: [], lifecycle_stages: [] },
    },
    relationship_types: {},
    views: {},
    lifecycle: [],
    capabilities: [],
  };
}
