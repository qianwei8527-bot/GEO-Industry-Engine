/**
 * Universe Node — the unified protocol for all Views.
 * Every View (Ecosystem, Business, Growth, Distribution, Future)
 * reads nodes through this interface.
 */

export interface UniverseNode {
  id: string;
  type: "company" | "provider" | "industry" | "capability" | "person" | "product";
  
  // Identity (from IdentityProfile)
  identity: {
    displayName: string;
    identityType: string;
    tagline?: string;
    industryContext?: string;
  };

  // Position (5D coordinates from Position Engine)
  position: {
    geoScore?: number;
    visibilityScore?: number;
    trustScore?: number;
    capabilityScore?: number;
    growthStage?: string;
    reputationLevel?: string;
    competitionPosition?: string;
  };

  // Growth (from Growth Engine)
  growth: {
    currentStage: string;
    evidenceCount: number;
    certificationCount: number;
    relationshipCount: number;
  };

  // Connections (from Ecosystem)
  connections: {
    competitors: number;
    partners: number;
    providers: number;
  };

  // Evolution (from NodeSnapshot)
  evolution?: {
    snapshotCount: number;
    trend: string;
    spanDays: number;
    totalGeoDelta: number;
    stageFrom?: string;
    stageTo?: string;
  };

  // Raw data (for direct access)
  raw: Record<string, any>;
}

/** Five Universe Views */
export type UniverseView = "ecosystem" | "business" | "growth" | "distribution" | "future";

export const FIVE_VIEWS: Array<{
  id: UniverseView;
  name: string;
  nameCn: string;
  desc: string;
}> = [
  { id: "ecosystem", name: "Ecosystem View", nameCn: "产业生态", desc: "我在哪里？" },
  { id: "business", name: "Business View", nameCn: "产业价值", desc: "如何创造价值？" },
  { id: "growth", name: "Growth View", nameCn: "成长路径", desc: "如何提升？" },
  { id: "distribution", name: "Distribution View", nameCn: "产业分布", desc: "机遇在哪里？" },
  { id: "future", name: "Future View", nameCn: "未来演化", desc: "向哪里去？" },
];

/** Build a UniverseNode from raw API data */
export function toUniverseNode(raw: any): UniverseNode {
  return {
    id: raw.id || "",
    type: (raw.type || raw.entity_type || "company") as UniverseNode["type"],
    identity: {
      displayName: raw.name || raw.display_name || "",
      identityType: raw.identity_type || raw.type || "企业",
      tagline: raw.tagline,
      industryContext: raw.industry_context || raw.industry_name,
    },
    position: {
      geoScore: raw.geo_score,
      visibilityScore: raw.visibility_score,
      trustScore: raw.trust_score,
      capabilityScore: raw.capability_score,
      growthStage: raw.growth_stage,
      reputationLevel: raw.reputation_level,
      competitionPosition: raw.competition_position,
    },
    growth: {
      currentStage: raw.growth_stage || "Entry",
      evidenceCount: raw.evidence_count || 0,
      certificationCount: raw.certification_count || 0,
      relationshipCount: raw.relationship_count || 0,
    },
    connections: {
      competitors: raw.competitor_count || 0,
      partners: raw.relationship_count || 0,
      providers: 0,
    },
    evolution: undefined, // fetched separately
    raw,
  };
}
