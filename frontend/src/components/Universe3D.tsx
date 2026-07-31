"use client";

import { useRef, useMemo, useState, useCallback, useEffect, Suspense } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Text, Html, Line, Sphere as R3FSphere } from "@react-three/drei";
import * as THREE from "three";
import { Compass, Loader2 } from "lucide-react";

// Node type config
const NODE_CONFIG: Record<string, { color: string; size: number; glowColor: string }> = {
  company: { color: "#3b82f6", size: 0.35, glowColor: "#60a5fa" },
  provider: { color: "#22c55e", size: 0.3, glowColor: "#4ade80" },
  industry: { color: "#a855f7", size: 0.45, glowColor: "#c084fc" },
  capability: { color: "#f59e0b", size: 0.25, glowColor: "#fbbf24" },
  person: { color: "#ec4899", size: 0.2, glowColor: "#f472b6" },
  product: { color: "#06b6d4", size: 0.28, glowColor: "#22d3ee" },
};

// Compute 3D positions using spherical distribution
function computePositions(nodes: any[], view: string) {
  const positions: Map<string, THREE.Vector3> = new Map();
  const center = new THREE.Vector3(0, 0, 0);

  // Group nodes by type
  const groups: Record<string, any[]> = {};
  nodes.forEach((n) => {
    const type = n.type || "company";
    if (!groups[type]) groups[type] = [];
    groups[type].push(n);
  });

  const types = Object.keys(groups);
  const baseRadius = 4;
  const radiusStep = 2.5;

  types.forEach((type, ti) => {
    const groupNodes = groups[type];
    const radius = baseRadius + ti * radiusStep;
    const count = groupNodes.length;

    groupNodes.forEach((node, ni) => {
      const phi = Math.acos(-1 + (2 * (ni + 0.5)) / count); // polar angle
      const theta = Math.PI * (1 + Math.sqrt(5)) * ni; // golden angle for even distribution
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);
      positions.set(node.id, new THREE.Vector3(x, y, z));
    });
  });

  return positions;
}

// Glowing node component
function GlowNode({ position, color, glowColor, size, label, type, onClick, isSelected }: {
  position: THREE.Vector3;
  color: string;
  glowColor: string;
  size: number;
  label: string;
  type: string;
  onClick: () => void;
  isSelected: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (glowRef.current) {
      glowRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.1);
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = 0.15 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
    }
    if (meshRef.current && isSelected) {
      meshRef.current.rotation.y += 0.01;
    }
  });

  const targetSize = hovered || isSelected ? size * 1.4 : size;

  return (
    <group position={position}>
      {/* Outer glow */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[targetSize * 2, 32, 32]} />
        <meshBasicMaterial color={glowColor} transparent opacity={0.12} depthWrite={false} />
      </mesh>
      {/* Inner glow ring */}
      <mesh>
        <torusGeometry args={[targetSize * 1.6, 0.04, 16, 48]} />
        <meshBasicMaterial color={glowColor} transparent opacity={0.3} depthWrite={false} />
      </mesh>
      {/* Main sphere */}
      <mesh
        ref={meshRef}
        onClick={(e) => { e.stopPropagation(); onClick(); }}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[targetSize, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 1.5 : 0.8}
          metalness={0.3}
          roughness={0.2}
        />
      </mesh>
      {/* Label */}
      <Html position={[0, targetSize + 0.8, 0]} center className="pointer-events-none">
        <div className={`text-[10px] font-medium whitespace-nowrap px-2 py-0.5 rounded-full ${
          isSelected ? "bg-white text-gray-900 shadow-lg" : "text-white/70"
        }`}
        style={{ textShadow: isSelected ? "none" : "0 0 8px rgba(0,0,0,0.8)" }}>
          {label.length > 8 ? label.slice(0, 8) + "..." : label}
        </div>
      </Html>
      {/* Selection indicator */}
      {isSelected && (
        <mesh>
          <ringGeometry args={[targetSize + 0.3, targetSize + 0.45, 48]} />
          <meshBasicMaterial color="#ffffff" side={THREE.DoubleSide} transparent opacity={0.6} />
        </mesh>
      )}
    </group>
  );
}

// Connection line between nodes
function ConnectionLine({ start, end, color = "#475569" }: { start: THREE.Vector3; end: THREE.Vector3; color?: string }) {
  const points = useMemo(() => {
    const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
    mid.y += start.distanceTo(end) * 0.3; // arc upward
    const curve = new THREE.QuadraticBezierCurve3(start.clone(), mid, end.clone());
    return curve.getPoints(30);
  }, [start, end]);

  return <Line points={points} color={color} lineWidth={0.5} transparent opacity={0.3} />;
}

// Starfield background
function Starfield() {
  const points = useMemo(() => {
    const pts: number[] = [];
    for (let i = 0; i < 600; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 15 + Math.random() * 10;
      pts.push(r * Math.sin(phi) * Math.cos(theta), r * Math.sin(phi) * Math.sin(theta), r * Math.cos(phi));
    }
    return new Float32Array(pts);
  }, []);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[points, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#ffffff" transparent opacity={0.6} sizeAttenuation />
    </points>
  );
}

// Camera controller with animation
function CameraController({ target }: { target: THREE.Vector3 | null }) {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  useEffect(() => {
    if (target && controlsRef.current) {
      const offset = new THREE.Vector3(3, 2, 5);
      const lookAt = target.clone();
      const camPos = lookAt.clone().add(offset);
      controlsRef.current.target.copy(lookAt);
      // Don't animate camera.position here; let user control freely
    }
  }, [target]);

  return <OrbitControls ref={controlsRef} enableDamping dampingFactor={0.08} minDistance={3} maxDistance={20} autoRotate autoRotateSpeed={0.3} />;
}

// Main 3D Scene
function UniverseScene({ graphData, selectedNodeId, onSelectNode, activeView }: {
  graphData: any;
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  activeView: string;
}) {
  const nodePositions = useMemo(() => {
    if (!graphData?.nodes) return new Map();
    return computePositions(graphData.nodes, activeView);
  }, [graphData, activeView]);

  if (!graphData?.nodes) return null;

  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={0.8} color="#ffffff" />
      <pointLight position={[-10, -5, -5]} intensity={0.3} color="#3b82f6" />
      <Starfield />
      <CameraController target={null} />

      {/* Edges */}
      {graphData.edges?.map((edge: any, i: number) => {
        const start = nodePositions.get(edge.source || edge.source_id);
        const end = nodePositions.get(edge.target || edge.target_id);
        if (!start || !end) return null;
        return <ConnectionLine key={i} start={start} end={end} />;
      })}

      {/* Nodes */}
      {graphData.nodes.map((node: any) => {
        const pos = nodePositions.get(node.id);
        if (!pos) return null;
        const config = NODE_CONFIG[node.type || "company"] || NODE_CONFIG.company;
        return (
          <GlowNode
            key={node.id}
            position={pos}
            color={config.color}
            glowColor={config.glowColor}
            size={config.size}
            label={node.label || node.name || node.id}
            type={node.type || "company"}
            isSelected={selectedNodeId === node.id}
            onClick={() => onSelectNode(node.id)}
          />
        );
      })}

      {/* Center reference grid */}
      <gridHelper args={[16, 20, "#1e293b", "#0f172a"]} position={[0, -6, 0]} />
    </>
  );
}

// Props for the wrapper
type Universe3DProps = {
  graphData: any;
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  activeView: string;
};

export default function Universe3D({ graphData, selectedNodeId, onSelectNode, activeView }: Universe3DProps) {
  if (!graphData?.nodes?.length) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-950">
        <div className="text-center">
          <Compass className="w-12 h-12 text-slate-700 mx-auto mb-3 animate-pulse" />
          <p className="text-slate-500">等待宇宙数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-black">
      <Canvas
        camera={{ position: [8, 5, 12], fov: 50, near: 0.1, far: 50 }}
        gl={{ antialias: true, alpha: false }}
        style={{ background: "radial-gradient(ellipse at center, #0a0a1a 0%, #000000 70%)" }}
      >
        <Suspense fallback={null}>
          <UniverseScene
            graphData={graphData}
            selectedNodeId={selectedNodeId}
            onSelectNode={onSelectNode}
            activeView={activeView}
          />
        </Suspense>
      </Canvas>
      {/* Overlay stats */}
      <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur rounded-lg px-3 py-1.5 text-xs text-slate-400 border border-slate-800 z-10">
        <span>{graphData.nodes.length} nodes</span>
        <span className="mx-2 text-slate-700">|</span>
        <span>{graphData.edges?.length || 0} connections</span>
        {selectedNodeId && (
          <>
            <span className="mx-2 text-slate-700">|</span>
            <span className="text-blue-400">1 selected</span>
          </>
        )}
      </div>
    </div>
  );
}
