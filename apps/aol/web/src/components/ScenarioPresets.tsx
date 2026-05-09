"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type Preset = {
  id: string;
  label: string;
  hint: string;
  prefs: Record<string, unknown>;
};

const PRESETS: Preset[] = [
  {
    id: "healthy",
    label: "Healthy device",
    hint: "battery 80% · all toggles off",
    prefs: { battery_saver: false, data_saver: false, private_mode: false },
  },
  {
    id: "low-battery",
    label: "Low battery",
    hint: "battery_saver on → heavy cloud features auto-hide",
    prefs: { battery_saver: true, data_saver: false, private_mode: false },
  },
  {
    id: "data-saver",
    label: "Data saver",
    hint: "data_saver on → cloud-only routes drop off",
    prefs: { battery_saver: false, data_saver: true, private_mode: false },
  },
  {
    id: "private",
    label: "Private mode",
    hint: "private_mode on → routing hard-locks to local",
    prefs: { battery_saver: false, data_saver: false, private_mode: true },
  },
];

/**
 * One-click context flips for the demo. A Moto PM should never have to
 * scroll through three checkboxes to see what Second Brain does on a low-battery
 * device — they should click "Low battery" and see it.
 */
export function ScenarioPresets() {
  const [active, setActive] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  return (
    <div className="rounded-2xl border border-ink-800 bg-ink-950/60 p-4">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-3">
        <div className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400/80">
          Click one — see Second Brain react
        </div>
        <div className="text-xs text-gray-500">
          Pretends the user&rsquo;s phone is in this state, then reloads the page so you can see what changes.
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {PRESETS.map((p) => {
          const isActive = active === p.id;
          return (
            <button
              key={p.id}
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                setActive(p.id);
                try {
                  await api.prefs(p.prefs);
                } finally {
                  setBusy(false);
                  // hard reload so all tabs pick up the new context
                  window.location.reload();
                }
              }}
              className={`rounded-xl border px-3 py-2 text-left transition disabled:opacity-50 ${
                isActive
                  ? "border-emerald-400/60 bg-emerald-400/10"
                  : "border-ink-800 bg-ink-900 hover:border-ink-600"
              }`}
            >
              <div className="text-sm font-semibold text-gray-100">{p.label}</div>
              <div className="text-xs text-gray-400">{p.hint}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
