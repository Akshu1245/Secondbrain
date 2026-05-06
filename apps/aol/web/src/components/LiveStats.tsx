"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Stats = {
  hidden: { hidden: number; total: number; pct: number };
  compute: { local_pct: number; saved_usd: number; saved_ms_avg: number; total: number };
};

/**
 * Live aggregate stats ribbon. Pulls from /api/before-after for surface
 * filtering totals + /api/compute/log for routing totals. Auto-polls every
 * 4 s so demo viewers see numbers move when they click around.
 */
export function LiveStats() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    let active = true;
    async function pull() {
      try {
        const [ba, log] = await Promise.all([api.beforeAfter(), api.computeLog()]);
        // The backend's `/before-after` shape is { before, after, savings: {...} }.
        const ba_any = ba as { before: { feature_count: number }; after: { hidden_count: number; feature_count: number }; savings: { features_hidden_pct: number } };
        if (!active) return;
        setStats({
          hidden: {
            hidden: ba_any.after.hidden_count,
            total: ba_any.before.feature_count,
            pct: ba_any.savings.features_hidden_pct,
          },
          compute: {
            local_pct: log.stats.local_pct,
            saved_usd: log.stats.saved_usd,
            saved_ms_avg: log.stats.saved_ms_avg,
            total: log.stats.total,
          },
        });
      } catch {
        /* leave previous stats; the backend is occasionally cold-starting on fly */
      }
    }
    pull();
    const t = setInterval(pull, 4000);
    return () => {
      active = false;
      clearInterval(t);
    };
  }, []);

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      <Cell
        label="Features hidden"
        value={stats ? `${stats.hidden.hidden} / ${stats.hidden.total}` : "—"}
        sub={stats ? `${stats.hidden.pct}% of the AI menu auto-hidden` : "loading…"}
        accent="emerald"
      />
      <Cell
        label="Ran on phone"
        value={stats ? `${stats.compute.local_pct}%` : "—"}
        sub={stats && stats.compute.total > 0 ? `out of ${stats.compute.total} AI calls` : "tap a feature in tab 3"}
        accent="emerald"
      />
      <Cell
        label="Cloud bill saved"
        value={stats ? `$${stats.compute.saved_usd.toFixed(4)}` : "—"}
        sub="vs running it all in the cloud"
        accent="amber"
      />
      <Cell
        label="Faster by"
        value={stats ? `${Math.round(stats.compute.saved_ms_avg)} ms` : "—"}
        sub="per AI call, on average"
        accent="sky"
      />
    </div>
  );
}

function Cell({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub: string;
  accent: "emerald" | "amber" | "sky";
}) {
  const tone =
    accent === "emerald"
      ? "text-emerald-300"
      : accent === "amber"
      ? "text-amber-300"
      : "text-sky-300";
  return (
    <div className="rounded-xl border border-ink-800 bg-ink-950/80 px-3 py-2.5">
      <div className="text-[10px] uppercase tracking-wider text-gray-500">{label}</div>
      <div className={`mt-0.5 text-xl font-semibold tabular-nums ${tone}`}>{value}</div>
      <div className="mt-0.5 text-[11px] text-gray-500">{sub}</div>
    </div>
  );
}
