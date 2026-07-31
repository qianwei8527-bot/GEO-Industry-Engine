// useRegistry ? React hook for Universe Registry access.
// All components should use this hook instead of hardcoding node type metadata.

"use client";

import { useMemo } from "react";
import {
  NodeTypeMeta,
  getNodeColor as _getNodeColor,
  getNodeGlow as _getNodeGlow,
  getNodeSize as _getNodeSize,
  getNodeLabel as _getNodeLabel,
  getNodeType as _getNodeType,
} from "./registryData";

export interface UseRegistryReturn {
  /** Get the color for a node type */
  color: (typeId: string, fallback?: string) => string;
  /** Get the glow color for a node type */
  glow: (typeId: string, fallback?: string) => string;
  /** Get the size for a node type */
  size: (typeId: string, fallback?: number) => number;
  /** Get the display label for a node type */
  label: (typeId: string, fallback?: string) => string;
  /** Get the full NodeTypeMeta for a node type */
  meta: (typeId: string) => NodeTypeMeta;
  /** Check if a string is a valid node type */
  isValidType: (typeId: string) => boolean;
  /** Get all registered node types */
  allTypes: () => NodeTypeMeta[];
  /** Get a normalized type id (strips prefixes like comp_, prov_, etc.) */
  normalizeType: (typeId: string) => string;
}

const TYPE_ID_MAP: Record<string, string> = {
  company: "company",
  provider: "provider",
  industry: "industry",
  capability: "capability",
  person: "person",
  product: "product",
  role: "role",
  policy: "policy",
  tool: "tool",
  service: "service",
  "ai_agent": "ai_agent",
  government: "government",
  knowledge: "knowledge",
  event: "event",
};

export function useRegistry(): UseRegistryReturn {
  return useMemo(() => ({
    color: _getNodeColor,
    glow: _getNodeGlow,
    size: _getNodeSize,
    label: _getNodeLabel,
    meta: _getNodeType,
    isValidType: (typeId: string) => {
      const cleaned = typeId.replace(/^(comp_|prov_|ind_|cap_)/, "");
      return cleaned in TYPE_ID_MAP;
    },
    allTypes: () => Object.values(TYPE_ID_MAP).map(id => _getNodeType(id)),
    normalizeType: (typeId: string) => {
      const cleaned = typeId.replace(/^(comp_|prov_|ind_|cap_)/, "");
      return TYPE_ID_MAP[cleaned] || cleaned;
    },
  }), []);
}

// Export for non-React usage
export const registry = {
  color: _getNodeColor,
  glow: _getNodeGlow,
  size: _getNodeSize,
  label: _getNodeLabel,
  meta: _getNodeType,
  normalizeType: (typeId: string) => {
    const cleaned = typeId.replace(/^(comp_|prov_|ind_|cap_)/, "");
    return TYPE_ID_MAP[cleaned] || cleaned;
  },
};
