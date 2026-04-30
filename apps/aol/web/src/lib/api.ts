"use client";

// In dev, Next.js rewrites `/api/*` to the FastAPI backend (see next.config.mjs).
// In a static export (devinapps.com), we read the absolute backend URL from
// NEXT_PUBLIC_API_BASE_URL injected at build time.
const ENV_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
const BASE = ENV_BASE ? `${ENV_BASE}/api` : "/api";

async function j<T>(r: Response): Promise<T> {
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export type Feature = {
  id: string;
  name: string;
  category: string;
  description?: string;
  default_on?: boolean;
  enabled?: boolean;
  compute_class: "light" | "medium" | "heavy";
  ms_local?: number;
  ms_cloud?: number;
  events?: number;
  share_pct?: number;
};

export type Optimised = {
  visible: Feature[];
  hide_recommended: Feature[];
  user_disabled: Feature[];
  rules: { low_usage_threshold_events_30d: number; priority_categories: string[] };
};

export type ComputeStat = {
  total: number;
  local_pct: number;
  cloud_pct: number;
  saved_usd: number;
  saved_ms_total?: number;
  saved_ms_avg: number;
};

export type ComputeLog = {
  ts: string;
  feature_name: string;
  decision: "local" | "cloud";
  reason: string;
  chosen_ms: number;
  alt_ms: number;
  cost_usd: number;
};

export type Suggestion = {
  id: string;
  name: string;
  category: string;
  reason: string;
  usage_events: number;
};

export const api = {
  features: () => fetch(`${BASE}/features`).then(j<{ features: Feature[]; user_prefs: any }>),
  optimised: () => fetch(`${BASE}/features/optimised`).then(j<Optimised>),
  toggle: (id: string, enabled: boolean) =>
    fetch(`${BASE}/features/${id}/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    }).then(j<{ feature_id: string; enabled: boolean }>),
  prefs: (p: Record<string, unknown>) =>
    fetch(`${BASE}/prefs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    }).then(j),
  context: (time_of_day?: string, activity?: string) => {
    const q = new URLSearchParams();
    if (time_of_day) q.set("time_of_day", time_of_day);
    if (activity) q.set("activity", activity);
    return fetch(`${BASE}/context/now?${q}`).then(
      j<{ context: { time_of_day: string; activity: string }; suggestions: Suggestion[] }>,
    );
  },
  route: (feature_id: string) =>
    fetch(`${BASE}/compute/route`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feature_id }),
    }).then(j<ComputeLog>),
  computeLog: () =>
    fetch(`${BASE}/compute/log`).then(j<{ log: ComputeLog[]; stats: ComputeStat }>),
  feedback: (p: { feature_id: string; rating: string; comment?: string }) =>
    fetch(`${BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    }).then(j),
  feedbackList: () =>
    fetch(`${BASE}/feedback`).then(
      j<{ entries: any[]; improvement_suggestions: any[] }>,
    ),
  beforeAfter: () => fetch(`${BASE}/before-after`).then(j),
  analytics: () => fetch(`${BASE}/analytics`).then(j),
  reset: () => fetch(`${BASE}/admin/reset`, { method: "POST" }).then(j),
};
