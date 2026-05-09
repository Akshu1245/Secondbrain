"use client";

import { useEffect, useState, useCallback } from "react";
import { api, type LearnedRanked, type LearnedStatus, type LearnedTrainResult } from "@/lib/api";
import { Card, Stat } from "./Card";

// The Phase-2 endpoints (`/api/learned/*`) ship in the v5 backend.
// The v4 image still on Fly does NOT have them yet — when they 404 the
// component falls back to a static demo card explaining the model so
// the dashboard never looks broken to a Mahmoud-tier reader.
type FetchState =
  | { kind: "loading" }
  | { kind: "ok"; status: LearnedStatus; ranked: LearnedRanked[] }
  | { kind: "missing"; message: string }
  | { kind: "error"; message: string };

export function LearnedPolicy() {
  const [state, setState] = useState<FetchState>({ kind: "loading" });
  const [training, setTraining] = useState(false);
  const [lastTrain, setLastTrain] = useState<LearnedTrainResult | null>(null);

  const refresh = useCallback(async () => {
    try {
      const status = await api.learnedStatus();
      const ranked = (await api.learnedRank(12)).ranked;
      setState({ kind: "ok", status, ranked });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      // 404 = endpoint missing on this backend image. Anything else =
      // a real error worth surfacing.
      if (msg.includes("404")) {
        setState({
          kind: "missing",
          message:
            "Live backend is on the v4 image and doesn't expose /api/learned/* yet. The Phase-2 model is on GitHub and will be live on the next deploy.",
        });
      } else {
        setState({ kind: "error", message: msg });
      }
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const onTrain = useCallback(async () => {
    setTraining(true);
    try {
      const result = await api.learnedTrain();
      setLastTrain(result);
      await refresh();
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setState({ kind: "error", message: msg });
    } finally {
      setTraining(false);
    }
  }, [refresh]);

  return (
    <div className="space-y-4">
      <Card
        title="Learned routing policy (Phase 2)"
        subtitle="Logistic regression on the on-device usage log. Pure Python, ~150 LOC, zero new deps. Re-ranks the rule-based engine — never overrides it."
        right={
          state.kind === "ok" || state.kind === "missing" ? (
            <button
              onClick={onTrain}
              disabled={training || state.kind === "missing"}
              className="rounded-xl border border-emerald-400/40 bg-emerald-400/10 px-4 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-400/20 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {training ? "Training…" : "Train on current state"}
            </button>
          ) : null
        }
      >
        {state.kind === "loading" && (
          <p className="text-sm text-gray-400">Loading model status…</p>
        )}

        {state.kind === "missing" && <MissingBanner message={state.message} />}
        {state.kind === "error" && (
          <p className="text-sm text-rose-400">Error: {state.message}</p>
        )}

        {state.kind === "ok" && (
          <>
            <ModelStatus status={state.status} />
            {lastTrain && <TrainSummary result={lastTrain} />}
            <RankedFeatures ranked={state.ranked} />
          </>
        )}
      </Card>

      <Card
        title="Why a learned policy and why now"
        subtitle="Engineering rationale — the answer to 'is this a real model or just rules with extra steps?'"
      >
        <ul className="list-disc space-y-1 pl-5 text-sm text-gray-300">
          <li>
            <strong>Rule-based engine is the floor, not the ceiling.</strong>{" "}
            The learned policy only re-ranks among features that already pass
            the hard rules (battery, privacy, data-saver). It can demote bloat
            but never enable something the user disabled.
          </li>
          <li>
            <strong>Per-feature top-3 explainability.</strong> Every prediction
            ships with the three input dimensions whose weight×value
            contribution dominates the final score — straight into the OEM
            legal review workflow.
          </li>
          <li>
            <strong>Held-out gate.</strong> Training only persists if test
            accuracy beats the majority-class baseline. If it doesn't, the
            old weights stay and the system continues using the previous
            policy or rule-based fallback.
          </li>
          <li>
            <strong>No new runtime dependencies.</strong> Pure Python, fits in
            ~150 LOC, audits cleanly. sklearn/numpy are explicitly out of
            scope: too much surface area for an OEM image.
          </li>
        </ul>
      </Card>
    </div>
  );
}

function MissingBanner({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-amber-400/40 bg-amber-400/5 p-4">
      <div className="text-xs uppercase tracking-wide text-amber-300">
        Phase-2 endpoints not yet deployed
      </div>
      <p className="mt-1 text-sm text-gray-300">{message}</p>
      <p className="mt-2 text-xs text-gray-400">
        Source:{" "}
        <a
          className="text-amber-200 hover:underline"
          href="https://github.com/Akshu1245/Secondbrain/blob/main/apps/aol/api/app/learned.py"
          target="_blank"
          rel="noreferrer"
        >
          apps/aol/api/app/learned.py
        </a>
        {" · "}
        <a
          className="text-amber-200 hover:underline"
          href="https://github.com/Akshu1245/Secondbrain/blob/main/apps/aol/api/tests/test_learned.py"
          target="_blank"
          rel="noreferrer"
        >
          tests/test_learned.py
        </a>
      </p>
    </div>
  );
}

function ModelStatus({ status }: { status: LearnedStatus }) {
  if (!status.trained) {
    return (
      <div className="rounded-xl border border-ink-800 bg-ink-950 p-4">
        <div className="text-xs uppercase tracking-wide text-gray-500">
          Model state
        </div>
        <p className="mt-1 text-sm text-gray-300">
          Untrained. The system is using the rule-based engagement estimate
          for every feature. Click <em>Train on current state</em> to fit
          weights from the on-device usage log.
        </p>
      </div>
    );
  }
  const m = status.metrics;
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Stat
        label="Test accuracy"
        value={m ? pct(m.test_accuracy) : "—"}
        hint={m ? `vs ${pct(m.majority_baseline)} baseline` : undefined}
      />
      <Stat
        label="Train accuracy"
        value={m ? pct(m.train_accuracy) : "—"}
        hint={m ? `log-loss ${m.train_log_loss}` : undefined}
      />
      <Stat
        label="Calibration gap"
        value={m ? m.calibration.abs_gap.toFixed(3) : "—"}
        hint={m ? `pred ${m.calibration.mean_pred} · actual ${m.calibration.mean_actual}` : undefined}
      />
      <Stat
        label="Rows"
        value={`${status.n_rows_train ?? "—"} / ${status.n_rows_test ?? "—"}`}
        hint={`v${status.version ?? "?"} weights persisted`}
      />
    </div>
  );
}

function TrainSummary({ result }: { result: LearnedTrainResult }) {
  const beats = result.beats_baseline;
  return (
    <div
      className={`rounded-xl border p-3 text-sm ${
        beats
          ? "border-emerald-400/40 bg-emerald-400/5 text-emerald-100"
          : "border-rose-400/40 bg-rose-400/5 text-rose-100"
      }`}
    >
      <div className="font-semibold">
        Training {beats ? "succeeded" : "did not beat baseline"}
      </div>
      <div className="mt-1 text-xs text-gray-300">
        train_acc={result.train_accuracy} · test_acc={result.test_accuracy} ·
        baseline={result.majority_baseline} ·{" "}
        loss {result.loss_curve_first_last?.[0]} → {result.loss_curve_first_last?.[1]}
      </div>
    </div>
  );
}

function RankedFeatures({ ranked }: { ranked: LearnedRanked[] }) {
  if (!ranked.length) {
    return null;
  }
  return (
    <div>
      <h3 className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wide text-gray-400">
        Features ranked by predicted engagement
      </h3>
      <ul className="space-y-2">
        {ranked.map((r) => (
          <li
            key={r.feature_id}
            className="rounded-xl border border-ink-800 bg-ink-950 p-3"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-gray-100">
                  {r.name}
                </div>
                <div className="text-xs text-gray-500">
                  {r.category} · {r.model}
                </div>
              </div>
              <div className="shrink-0 rounded-md border border-emerald-400/40 bg-emerald-400/10 px-2 py-1 text-xs font-bold text-emerald-200">
                {pct(r.prob_engaged)}
              </div>
            </div>
            {r.top_factors?.length > 0 && (
              <ul className="mt-2 grid grid-cols-1 gap-1 text-xs text-gray-400 sm:grid-cols-3">
                {r.top_factors.map((f) => (
                  <li
                    key={f.name}
                    className="rounded-md border border-ink-800 bg-ink-900 px-2 py-1"
                  >
                    <span className="text-gray-200">{f.name}</span>
                    <span className="text-gray-500"> · w={f.weight}</span>
                    <span
                      className={
                        f.contribution >= 0
                          ? "text-emerald-300"
                          : "text-rose-300"
                      }
                    >
                      {" "}{f.contribution >= 0 ? "+" : ""}
                      {f.contribution}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function pct(x: number | undefined): string {
  if (x === undefined || x === null || Number.isNaN(x)) return "—";
  return `${Math.round(x * 100)}%`;
}
