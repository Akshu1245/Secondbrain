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

export type MemorySuggestion = {
  feature_id: string;
  name: string;
  action: "auto_hide_durable";
  confidence: "high" | "medium";
  evidence: string[];
  window_days: number;
  signals: {
    disable_count: number;
    negative_ratings: number;
    positive_ratings: number;
  };
};

export type MemoryRecall = {
  feature_id: string;
  window_days: number;
  disable_count: number;
  rating_counts: Record<string, number>;
  negative_ratings: number;
  positive_ratings: number;
  context_hide_count: number;
  disables: Array<{ ts: string; feature_id: string; enabled: boolean }>;
  ratings: Array<{ ts: string; feature_id: string; rating: string }>;
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
      j<{
        entries: any[];
        improvement_suggestions: any[];
        memory_suggestions: MemorySuggestion[];
      }>,
    ),
  memoryRecall: (feature_id: string, days = 90) => {
    const q = new URLSearchParams({ feature_id, days: String(days) });
    return fetch(`${BASE}/memory/recall?${q}`).then(j<MemoryRecall>);
  },
  memorySuggestions: (days = 90) =>
    fetch(`${BASE}/memory/suggestions?days=${days}`).then(
      j<{ window_days: number; suggestions: MemorySuggestion[] }>,
    ),
  beforeAfter: () => fetch(`${BASE}/before-after`).then(j),
  analytics: () => fetch(`${BASE}/analytics`).then(j),
  reset: () => fetch(`${BASE}/admin/reset`, { method: "POST" }).then(j),
  learnedStatus: () => fetch(`${BASE}/learned/status`).then(j<LearnedStatus>),
  learnedTrain: () =>
    fetch(`${BASE}/learned/train`, { method: "POST" }).then(j<LearnedTrainResult>),
  learnedPredict: (feature_id: string) =>
    fetch(`${BASE}/learned/predict?feature_id=${encodeURIComponent(feature_id)}`).then(
      j<LearnedPrediction>,
    ),
  learnedRank: (limit = 12) =>
    fetch(`${BASE}/learned/rank?limit=${limit}`).then(j<{ ranked: LearnedRanked[] }>),
};

export type LearnedFactor = {
  name: string;
  value: number;
  weight: number;
  contribution: number;
};

export type LearnedPrediction = {
  feature_id: string;
  prob_engaged: number;
  model: string;
  top_factors: LearnedFactor[];
};

export type LearnedRanked = LearnedPrediction & {
  name: string;
  category: string;
};

export type LearnedMetrics = {
  train_accuracy: number;
  test_accuracy: number;
  train_log_loss: number;
  test_log_loss: number;
  majority_baseline: number;
  calibration: { mean_pred: number; mean_actual: number; abs_gap: number };
};

export type LearnedStatus = {
  trained: boolean;
  n_rows?: number | null;
  n_rows_train?: number | null;
  n_rows_test?: number | null;
  version?: number | null;
  metrics?: LearnedMetrics | null;
  feature_names?: string[] | null;
  weights?: number[] | null;
};

export type LearnedTrainResult = LearnedStatus & {
  beats_baseline?: boolean;
  rows_train?: number;
  rows_test?: number;
  train_accuracy?: number;
  test_accuracy?: number;
  train_log_loss?: number;
  test_log_loss?: number;
  majority_baseline?: number;
  calibration?: LearnedMetrics["calibration"];
  loss_curve_first_last?: [number | null, number | null];
};
