"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GraphResponse } from "@/lib/api";

/**
 * Lightweight force-directed graph rendered to canvas.
 * No external dependencies — keeps the JS bundle small.
 */
export default function GraphView({ data }: { data: GraphResponse }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoverLabel, setHoverLabel] = useState<string | null>(null);

  const sim = useMemo(() => buildSimulation(data), [data]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      const { clientWidth, clientHeight } = canvas;
      canvas.width = clientWidth * dpr;
      canvas.height = clientHeight * dpr;
    };
    resize();
    window.addEventListener("resize", resize);

    const ctx = canvas.getContext("2d")!;
    let raf = 0;

    const draw = () => {
      stepSimulation(sim);
      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
      ctx.translate(canvas.clientWidth / 2, canvas.clientHeight / 2);

      // edges
      ctx.lineWidth = 0.6;
      ctx.strokeStyle = "rgba(120,120,140,0.35)";
      for (const e of sim.edges) {
        const a = sim.nodes[e.s];
        const b = sim.nodes[e.t];
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }

      // nodes
      for (const n of sim.nodes) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = NODE_COLOR[n.type];
        ctx.fill();
        if (n.r > 5) {
          ctx.fillStyle = "rgba(0,0,0,0.55)";
          ctx.font = "10px ui-sans-serif, system-ui";
          ctx.fillText(n.label.slice(0, 24), n.x + n.r + 3, n.y + 3);
        }
      }
      ctx.restore();
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);

    const onMove = (ev: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = ev.clientX - rect.left - rect.width / 2;
      const y = ev.clientY - rect.top - rect.height / 2;
      const hit = sim.nodes.find((n) => (n.x - x) ** 2 + (n.y - y) ** 2 < (n.r + 4) ** 2);
      setHoverLabel(hit ? `${hit.type}: ${hit.label}` : null);
    };
    canvas.addEventListener("mousemove", onMove);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("mousemove", onMove);
    };
  }, [sim]);

  return (
    <div className="relative h-[70vh] overflow-hidden rounded-xl border border-border bg-card">
      <canvas ref={canvasRef} className="h-full w-full" />
      {hoverLabel && (
        <div className="pointer-events-none absolute left-3 top-3 rounded-md bg-background/80 px-2 py-1 text-xs backdrop-blur">
          {hoverLabel}
        </div>
      )}
      <div className="pointer-events-none absolute bottom-3 left-3 flex gap-3 text-xs text-muted">
        <Legend color={NODE_COLOR.item} label="item" />
        <Legend color={NODE_COLOR.entity} label="entity" />
        <Legend color={NODE_COLOR.tag} label="tag" />
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span className="size-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}

const NODE_COLOR: Record<string, string> = {
  item: "#6366f1",
  entity: "#10b981",
  tag: "#f59e0b",
};

interface SimNode {
  id: string;
  label: string;
  type: "item" | "entity" | "tag";
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
}
interface SimEdge {
  s: number;
  t: number;
}
interface Sim {
  nodes: SimNode[];
  edges: SimEdge[];
}

function buildSimulation(data: GraphResponse): Sim {
  const idx = new Map<string, number>();
  const nodes: SimNode[] = data.nodes.map((n, i) => {
    idx.set(n.id, i);
    return {
      id: n.id,
      label: n.label,
      type: n.type,
      x: Math.cos((i / data.nodes.length) * Math.PI * 2) * 140,
      y: Math.sin((i / data.nodes.length) * Math.PI * 2) * 140,
      vx: 0,
      vy: 0,
      r: n.type === "item" ? 5 : n.type === "entity" ? 4 : 3,
    };
  });
  const edges: SimEdge[] = [];
  for (const e of data.edges) {
    const s = idx.get(e.source);
    const t = idx.get(e.target);
    if (s !== undefined && t !== undefined) edges.push({ s, t });
  }
  return { nodes, edges };
}

function stepSimulation(sim: Sim) {
  const N = sim.nodes.length;
  // Repulsion (n^2, fine up to ~500 nodes)
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      const a = sim.nodes[i];
      const b = sim.nodes[j];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d2 = dx * dx + dy * dy + 1;
      const f = 600 / d2;
      const fx = (dx / Math.sqrt(d2)) * f;
      const fy = (dy / Math.sqrt(d2)) * f;
      a.vx -= fx;
      a.vy -= fy;
      b.vx += fx;
      b.vy += fy;
    }
  }
  // Spring-like edges
  for (const e of sim.edges) {
    const a = sim.nodes[e.s];
    const b = sim.nodes[e.t];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
    const target = 60;
    const f = (d - target) * 0.02;
    const fx = (dx / d) * f;
    const fy = (dy / d) * f;
    a.vx += fx;
    a.vy += fy;
    b.vx -= fx;
    b.vy -= fy;
  }
  // Centering + damping + integrate
  for (const n of sim.nodes) {
    n.vx -= n.x * 0.005;
    n.vy -= n.y * 0.005;
    n.vx *= 0.85;
    n.vy *= 0.85;
    n.x += n.vx;
    n.y += n.vy;
  }
}
