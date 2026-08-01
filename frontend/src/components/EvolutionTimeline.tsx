"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus, GitBranch, ArrowRight, Award, Activity, Zap, Target } from "lucide-react";

interface EvolutionEvent {
  sequence: number;
  from_date: string;
  to_date: string;
  trigger: string;
  changes: Array<{ dimension: string; delta?: number; direction?: string; from?: string; to?: string }>;
  scores: any;
  insight: string;
  is_significant: boolean;
  rules_cited: string[];
}

interface EvolutionData {
  status: string;
  entity_id: string;
  entity_name?: string;
  snapshot_count: number;
  span_days: number;
  trajectory: { trend: string; message: string; total_geo_delta?: number; stage_from?: string; stage_to?: string };
  current_state: any;
  evolution_events: EvolutionEvent[];
  next_actions: Array<{ priority: number; action: string; why: string }>;
  message?: string;
}

export default function EvolutionTimeline({ entityId }: { entityId: string }) {
  const [data, setData] = useState<EvolutionData | null>(null);
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
      <div className="text-center py-8 text-gray-500">
        <Activity className="w-6 h-6 mx-auto mb-2 animate-pulse" />
        <p className="text-sm">加载生命轨迹...</p>
      </div>
    );
  }

  if (!data) return null;

  const isNewborn = data.status === "newborn";

  return (
    <div className="mt-8 border border-gray-800 rounded-xl bg-gray-900/50 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="w-5 h-5 text-emerald-400" />
          <div>
            <h2 className="font-semibold text-white">
              {isNewborn ? "GEO 生命起点" : "宇宙生命轨迹"}
            </h2>
            <p className="text-xs text-gray-500">
              {isNewborn
                ? "刚刚进入 Universe——每一次变化都将被记录"
                : `${data.snapshot_count} 个快照 · 跨越 ${data.span_days} 天`}
            </p>
          </div>
        </div>
        {!isNewborn && (
          <div className="flex items-center gap-2">
            {data.trajectory.trend === "strong_rising" && (
              <span className="flex items-center gap-1 text-xs bg-emerald-900/50 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/30">
                <TrendingUp className="w-3 h-3" /> 强势上升
              </span>
            )}
            {data.trajectory.trend === "rising" && (
              <span className="flex items-center gap-1 text-xs bg-blue-900/50 text-blue-400 px-3 py-1 rounded-full border border-blue-500/30">
                <TrendingUp className="w-3 h-3" /> 稳步成长
              </span>
            )}
            {data.trajectory.trend === "stable" && (
              <span className="flex items-center gap-1 text-xs bg-gray-800 text-gray-400 px-3 py-1 rounded-full border border-gray-700">
                <Minus className="w-3 h-3" /> 保持稳定
              </span>
            )}
            {data.trajectory.trend === "declining" && (
              <span className="flex items-center gap-1 text-xs bg-red-900/50 text-red-400 px-3 py-1 rounded-full border border-red-500/30">
                <TrendingDown className="w-3 h-3" /> 需要关注
              </span>
            )}
          </div>
        )}
      </div>

      {/* Newborn state */}
      {isNewborn && (
        <div className="px-6 py-10 text-center">
          <Award className="w-10 h-10 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-400 text-sm max-w-md mx-auto">{data.message}</p>
          {data.current_state && (
            <div className="mt-4 inline-flex items-center gap-2 bg-gray-800 px-4 py-2 rounded-lg">
              <Target className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-300">当前阶段：{data.current_state}</span>
            </div>
          )}
        </div>
      )}

      {/* Evolution Timeline */}
      {!isNewborn && data.evolution_events && data.evolution_events.length > 0 && (
        <div className="px-6 py-4">
          <div className="space-y-0">
            {data.evolution_events.map((event, idx) => (
              <div key={idx} className="relative pl-8 pb-6 last:pb-0">
                {/* Timeline line */}
                {idx < data.evolution_events.length - 1 && (
                  <div className="absolute left-[11px] top-8 bottom-0 w-0.5 bg-gray-800" />
                )}
                {/* Timeline dot */}
                <div className={"absolute left-0 top-1 w-5.5 h-5.5 rounded-full border-2 flex items-center justify-center " +
                  (event.is_significant
                    ? "border-emerald-500 bg-emerald-500/20"
                    : "border-gray-700 bg-gray-800")}>
                  {event.is_significant && <Zap className="w-2.5 h-2.5 text-emerald-400" />}
                </div>

                {/* Event card */}
                <div className={"p-4 rounded-lg border " +
                  (event.is_significant
                    ? "bg-emerald-500/5 border-emerald-500/20"
                    : "bg-gray-800/30 border-gray-800")}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-gray-500">{event.from_date} → {event.to_date}</span>
                    {event.is_significant && (
                      <span className="text-xs bg-emerald-900/50 text-emerald-400 px-2 py-0.5 rounded">关键变化</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{event.insight}</p>

                  {/* Score deltas */}
                  <div className="flex gap-3 flex-wrap">
                    {event.scores.geo.delta !== 0 && (
                      <span className={"text-xs px-2 py-1 rounded " + (event.scores.geo.delta > 0 ? "bg-emerald-900/30 text-emerald-400" : "bg-red-900/30 text-red-400")}>
                        GEO {event.scores.geo.delta > 0 ? "+" : ""}{event.scores.geo.delta}
                      </span>
                    )}
                    {event.scores.trust.delta !== 0 && (
                      <span className={"text-xs px-2 py-1 rounded " + (event.scores.trust.delta > 0 ? "bg-blue-900/30 text-blue-400" : "bg-red-900/30 text-red-400")}>
                        Trust {event.scores.trust.delta > 0 ? "+" : ""}{event.scores.trust.delta}
                      </span>
                    )}
                    {event.scores.visibility.delta !== 0 && (
                      <span className={"text-xs px-2 py-1 rounded " + (event.scores.visibility.delta > 0 ? "bg-purple-900/30 text-purple-400" : "bg-red-900/30 text-red-400")}>
                        Vis {event.scores.visibility.delta > 0 ? "+" : ""}{event.scores.visibility.delta}
                      </span>
                    )}
                  </div>

                  {/* Trigger */}
                  {event.trigger && !event.trigger.startsWith("周期性") && (
                    <div className="mt-2 text-xs text-gray-600">
                      触发：{event.trigger}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Actions */}
      {!isNewborn && data.next_actions && data.next_actions.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-800">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-amber-400" />
            下一步行动建议
          </h3>
          <div className="space-y-2">
            {data.next_actions.map((action, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-gray-800/50">
                <span className="w-5 h-5 rounded-full bg-gray-700 flex items-center justify-center text-xs text-gray-400 flex-shrink-0 mt-0.5">
                  {action.priority}
                </span>
                <div>
                  <p className="text-sm text-gray-300">{action.action}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{action.why}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
