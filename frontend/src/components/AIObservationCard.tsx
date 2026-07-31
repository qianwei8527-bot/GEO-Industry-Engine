"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus, Activity, Zap } from "lucide-react";

type Props = {
  entityId: string;
  entityName?: string;
  entityType?: string;
};

/** AI Observation Card — shows the node's evolution summary.
 *  Fetches from /api/v1/universe/identity/evolution/{entityId}
 *  and renders a compact insight card. */
export default function AIObservationCard({ entityId, entityName, entityType }: Props) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!entityId) return;
    fetch("http://localhost:8080/api/v1/universe/identity/evolution/" + entityId)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [entityId]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-500 p-2">
        <Activity className="w-3 h-3 animate-pulse" />
        AI 正在观察节点...
      </div>
    );
  }

  if (!data) return null;

  const isNewborn = data.status === "newborn";
  const trend = data.trajectory?.trend;

  return (
    <div className="p-3 rounded-lg border bg-gradient-to-r" style={{
      borderColor: isNewborn ? "rgba(107,114,128,0.3)" : trend === "strong_rising" || trend === "rising" ? "rgba(52,211,153,0.3)" : "rgba(107,114,128,0.3)",
      background: isNewborn ? "rgba(107,114,128,0.05)" : "rgba(52,211,153,0.03)",
    }}>
      <div className="flex items-center gap-2 mb-1">
        <Zap className="w-3.5 h-3.5" style={{ color: isNewborn ? "#9CA3AF" : "#34D399" }} />
        <span className="text-xs font-medium" style={{ color: isNewborn ? "#9CA3AF" : "#34D399" }}>
          {isNewborn ? "新节点" : "AI 观察"}
        </span>
        {!isNewborn && data.evolution_events && (
          <span className="text-xs text-gray-500">
            {data.evolution_events.length} 次变化 · {data.span_days} 天
          </span>
        )}
      </div>

      <p className="text-xs text-gray-400 leading-relaxed">
        {isNewborn
          ? data.message || "节点刚刚进入 Universe，等待第一次变化。"
          : data.trajectory?.message || "节点正在演化中。"}
      </p>

      {!isNewborn && data.trajectory?.total_geo_delta !== undefined && (
        <div className="flex items-center gap-3 mt-2">
          <span className="text-xs font-mono" style={{
            color: data.trajectory.total_geo_delta > 0 ? "#34D399" : data.trajectory.total_geo_delta < 0 ? "#F87171" : "#9CA3AF",
          }}>
            GEO {data.trajectory.total_geo_delta > 0 ? "+" : ""}{data.trajectory.total_geo_delta}
          </span>
          {data.trajectory.stage_from !== data.trajectory.stage_to && (
            <span className="text-xs text-gray-500">
              {data.trajectory.stage_from} → {data.trajectory.stage_to}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
