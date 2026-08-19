"use client";

import { useState } from "react";
import {
  List,
  MapPin,
  RefreshCw,
  RotateCcw,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { MAP_NODE_DEFS, MAP_VIEW_DEFS } from "@/lib/realm-owner/config";
import { getIcon } from "./icon-map";
import ModuleState from "./module-state";
import type { ModuleStateVariant } from "./module-state";
import type { MapMode, RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

const NODE_X = [10, 26, 42, 58, 74, 90];
const NODE_Y = 42;
const OWNER_X = 50;
const OWNER_Y = 84;

interface IndustryEvolutionCanvasProps {
  map: RealmOwnerHomeViewModel["map"];
  mode: MapMode;
  onModeChange: (mode: MapMode) => void;
  onOpenNode: (nodeId: string) => void;
  onOpenPositionConfig: () => void;
  onOpenMapConfig: () => void;
  state?: ModuleStateVariant | "ready";
  stateTitle?: string;
  stateDescription?: string;
  onRetry?: () => void;
}

export default function IndustryEvolutionCanvas({
  map,
  mode,
  onModeChange,
  onOpenNode,
  onOpenPositionConfig,
  onOpenMapConfig,
  state = "ready",
  stateTitle,
  stateDescription,
  onRetry,
}: IndustryEvolutionCanvasProps) {
  const [zoom, setZoom] = useState(1);
  const [showList, setShowList] = useState(false);
  const definitions = MAP_NODE_DEFS[mode];

  const ownerLineTarget = map.ownerPosition.nodeIds[0] || definitions[0].id;
  const ownerTargetIndex = Math.max(
    0,
    definitions.findIndex((node) => node.id === ownerLineTarget),
  );
  const ownerTargetX = NODE_X[ownerTargetIndex] || NODE_X[0];

  return (
    <section
      className="realm-card flex min-h-[420px] flex-col overflow-hidden"
      aria-labelledby="industry-map-title"
    >
      <header className="flex flex-wrap items-center gap-2 border-b border-slate-200 px-3.5 py-3">
        <div className="min-w-0">
          <h2 id="industry-map-title" className="text-sm font-semibold text-slate-800">
            行业演化与资源地图
          </h2>
          <p className="mt-0.5 truncate text-[11px] text-slate-500">{map.dataSourceLabel}</p>
        </div>

        <div className="ml-auto flex flex-wrap items-center gap-1.5">
          <div role="tablist" aria-label="地图视图" className="flex rounded-lg border border-slate-200 bg-slate-50 p-0.5">
            {MAP_VIEW_DEFS.map((view) => (
              <button
                key={view.id}
                role="tab"
                aria-selected={mode === view.id}
                type="button"
                onClick={() => onModeChange(view.id)}
                title={view.hint}
                className={`rounded-md px-2.5 py-1.5 text-xs font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-teal-600 ${
                  mode === view.id ? "bg-white text-teal-800 shadow-sm ring-1 ring-slate-200" : "text-slate-500 hover:text-slate-700"
                }`}
              >
                {view.label}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={onOpenMapConfig}
            className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 text-xs font-medium text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
          >
            <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
            拉取配置
          </button>
        </div>
      </header>

      {state !== "ready" ? (
        <div className="p-4">
          <ModuleState
            variant={state}
            title={stateTitle || (state === "error" ? "地图数据不可用" : "地图暂不可用")}
            description={stateDescription || "地图模块已隔离，其余模块不受影响。"}
            actionLabel={state === "error" ? "重试" : undefined}
            onAction={onRetry}
          />
        </div>
      ) : (
        <>
          <div className="relative flex-1 overflow-auto bg-[linear-gradient(to_bottom,#f8faf9,#eef4f2)] p-3">
            <div
              className="relative min-h-[360px] min-w-[720px]"
              style={{ transform: `scale(${zoom})`, transformOrigin: "50% 0" }}
            >
              <svg
                className="pointer-events-none absolute inset-0 h-full w-full"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                {map.edges.map((edge) => {
                  const sourceIndex = definitions.findIndex((node) => node.id === edge.source);
                  const targetIndex = definitions.findIndex((node) => node.id === edge.target);
                  const x1 = NODE_X[sourceIndex] ?? NODE_X[0];
                  const x2 = NODE_X[targetIndex] ?? NODE_X[0];
                  return (
                    <line
                      key={edge.id}
                      x1={x1}
                      y1={NODE_Y}
                      x2={x2}
                      y2={NODE_Y}
                      stroke="#94a3b8"
                      strokeWidth="0.35"
                    />
                  );
                })}
                <line
                  x1={ownerTargetX}
                  y1={NODE_Y}
                  x2={OWNER_X}
                  y2={OWNER_Y}
                  stroke="#0b63e6"
                  strokeWidth="0.3"
                  strokeDasharray="1.4 1"
                />
              </svg>

              {definitions.map((node, index) => {
                const Icon = getIcon(node.iconKey);
                const mapNode = map.nodes[index];
                return (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => onOpenNode(node.id)}
                    title={node.description}
                    aria-label={`${node.label}：${node.description}`}
                    className="group absolute -translate-x-1/2 -translate-y-1/2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
                    style={{ left: `${NODE_X[index]}%`, top: `${NODE_Y}%` }}
                  >
                    <span
                      className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full border-2 border-dotted border-slate-400 bg-white text-slate-600 shadow-sm transition group-hover:border-teal-500 group-hover:text-teal-700 sm:h-[72px] sm:w-[72px]`}
                    >
                      <Icon className="h-6 w-6 sm:h-7 sm:w-7" aria-hidden="true" />
                    </span>
                    <span className="mt-1.5 block w-20 text-center text-[11px] font-medium leading-4 text-slate-700">
                      {mapNode?.label || node.label}
                    </span>
                  </button>
                );
              })}

              <button
                type="button"
                onClick={onOpenPositionConfig}
                aria-label="我的位置：待确认，打开配置"
                className="absolute -translate-x-1/2 -translate-y-1/2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                style={{ left: `${OWNER_X}%`, top: `${OWNER_Y}%` }}
              >
                <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border-2 border-dashed border-blue-500 bg-blue-50 text-blue-700 sm:h-[72px] sm:w-[72px]">
                  <MapPin className="h-6 w-6 sm:h-7 sm:w-7" aria-hidden="true" />
                </span>
                <span className="mt-1.5 block w-24 text-center text-[11px] font-semibold leading-4 text-blue-700">
                  我的位置：待确认
                </span>
              </button>
            </div>
          </div>

          <footer className="flex flex-wrap items-center gap-2 border-t border-slate-200 px-3.5 py-2.5">
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setZoom((value) => Math.min(1.5, value + 0.15))}
                aria-label="放大地图"
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
              >
                <ZoomIn className="h-4 w-4" aria-hidden="true" />
              </button>
              <button
                type="button"
                onClick={() => setZoom((value) => Math.max(0.6, value - 0.15))}
                aria-label="缩小地图"
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
              >
                <ZoomOut className="h-4 w-4" aria-hidden="true" />
              </button>
              <button
                type="button"
                onClick={() => setZoom(1)}
                aria-label="重置地图缩放"
                className="inline-flex h-8 items-center gap-1 rounded-lg border border-slate-300 bg-white px-2 text-xs font-medium text-slate-600 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
              >
                <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
                重置
              </button>
            </div>

            <button
              type="button"
              onClick={() => setShowList((value) => !value)}
              aria-expanded={showList}
              className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
            >
              <List className="h-3.5 w-3.5" aria-hidden="true" />
              节点列表
            </button>

            <span className="ml-auto text-[11px] text-slate-500">
              当前为预演模板，不写入真实 World
            </span>
          </footer>

          {showList && (
            <div className="border-t border-slate-200 px-3.5 py-3">
              <ul className="grid grid-cols-2 gap-1.5 sm:grid-cols-3">
                {definitions.map((node, index) => (
                  <li key={node.id}>
                    <button
                      type="button"
                      onClick={() => onOpenNode(node.id)}
                      className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-left text-xs text-slate-700 hover:border-teal-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
                    >
                      <span className="block font-medium">{index + 1}. {node.label}</span>
                      <span className="mt-0.5 block text-[11px] text-slate-500">{node.description}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </section>
  );
}