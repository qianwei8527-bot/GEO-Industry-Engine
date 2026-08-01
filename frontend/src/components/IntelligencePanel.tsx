
"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  Activity, BarChart3, Compass, BookOpen, Link2, Database,
  Briefcase, X, Shield, Eye, Zap, Star, Building2, Users,
  Factory, Target, Award, TrendingUp, ChevronRight, Loader2,
  Crosshair, Sparkles, Clock,
} from "lucide-react";

type PanelData = {
  node_id: string; node_type: string;
  data?: any;
  rules_cited?: any[];
  panel_sections?: Record<string, any>;
};

const TAB_ICONS: Record<string, any> = {
  status: Activity, assessment: BarChart3, direction: Compass,
  learning: BookOpen, resources: Link2, data: Database, business: Briefcase,
};

const TAB_LABELS_CN: Record<string, string> = {
  status: "当前状态",
  assessment: "能力测评",
  direction: "发展方向",
  learning: "学习成长",
  resources: "资源连接",
  data: "数据资产",
  business: "商业机会",
};

// ── Lifecycle stages (3.4) ──
const LIFECYCLE_STEPS = [
  { key: "position", label: "Position", cn: "定位", desc: "我在哪里？处于什么阶段？", icon: Crosshair },
  { key: "selfknow", label: "Know", cn: "自知", desc: "缺什么能力？缺什么关系？", icon: Eye },
  { key: "action", label: "Action", cn: "行动", desc: "下一步该做什么？", icon: Zap },
  { key: "provision", label: "Tool", cn: "使用", desc: "Universe提供的路径与资源", icon: Compass },
  { key: "accumulate", label: "Memory", cn: "沉淀", desc: "每一次行动留下记录", icon: Clock },
  { key: "reputation", label: "Trust", cn: "信誉", desc: "可追溯的资产", icon: Shield },
];

type Props = {
  nodeData: any;
  nodeDetail: any;
  onClose: () => void;
};

export default function IntelligencePanel({ nodeData, nodeDetail, onClose }: Props) {
  const [activeTab, setActiveTab] = useState("status");
  const [panelData, setPanelData] = useState<PanelData | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch panel data from the universe panel API
  useEffect(() => {
    if (!nodeData) return;
    const rawId = (nodeData.id || "").replace(/^(comp_|prov_|ind_|cap_)/, "");
    const nodeType = nodeData.type || "company";
    if (!rawId) return;

    setLoading(true);
    api.universe.panel(nodeType, rawId)
      .then((data) => { if (data) setPanelData(data as PanelData); })
      .catch(() => setPanelData(null))
      .finally(() => setLoading(false));
  }, [nodeData]);

  if (!nodeData) return null;

  const nodeType = panelData?.node_type || nodeDetail?.node_type || nodeData.type || "company";
  const tabs = ["status", "assessment", "direction", "learning", "resources", "data", "business"];
  const nodeName = panelData?.data?.node?.name || nodeDetail?.node_name || nodeData.label || nodeData.name || "Node";
  const geoScore = panelData?.data?.node?.geo_score ?? nodeDetail?.geo_score ?? nodeData?.geo_score ?? 0;
  const trustScore = panelData?.data?.node?.trust_score ?? nodeDetail?.trust_score ?? 0;
  const evidenceCount = panelData?.data?.intelligence?.evidence_count ?? nodeDetail?.evidence_count ?? 0;
  const capabilityCount = panelData?.data?.intelligence?.capability_count ?? nodeDetail?.capability_count ?? 0;
  const relationshipCount = panelData?.data?.graph?.relationship_count ?? nodeDetail?.relationship_count ?? 0;
  const growthStage = panelData?.data?.evolution?.growth_stage ?? nodeDetail?.growth_stage ?? null;
  const reputation = panelData?.data?.intelligence?.reputation ?? nodeDetail?.reputation ?? null;
  const competitors = panelData?.data?.graph?.competitors ?? nodeDetail?.competitors ?? [];
  const rulesCited = panelData?.rules_cited ?? [];

  // Determine which lifecycle step the node is at
  const lifecycleActiveIndex = (() => {
    if (!geoScore && !evidenceCount) return 0; // just positioned
    if (geoScore > 0 && evidenceCount === 0) return 1; // knows itself but no action
    if (evidenceCount > 0 && relationshipCount === 0) return 2; // acting
    if (relationshipCount > 0 && (!reputation || reputation.total_score < 20)) return 3; // using tools
    if (reputation && reputation.total_score >= 20 && reputation.total_score < 50) return 4; // accumulating
    if (reputation && reputation.total_score >= 50) return 5; // trusted
    return 0;
  })();

  function NodeIcon() {
    switch (nodeType) {
      case "company": return <Building2 className="w-4 h-4 text-blue-500" />;
      case "provider": return <Users className="w-4 h-4 text-green-500" />;
      case "industry": return <Factory className="w-4 h-4 text-purple-500" />;
      case "capability": return <Target className="w-4 h-4 text-amber-500" />;
      default: return <Compass className="w-4 h-4 text-slate-500" />;
    }
  }

  function scoreColor(s: number) {
    return s >= 70 ? "text-green-600" : s >= 40 ? "text-amber-600" : "text-red-600";
  }

  return (
    <div className="w-80 h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-200 bg-slate-50">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
            <NodeIcon />
            {nodeName}
          </h3>
          <p className="text-[10px] text-slate-400 mt-0.5 capitalize">{nodeType}</p>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-200 rounded">
          <X className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {/* ── Lifecycle Progress Bar (3.4) ── */}
      <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-purple-50 px-3 py-2.5">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-semibold text-slate-600">Universe Lifecycle</span>
          <span className="text-[9px] text-slate-400">
            {LIFECYCLE_STEPS[lifecycleActiveIndex]?.cn}阶段
          </span>
        </div>
        <div className="flex items-center gap-0.5">
          {LIFECYCLE_STEPS.map((step, i) => {
            const isActive = i <= lifecycleActiveIndex;
            const isCurrent = i === lifecycleActiveIndex;
            const StepIcon = step.icon;
            return (
              <div key={step.key} className="flex items-center">
                <div className={`flex flex-col items-center gap-0.5 transition-all ${isActive ? "opacity-100" : "opacity-30"}`}
                  title={step.desc}>
                  <StepIcon className={`w-3 h-3 ${isCurrent ? "text-blue-600" : isActive ? "text-green-500" : "text-slate-300"}`} />
                  <span className="text-[7px] text-slate-500 leading-tight">{step.cn}</span>
                </div>
                {i < 5 && <div className={`w-3 h-px ${i < lifecycleActiveIndex ? "bg-green-400" : "bg-slate-200"}`} />}
              </div>
            );
          })}
        </div>
        {/* Next action hint */}
        {lifecycleActiveIndex < 5 && (
          <p className="text-[9px] text-blue-600 mt-1.5 flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5" />
            Next: {LIFECYCLE_STEPS[lifecycleActiveIndex + 1]?.desc}
          </p>
        )}
        {lifecycleActiveIndex >= 5 && (
          <p className="text-[9px] text-green-600 mt-1.5 flex items-center gap-1">
            <Shield className="w-2.5 h-2.5" />
            Reputation asset established — maintain and grow
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 bg-white overflow-x-auto">
        {tabs.map((t) => (
          <button key={t} onClick={() => setActiveTab(t)}
            className={`flex items-center gap-1 px-3 py-2 text-[10px] font-medium whitespace-nowrap border-b-2 transition-all ${
              activeTab === t ? "border-blue-500 text-blue-600" : "border-transparent text-slate-400 hover:text-slate-600"
            }`}
          >
            {TAB_LABELS_CN[t]}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
          </div>
        )}

        {!loading && activeTab === "status" && (
          <div className="space-y-3">
            {/* Score Cards */}
            <div className="grid grid-cols-2 gap-2">
              <ScoreCard label="GEO Score" value={geoScore} icon={Target} color={scoreColor(geoScore)} />
              <ScoreCard label="Trust Score" value={trustScore} icon={Shield} color={scoreColor(trustScore)} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <ScoreCard label="Evidence" value={evidenceCount} icon={Database} />
              <ScoreCard label="Capabilities" value={capabilityCount} icon={Zap} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <ScoreCard label="Relationships" value={relationshipCount} icon={Link2} />
              <ScoreCard label="Reputation" value={reputation?.total_score ?? "N/A"} icon={Star} color={reputation?.total_score ? scoreColor(reputation.total_score) : "text-slate-400"} />
            </div>

            {/* Lifecycle Map */}
            <div className="bg-white border border-slate-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Lifecycle Position</h4>
              <div className="space-y-1.5">
                {LIFECYCLE_STEPS.map((step, i) => (
                  <div key={step.key} className={`flex items-center gap-2 text-[10px] ${i <= lifecycleActiveIndex ? "text-gray-700" : "text-slate-300"}`}>
                    <step.icon className={`w-3 h-3 ${i < lifecycleActiveIndex ? "text-green-500" : i === lifecycleActiveIndex ? "text-blue-500" : "text-slate-300"}`} />
                    <span className="font-medium w-8">{step.cn}</span>
                    <span className="text-slate-400">{step.desc}</span>
                    {i < lifecycleActiveIndex && <span className="ml-auto text-green-500">OK</span>}
                    {i === lifecycleActiveIndex && <span className="ml-auto text-blue-500 text-[8px] animate-pulse">NOW</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {!loading && activeTab === "assessment" && (
          <div className="space-y-3">
            <div className="bg-white border border-slate-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Capability Assessment</h4>
              <div className="space-y-2 text-xs">
                <BarRow label="GEO Score" value={geoScore} max={100} color="bg-blue-500" />
                <BarRow label="Trust" value={trustScore} max={100} color="bg-green-500" />
                <BarRow label="Evidence" value={Math.min(evidenceCount * 10, 100)} max={100} color="bg-amber-500" />
                <BarRow label="Relations" value={Math.min(relationshipCount * 10, 100)} max={100} color="bg-purple-500" />
              </div>
            </div>
            <p className="text-[10px] text-slate-400 text-center">Assessment based on Universe Rules engine</p>
          </div>
        )}

        {!loading && activeTab === "direction" && (
          <div className="space-y-3">
            <div className="bg-white border border-slate-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Growth Direction</h4>
              {growthStage ? (
                <div className="space-y-2 text-xs">
                  <Row label="Stage" value={growthStage.stage} />
                  <Row label="Level" value={"Lv." + growthStage.level} />
                  <Row label="Progress" value={(growthStage.progress || 0) + "%"} />
                </div>
              ) : (
                <p className="text-xs text-slate-400">Growth stage data not yet available.</p>
              )}
            </div>
            {/* Next recommended action */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-blue-700 uppercase mb-1.5">Recommended Next</h4>
              <p className="text-[10px] text-blue-600">
                {lifecycleActiveIndex <= 1 ? "Run GEO Detection to establish your baseline position" :
                 lifecycleActiveIndex === 2 ? "Connect with service providers matching your capability gaps" :
                 lifecycleActiveIndex === 3 ? "Build evidence records through certifications and case studies" :
                 lifecycleActiveIndex === 4 ? "Continue accumulating trust data — your reputation is growing" :
                 "Leverage your reputation to explore new markets"}
              </p>
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-2.5">
              <p className="text-[10px] text-amber-700">R04: Growth = Learn → Practice → Cases → Trust → Ecosystem Node</p>
            </div>
          </div>
        )}

        {!loading && activeTab === "data" && (
          <div className="space-y-3">
            <div className="bg-white border border-slate-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Data Assets</h4>
              <div className="space-y-2 text-xs">
                <Row label="Evidence Records" value={evidenceCount} />
                <Row label="Capabilities" value={capabilityCount} />
                <Row label="Relationships" value={relationshipCount} />
              </div>
            </div>
            {competitors.length > 0 && (
              <div className="bg-white border border-slate-200 rounded-lg p-3">
                <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Competitors</h4>
                <div className="flex flex-wrap gap-1">
                  {competitors.map((c: any, i: number) => (
                    <span key={i} className="bg-red-50 text-red-700 text-[10px] px-2 py-0.5 rounded">{c.name}</span>
                  ))}
                </div>
              </div>
            )}
            <p className="text-[10px] text-slate-400 text-center">
              Data accumulation → Reputation capital (Principle 3.4)
            </p>
          </div>
        )}

        {!loading && activeTab === "business" && (
          <div className="space-y-3">
            <div className="bg-white border border-slate-200 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Commercial Opportunities</h4>
              <p className="text-xs text-slate-400 mb-3">Candidate providers and market demands for this node.</p>
              <a href="/marketplace" className="flex items-center gap-2 w-full px-3 py-2 bg-green-50 text-green-700 rounded-lg text-xs font-medium hover:bg-green-100">
                <Briefcase className="w-3.5 h-3.5" /> Find Providers <ChevronRight className="w-3 h-3 ml-auto" />
              </a>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5">
              <p className="text-[10px] text-blue-700">R07: Marketplace is the natural business exit of the industry map.</p>
            </div>
          </div>
        )}

        {!loading && activeTab === "learning" && <PlaceholderTab title="Learning & Growth" desc="Courses, certification paths, and skill trees will appear here." icon={BookOpen} />}
        {!loading && activeTab === "resources" && <PlaceholderTab title="Resource Connections" desc="Experts, tools, and service providers relevant to this node." icon={Link2} />}
      </div>
    </div>
  );
}

function PlaceholderTab({ title, desc, icon: Icon }: { title: string; desc: string; icon: any }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <Icon className="w-8 h-8 text-slate-300 mb-2" />
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className="text-xs text-slate-400 mt-1">{desc}</p>
    </div>
  );
}

function Row({ label, value, bold, color, capitalize }: { label: string; value: any; bold?: boolean; color?: string; capitalize?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className={`${bold ? "font-bold " : "font-medium "}${color || "text-gray-700"} ${capitalize ? "capitalize" : ""}`}>{value}</span>
    </div>
  );
}

function ScoreCard({ label, value, icon: Icon, color }: { label: string; value: any; icon: any; color?: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-2.5">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="w-3 h-3 text-slate-400" />
        <span className="text-[10px] text-slate-500">{label}</span>
      </div>
      <span className={`text-lg font-bold ${color || "text-gray-700"}`}>{value}</span>
    </div>
  );
}

function BarRow({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div>
      <div className="flex justify-between text-[10px] mb-0.5">
        <span className="text-slate-500">{label}</span>
        <span className="font-medium text-gray-700">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-slate-100 rounded-full">
        <div className={`h-full rounded-full ${color}`} style={{ width: pct + "%" }} />
      </div>
    </div>
  );
}
