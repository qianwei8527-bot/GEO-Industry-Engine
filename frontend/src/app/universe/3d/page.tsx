"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Compass, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { getNodeColor, getNodeGlow, getNodeSize, getNodeLabel, getNodeType } from "@/lib/registryData";

// Seed data inline — no API dependency needed
const SEED_NODES = [
  { id: "ind_geo", type: "industry", label: "GEO", geo_score: null },
  { id: "comp_1", type: "company", label: "AI内容引擎", geo_score: 88 },
  { id: "comp_2", type: "company", label: "智识数据", geo_score: 82 },
  { id: "comp_3", type: "company", label: "企业知识图谱", geo_score: 65 },
  { id: "comp_4", type: "company", label: "结构化SEO", geo_score: 58 },
  { id: "comp_5", type: "company", label: "品牌权威", geo_score: 52 },
  { id: "comp_6", type: "company", label: "AI监测", geo_score: 32 },
  { id: "comp_7", type: "company", label: "内容优化", geo_score: 28 },
  { id: "comp_8", type: "company", label: "可信验证", geo_score: 25 },
  { id: "prov_1", type: "provider", label: "ContentForge", geo_score: null },
  { id: "prov_2", type: "provider", label: "DataStruct", geo_score: null },
  { id: "prov_3", type: "provider", label: "AI-Optimize", geo_score: null },
  { id: "prov_4", type: "provider", label: "TrustEngine", geo_score: null },
  { id: "prov_5", type: "provider", label: "MonitorPro", geo_score: null },
  { id: "prov_6", type: "provider", label: "BrandPulse", geo_score: null },
  { id: "cap_1", type: "capability", label: "实体构建", geo_score: null },
  { id: "cap_2", type: "capability", label: "证据管理", geo_score: null },
  { id: "cap_3", type: "capability", label: "内容工程", geo_score: null },
  { id: "cap_4", type: "capability", label: "AI可见度", geo_score: null },
  { id: "cap_5", type: "capability", label: "权威建设", geo_score: null },
  { id: "cap_6", type: "capability", label: "监测分析", geo_score: null },
];

const SEED_EDGES = [
  ...SEED_NODES.filter(n => n.type === "company").map(n => ({ source: n.id, target: "ind_geo" })),
  { source: "comp_1", target: "prov_1" }, { source: "comp_1", target: "prov_3" },
  { source: "comp_2", target: "prov_2" }, { source: "comp_2", target: "prov_4" },
  { source: "comp_3", target: "prov_1" }, { source: "comp_3", target: "prov_5" },
  { source: "comp_4", target: "prov_2" }, { source: "comp_4", target: "prov_3" },
  { source: "comp_5", target: "prov_6" }, { source: "comp_5", target: "prov_4" },
  { source: "comp_6", target: "prov_5" }, { source: "comp_7", target: "prov_1" },
  { source: "comp_8", target: "prov_4" },
  { source: "prov_1", target: "prov_3" }, { source: "prov_2", target: "prov_5" },
  { source: "cap_1", target: "prov_2" }, { source: "cap_2", target: "prov_4" },
  { source: "cap_3", target: "prov_1" }, { source: "cap_4", target: "prov_3" },
  { source: "cap_5", target: "prov_6" }, { source: "cap_6", target: "prov_5" },
];

// Colors, sizes, labels are now loaded from UniverseRegistry via useRegistry() hook

// Compute 3D positions (spherical layers)
function computePositions(nodes: any[]) {
  const groups: Record<string, any[]> = {};
  nodes.forEach(n => { const t = n.type; if (!groups[t]) groups[t] = []; groups[t].push(n); });
  const positions: Record<string, [number, number, number]> = {};
  const baseR = 180, stepR = 150;
  Object.entries(groups).forEach(([type, gns], ti) => {
    const r = baseR + ti * stepR;
    gns.forEach((node, ni) => {
      const phi = Math.acos(-1 + 2 * (ni + 0.5) / gns.length);
      const theta = Math.PI * (1 + Math.sqrt(5)) * ni;
      positions[node.id] = [
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi),
      ];
    });
  });
  return positions;
}

function project(x: number, y: number, z: number, cx: number, cy: number, focal: number, camZ: number) {
  const dz = camZ - z;
  const s = focal / Math.max(dz, 1);
  return { sx: cx + x * s, sy: cy - y * s, scale: s };
}

export default function Universe3DPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [rotX, setRotX] = useState(0.3);
  const [rotY, setRotY] = useState(0);
  const dragRef = useRef({ active: false, lastX: 0, lastY: 0, rotX: 0.3, rotY: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const resize = () => {
      canvas.width = container.clientWidth * (window.devicePixelRatio || 1);
      canvas.height = container.clientHeight * (window.devicePixelRatio || 1);
      canvas.style.width = container.clientWidth + "px";
      canvas.style.height = container.clientHeight + "px";
    };
    resize();
    window.addEventListener("resize", resize);

    const ctx = canvas.getContext("2d")!;
    const positions = computePositions(SEED_NODES);

    let animId: number;
    function draw() {
      if (!canvas) return;
      animId = requestAnimationFrame(draw);
      const w = canvas.width, h = canvas.height;
      const dpr = window.devicePixelRatio || 1;
      const cx = w / 2, cy = h / 2;
      const focal = 500;
      const camZ = 800;

      // Clear
      ctx.fillStyle = "#050515";
      ctx.fillRect(0, 0, w, h);

      // Stars
      ctx.fillStyle = "white";
      for (let i = 0; i < 400; i++) {
        const sx = ((i * 337 + 17) % 1000) * (w / 1000);
        const sy = ((i * 173 + 50) % 800) * (h / 800);
        const br = 0.3 + (i % 100) / 100 * 0.7;
        ctx.globalAlpha = br;
        ctx.beginPath();
        ctx.arc(sx, sy, (0.4 + (i % 3) * 0.5) * dpr, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

      // Rotation
      const cosX = Math.cos(rotX), sinX = Math.sin(rotX);
      const cosY = Math.cos(rotY), sinY = Math.sin(rotY);

      // Project all nodes
      const projNodes: any[] = [];
      for (const node of SEED_NODES) {
        let [x, y, z] = positions[node.id] || [0, 0, 0];
        // Rotate around Y
        const rx = x * cosY - z * sinY;
        const rz = x * sinY + z * cosY;
        // Rotate around X
        const ry = y * cosX - rz * sinX;
        const rz2 = y * sinX + rz * cosX;
        const { sx, sy, scale } = project(rx, ry, rz2, cx, cy, focal, camZ);
        projNodes.push({ ...node, sx, sy, scale, z: rz2 });
      }
      projNodes.sort((a, b) => a.z - b.z);

      // Draw edges
      for (const edge of SEED_EDGES) {
        const sn = projNodes.find(n => n.id === edge.source);
        const tn = projNodes.find(n => n.id === edge.target);
        if (!sn || !tn) continue;
        const mx = (sn.sx + tn.sx) / 2;
        const my = (sn.sy + tn.sy) / 2 - Math.abs(sn.sx - tn.sx) * 0.1;
        ctx.strokeStyle = "#334466";
        ctx.lineWidth = 0.6 * dpr;
        ctx.globalAlpha = 0.25;
        ctx.beginPath();
        ctx.moveTo(sn.sx, sn.sy);
        ctx.quadraticCurveTo(mx, my, tn.sx, tn.sy);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }

      // Draw nodes
      for (const node of projNodes) {
        const color = getNodeColor(node.type, "#3b82f6");
        const glow = getNodeGlow(node.type, "#60a5fa");
        const baseSize = getNodeSize(node.type, 14);
        const size = baseSize * Math.max(node.scale, 0.3) * dpr;
        const isSel = selectedNode?.id === node.id;

        // Glow layers
        for (let g = 3; g >= 1; g--) {
          const gr = size * (1 + g * 0.6);
          const grad = ctx.createRadialGradient(node.sx, node.sy, size * 0.3, node.sx, node.sy, gr);
          grad.addColorStop(0, glow + "40");
          grad.addColorStop(0.5, glow + "10");
          grad.addColorStop(1, "transparent");
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.arc(node.sx, node.sy, gr, 0, Math.PI * 2);
          ctx.fill();
        }

        // Selection ring
        if (isSel) {
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2 * dpr;
          ctx.globalAlpha = 0.8;
          ctx.beginPath();
          ctx.arc(node.sx, node.sy, size * 1.5, 0, Math.PI * 2);
          ctx.stroke();
          ctx.globalAlpha = 1;
        }

        // Ring
        ctx.strokeStyle = glow;
        ctx.lineWidth = 1.2 * dpr;
        ctx.globalAlpha = 0.5;
        ctx.beginPath();
        ctx.arc(node.sx, node.sy, size * 1.15, 0, Math.PI * 2);
        ctx.stroke();
        ctx.globalAlpha = 1;

        // Main sphere
        const sgrad = ctx.createRadialGradient(node.sx - size * 0.25, node.sy - size * 0.3, size * 0.1, node.sx, node.sy, size);
        sgrad.addColorStop(0, "#ffffff");
        sgrad.addColorStop(0.2, color);
        sgrad.addColorStop(0.7, color);
        sgrad.addColorStop(1, "#000000");
        ctx.fillStyle = sgrad;
        ctx.beginPath();
        ctx.arc(node.sx, node.sy, size, 0, Math.PI * 2);
        ctx.fill();

        // Label
        ctx.fillStyle = "white";
        ctx.globalAlpha = 0.85;
        ctx.font = `${Math.max(9, baseSize * 0.55) * dpr}px sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText(node.label, node.sx, node.sy + size + 14 * dpr);
        ctx.globalAlpha = 1;

        // Score
        if (node.geo_score !== null && node.geo_score !== undefined) {
          const sc = node.geo_score >= 70 ? "#4ade80" : node.geo_score >= 40 ? "#fbbf24" : "#f87171";
          ctx.fillStyle = sc;
          ctx.font = `bold ${10 * dpr}px sans-serif`;
          ctx.fillText(String(node.geo_score), node.sx, node.sy + size + 26 * dpr);
        }
      }

      // Legend
      const legendX = w - 130 * dpr;
      const legendY = h - 120 * dpr;
      ctx.fillStyle = "#0f172a";
      ctx.globalAlpha = 0.85;
      ctx.beginPath();
      ctx.roundRect(legendX - 10 * dpr, legendY - 10 * dpr, 125 * dpr, 110 * dpr, 8 * dpr);
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.fillStyle = "#64748b";
      ctx.font = `bold ${10 * dpr}px sans-serif`;
      ctx.textAlign = "center";
      ctx.fillText("LEGEND", legendX + 52 * dpr, legendY + 10 * dpr);

      const legendItems = [
        { type: "industry", label: "行业" },
        { type: "company", label: "企业" },
        { type: "provider", label: "服务商" },
        { type: "capability", label: "能力" },
      ];
      legendItems.forEach((item, i) => {
        const y = legendY + 32 * dpr + i * 20 * dpr;
        ctx.fillStyle = getNodeColor(item.type, "#3b82f6");
        ctx.beginPath();
        ctx.arc(legendX + 15 * dpr, y, 6 * dpr, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#cbd5e1";
        ctx.textAlign = "left";
        ctx.font = `${11 * dpr}px sans-serif`;
        ctx.fillText(item.label, legendX + 28 * dpr, y + 4 * dpr);
      });
    }

    // Click handler
    const onClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = (e.clientX - rect.left) * (window.devicePixelRatio || 1);
      const my = (e.clientY - rect.top) * (window.devicePixelRatio || 1);

      const dpr = window.devicePixelRatio || 1;
      const cx = canvas.width / 2, cy = canvas.height / 2, focal = 500, camZ = 800;
      const cosX = Math.cos(rotX), sinX = Math.sin(rotX);
      const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      const positions = computePositions(SEED_NODES);

      let closest: any = null;
      let closestDist = 30 * dpr;
      for (const node of SEED_NODES) {
        let [x, y, z] = positions[node.id] || [0, 0, 0];
        const rx = x * cosY - z * sinY;
        const rz = x * sinY + z * cosY;
        const ry = y * cosX - rz * sinX;
        const rz2 = y * sinX + rz * cosX;
        const { sx, sy, scale } = project(rx, ry, rz2, cx, cy, focal, camZ);
        const baseSize = (getNodeSize(node.type, 14)) * Math.max(scale, 0.3) * dpr;
        const dist = Math.hypot(mx - sx, my - sy);
        if (dist < Math.max(baseSize * 1.5, closestDist)) {
          closest = node;
          closestDist = dist;
        }
      }
      setSelectedNode(closest);
    };

    // Drag handlers
    const onMouseDown = (e: MouseEvent) => {
      dragRef.current = { active: true, lastX: e.clientX, lastY: e.clientY, rotX, rotY };
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!dragRef.current.active) return;
      const dx = (e.clientX - dragRef.current.lastX) * 0.005;
      const dy = (e.clientY - dragRef.current.lastY) * 0.005;
      setRotX(dragRef.current.rotX - dy);
      setRotY(dragRef.current.rotY + dx);
    };
    const onMouseUp = () => { dragRef.current.active = false; };

    canvas.addEventListener("click", onClick);
    canvas.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    draw();

    return () => {
      cancelAnimationFrame(animId);
      canvas.removeEventListener("click", onClick);
      canvas.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("resize", resize);
    };
  }, [rotX, rotY, selectedNode]);

  return (
    <div className="h-screen bg-[#050515] flex flex-col relative overflow-hidden">
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between px-5 py-2.5 bg-black/60 backdrop-blur border-b border-slate-800/50">
        <div className="flex items-center gap-4">
          <Link href="/universe/navigation" className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /><span className="text-xs">2D</span>
          </Link>
          <div className="w-px h-4 bg-slate-700/50" />
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-blue-400" /><span className="text-white font-bold text-sm">GEO Universe 3D</span>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span>{SEED_NODES.length} nodes</span>
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
        </div>
      </div>

      {/* Canvas */}
      <div ref={containerRef} className="flex-1 cursor-grab active:cursor-grabbing">
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>

      {/* Selected node panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 md:left-auto md:right-4 md:w-60 bg-slate-900/90 backdrop-blur border border-slate-700/80 rounded-xl p-4 z-20 shadow-2xl">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-white font-bold text-sm">{selectedNode.label}</h3>
              <span className="text-[10px] text-slate-500 capitalize">{selectedNode.type}</span>
            </div>
            <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-slate-300">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          {selectedNode.geo_score !== null && selectedNode.geo_score !== undefined && (
            <div className="flex justify-between py-1 border-t border-slate-800/50 text-xs">
              <span className="text-slate-500">GEO Score</span>
              <span className="text-blue-400 font-bold">{selectedNode.geo_score}</span>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-16 right-3 z-20 bg-black/40 backdrop-blur rounded-lg p-2.5 border border-slate-800/50">
        <p className="text-[9px] text-slate-500 uppercase mb-2 tracking-wider">Legend</p>
        <div className="space-y-1">
          {[{t:"industry",l:"行业"},{t:"company",l:"企业"},{t:"provider",l:"服务商"},{t:"capability",l:"能力"}].map(({t,l}) => (
            <div key={t} className="flex items-center gap-2 text-[10px]">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: getNodeColor(t, "#3b82f6"), boxShadow: `0 0 6px ${getNodeGlow(t, "#60a5fa")}` }} />
              <span className="text-slate-400">{l}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom hint */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <p className="text-[10px] text-slate-600 bg-black/30 px-3 py-1 rounded-full">
          Drag to rotate · Click node to select
        </p>
      </div>
    </div>
  );
}
