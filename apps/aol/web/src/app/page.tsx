"use client";

import { useEffect, useState, useCallback } from "react";
import { api, type ComputeLog, type Feature, type Optimised, type Suggestion, type ComputeStat } from "@/lib/api";
import { Card, Stat } from "@/components/Card";
import { Pill } from "@/components/Pill";
import { Architecture } from "@/components/Architecture";
import { LiveStats } from "@/components/LiveStats";
import { ScenarioPresets } from "@/components/ScenarioPresets";
import { PitchCard } from "@/components/PitchCard";
import { IntegrateCard } from "@/components/IntegrateCard";
import { ForwardCard } from "@/components/ForwardCard";

type Tab = "control" | "context" | "compute" | "before-after" | "feedback" | "pitch";

const TABS: { id: Tab; n: number; label: string; sub: string }[] = [
  { id: "control",      n: 1, label: "Hide what nobody uses",          sub: "declutter the AI menu" },
  { id: "context",      n: 2, label: "Show the right thing right now",  sub: "morning ≠ evening" },
  { id: "compute",      n: 3, label: "Run on phone vs cloud",           sub: "free + private when possible" },
  { id: "before-after", n: 4, label: "Before vs after Second Brain",             sub: "see the win, side-by-side" },
  { id: "feedback",     n: 5, label: "Learn what the user hates",       sub: "never come back if disabled" },
  { id: "pitch",        n: 6, label: "The pitch — numbers",              sub: "what to say to Mahmoud" },
];

export default function Home() {
  const [tab, setTab] = useState<Tab>("control");

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <Header />
      <div className="mt-4">
        <LiveStats />
        <p className="mt-2 text-xs text-gray-500">
          ↑ Live numbers from the demo backend. Click around in the tabs below — the numbers move.
        </p>
      </div>
      <div className="mt-4">
        <PitchCard />
      </div>
      <div className="mt-4 space-y-4">
        <Architecture />
        <ScenarioPresets />
      </div>
      <div className="mt-4">
        <IntegrateCard />
      </div>
      <div className="mt-6">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-gray-500">
          Six tabs · click each to see one thing Second Brain does
        </h3>
        <nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-xl border px-3 py-2 text-left transition ${
                tab === t.id
                  ? "border-emerald-400/60 bg-emerald-400/10"
                  : "border-ink-800 bg-ink-900 hover:border-ink-700"
              }`}
            >
              <div className="flex items-center gap-1.5">
                <span className="rounded-md border border-emerald-400/40 bg-emerald-400/10 px-1.5 py-0.5 text-[10px] font-bold text-emerald-300">
                  {t.n}
                </span>
                <span className="text-sm font-semibold text-gray-100">{t.label}</span>
              </div>
              <div className="mt-1 text-xs text-gray-400">{t.sub}</div>
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-6 space-y-6">
        {tab === "control"      && <ControlPanel />}
        {tab === "context"      && <ContextEngine />}
        {tab === "compute"      && <ComputeRouter />}
        {tab === "before-after" && <BeforeAfter />}
        {tab === "feedback"     && <FeedbackPanel />}
        {tab === "pitch"        && <PitchEvidence />}
      </div>
      <div className="mt-8">
        <ForwardCard />
      </div>
      <p className="mt-6 text-center text-xs text-gray-500">
        Built by Akshay · <a className="hover:text-emerald-300" href="https://github.com/Akshu1245/Secondbrain" target="_blank" rel="noreferrer">github.com/Akshu1245/Secondbrain</a> · open-source, drop-in, no SDK
      </p>
    </main>
  );
}

function Header() {
  return (
    <header className="rounded-2xl border border-ink-800 bg-gradient-to-br from-ink-900 via-ink-950 to-ink-900 p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-emerald-400/40 bg-emerald-400/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.25em] text-emerald-300">
              Second Brain
            </span>
            <span className="rounded-full border border-ink-700 bg-ink-900 px-2.5 py-0.5 text-[10px] uppercase tracking-wider text-gray-400">
              v0.4 · live demo
            </span>
            <span className="rounded-full border border-sky-500/30 bg-sky-500/10 px-2.5 py-0.5 text-[10px] uppercase tracking-wider text-sky-300">
              memory + routing layer for OEM AI
            </span>
          </div>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Phones ship too much AI nobody uses. Second Brain fixes that.
          </h1>
          <p className="mt-2 max-w-3xl text-base text-gray-300">
            One drop-in layer the OEM (<span className="text-gray-100">Moto</span>,{" "}
            <span className="text-gray-100">Samsung</span>, <span className="text-gray-100">OnePlus</span>) ships beside its AI assistant. It{" "}
            <span className="text-emerald-300">hides features the user never opens</span>,{" "}
            <span className="text-emerald-300">runs the rest on-device</span> when it can (faster, free, private),
            and <span className="text-emerald-300">remembers what the user disabled</span> so it doesn&rsquo;t come back.
          </p>
          <p className="mt-2 max-w-3xl text-sm text-gray-500">
            ~131 lines of Kotlin · rule-based · live demo below · open-source on GitHub.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <a
              href="https://github.com/Akshu1245/Secondbrain/tree/main/docs/oem-pitch"
              target="_blank"
              rel="noreferrer"
              className="rounded-lg border border-emerald-400/50 bg-emerald-400/10 px-3 py-1.5 text-sm font-medium text-emerald-200 hover:bg-emerald-400/20"
            >
              Read the pitch package →
            </a>
            <a
              href="https://github.com/Akshu1245/Secondbrain"
              target="_blank"
              rel="noreferrer"
              className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-1.5 text-sm text-gray-200 hover:border-emerald-400/40"
            >
              GitHub repo
            </a>
            <a
              href="#how-it-fits-in"
              className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-1.5 text-sm text-gray-200 hover:border-emerald-400/40"
            >
              View architecture ↓
            </a>
          </div>
        </div>
        <div className="flex shrink-0 flex-col items-start gap-2 lg:items-end">
          <ResetButton />
          <p className="max-w-xs text-right text-[11px] text-gray-500">
            Re-seeds 24 named Moto AI features + 30d of usage so every visitor
            sees the same baseline.
          </p>
        </div>
      </div>
    </header>
  );
}

function ResetButton() {
  const [busy, setBusy] = useState(false);
  return (
    <button
      onClick={async () => {
        setBusy(true);
        try { await api.reset(); } finally { setBusy(false); window.location.reload(); }
      }}
      className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-1.5 text-sm text-gray-300 hover:border-emerald-400/50 hover:text-emerald-300 disabled:opacity-50"
      disabled={busy}
      title="Re-seed the mock dataset and regenerate 30 days of usage"
    >
      {busy ? "Resetting…" : "Reset demo data"}
    </button>
  );
}

// ── Tab: Control Panel ─────────────────────────────────────────────────────

function ControlPanel() {
  const [data, setData] = useState<Optimised | null>(null);
  const [features, setFeatures] = useState<Feature[]>([]);
  const [prefs, setPrefs] = useState<{ priority_categories: string[]; battery_saver: boolean; data_saver: boolean; private_mode: boolean }>(
    { priority_categories: [], battery_saver: false, data_saver: false, private_mode: false },
  );

  const reload = useCallback(async () => {
    const [opt, all] = await Promise.all([api.optimised(), api.features()]);
    setData(opt);
    setFeatures(all.features);
    setPrefs(all.user_prefs);
  }, []);
  useEffect(() => { reload(); }, [reload]);

  const allCategories = Array.from(new Set(features.map((f) => f.category))).sort();

  return (
    <>
      <Card
        title="User preferences"
        subtitle="Drives the smart filter + compute router"
      >
        <div className="space-y-4">
          <div>
            <div className="mb-2 text-xs uppercase tracking-wide text-gray-500">Priority categories</div>
            <div className="flex flex-wrap gap-2">
              {allCategories.map((c) => {
                const active = prefs.priority_categories.includes(c);
                return (
                  <button
                    key={c}
                    onClick={async () => {
                      const next = active
                        ? prefs.priority_categories.filter((x) => x !== c)
                        : [...prefs.priority_categories, c];
                      await api.prefs({ priority_categories: next });
                      reload();
                    }}
                    className={`rounded-full border px-3 py-1 text-sm transition ${
                      active
                        ? "border-emerald-400/60 bg-emerald-400/10 text-emerald-200"
                        : "border-ink-700 bg-ink-900 text-gray-300 hover:border-ink-600"
                    }`}
                  >
                    {c}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            {(["battery_saver", "data_saver", "private_mode"] as const).map((k) => (
              <label key={k} className="flex items-center gap-3 rounded-lg border border-ink-800 bg-ink-950 px-3 py-2">
                <input
                  type="checkbox"
                  checked={prefs[k]}
                  onChange={async (e) => {
                    await api.prefs({ [k]: e.target.checked });
                    reload();
                  }}
                  className="h-4 w-4 accent-emerald-400"
                />
                <span className="text-sm">{k.replace("_", " ")}</span>
              </label>
            ))}
          </div>
        </div>
      </Card>

      {data && (
        <>
          <Card
            title={`Visible features (${data.visible.length})`}
            subtitle="What the OEM AI assistant should surface, after Second Brain applies the rules"
          >
            <ul className="divide-y divide-ink-800">
              {data.visible.map((f) => (
                <FeatureRow key={f.id} f={f} onChange={reload} />
              ))}
            </ul>
          </Card>
          <Card
            title={`Second Brain recommends hiding (${data.hide_recommended.length})`}
            subtitle={`Used < ${data.rules.low_usage_threshold_events_30d} times in last 30 days and not in your priority categories`}
          >
            <ul className="divide-y divide-ink-800">
              {data.hide_recommended.map((f) => (
                <FeatureRow key={f.id} f={f} onChange={reload} dim />
              ))}
            </ul>
          </Card>
          {data.user_disabled.length > 0 && (
            <Card title={`Disabled by you (${data.user_disabled.length})`}>
              <ul className="divide-y divide-ink-800">
                {data.user_disabled.map((f) => (
                  <FeatureRow key={f.id} f={f} onChange={reload} dim />
                ))}
              </ul>
            </Card>
          )}
        </>
      )}
    </>
  );
}

function FeatureRow({ f, onChange, dim }: { f: Feature; onChange: () => void; dim?: boolean }) {
  return (
    <li className={`flex items-center justify-between gap-4 py-3 ${dim ? "opacity-70" : ""}`}>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium">{f.name}</span>
          <Pill tone={f.compute_class as "light" | "medium" | "heavy"}>{f.compute_class}</Pill>
          <Pill>{f.category}</Pill>
        </div>
        <div className="mt-1 text-xs text-gray-400">{f.description}</div>
        <div className="mt-1 text-xs text-gray-500">
          {f.events ?? 0} events / 30d · {f.share_pct ?? 0}% of total
          {typeof f.ms_local === "number" && (
            <span> · local {f.ms_local}ms · cloud {f.ms_cloud}ms</span>
          )}
        </div>
      </div>
      <label className="flex shrink-0 items-center gap-2">
        <input
          type="checkbox"
          checked={f.enabled ?? false}
          onChange={async (e) => {
            await api.toggle(f.id, e.target.checked);
            onChange();
          }}
          className="h-4 w-4 accent-emerald-400"
        />
        <Pill tone={f.enabled ? "on" : "off"}>{f.enabled ? "ON" : "OFF"}</Pill>
      </label>
    </li>
  );
}

// ── Tab: Context Engine ───────────────────────────────────────────────────

function ContextEngine() {
  const [tod, setTod] = useState("morning");
  const [act, setAct] = useState("commute");
  const [data, setData] = useState<{ context: { time_of_day: string; activity: string }; suggestions: Suggestion[] } | null>(null);

  const refresh = useCallback(async () => {
    setData(await api.context(tod, act));
  }, [tod, act]);
  useEffect(() => { refresh(); }, [refresh]);

  return (
    <Card
      title="Context-aware suggestions"
      subtitle="What Second Brain would surface to the user given the current context"
    >
      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Selector label="Time of day" value={tod} onChange={setTod}
          options={["morning", "midday", "evening", "night"]} />
        <Selector label="Activity" value={act} onChange={setAct}
          options={["commute", "exercise", "work", "meeting", "leisure", "errands", "winddown", "sleeping"]} />
      </div>
      {data && (
        <ul className="space-y-3">
          {data.suggestions.map((s) => (
            <li key={s.id} className="rounded-xl border border-ink-800 bg-ink-950 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{s.name}</div>
                  <div className="text-xs text-gray-400">{s.reason} · {s.usage_events} events / 30d</div>
                </div>
                <Pill>{s.category}</Pill>
              </div>
            </li>
          ))}
          {data.suggestions.length === 0 && (
            <li className="rounded-xl border border-ink-800 bg-ink-950 p-4 text-sm text-gray-400">
              No suggestions for this context — features in this slot are all disabled.
            </li>
          )}
        </ul>
      )}
    </Card>
  );
}

function Selector({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-gray-500">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm"
      >
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );
}

// ── Tab: Compute Router ────────────────────────────────────────────────────

function ComputeRouter() {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [pick, setPick] = useState("");
  const [stats, setStats] = useState<ComputeStat | null>(null);
  const [log, setLog] = useState<ComputeLog[]>([]);

  const reload = useCallback(async () => {
    const [all, l] = await Promise.all([api.features(), api.computeLog()]);
    setFeatures(all.features);
    if (!pick && all.features.length) setPick(all.features[0].id);
    setStats(l.stats);
    setLog(l.log);
  }, [pick]);
  useEffect(() => { reload(); }, [reload]);

  return (
    <>
      <Card
        title="Routing decision"
        subtitle="Pick a feature; Second Brain decides whether to run it on-device or in the cloud, and explains why"
      >
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1">
            <span className="text-xs uppercase tracking-wide text-gray-500">Feature</span>
            <select
              value={pick}
              onChange={(e) => setPick(e.target.value)}
              className="w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm sm:min-w-[18rem] sm:w-auto"
            >
              {features.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.compute_class})
                </option>
              ))}
            </select>
          </label>
          <button
            onClick={async () => {
              if (!pick) return;
              await api.route(pick);
              reload();
            }}
            className="rounded-lg border border-emerald-400/60 bg-emerald-400/10 px-4 py-2 text-sm font-medium text-emerald-200 hover:bg-emerald-400/20"
          >
            Run routing
          </button>
        </div>
      </Card>

      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Total decisions" value={stats.total} />
          <Stat label="Local" value={`${stats.local_pct}%`} hint="on-device, free" />
          <Stat label="Cloud" value={`${stats.cloud_pct}%`} hint="paid + network" />
          <Stat label="Avg latency saved" value={`${stats.saved_ms_avg} ms`} hint={`vs. naïve routing`} />
        </div>
      )}

      <Card title="Recent decisions" subtitle="Most-recent first; every decision shows the rule that fired">
        <ul className="divide-y divide-ink-800">
          {log.map((e, i) => (
            <li key={i} className="flex items-center justify-between gap-3 py-3">
              <div>
                <div className="flex items-center gap-2">
                  <Pill tone={e.decision}>{e.decision}</Pill>
                  <span className="font-medium">{e.feature_name}</span>
                </div>
                <div className="mt-0.5 text-xs text-gray-400">{e.reason}</div>
              </div>
              <div className="shrink-0 text-right text-xs text-gray-500">
                <div>{e.chosen_ms} ms (vs {e.alt_ms} ms)</div>
                <div>${e.cost_usd.toFixed(4)}</div>
              </div>
            </li>
          ))}
          {log.length === 0 && (
            <li className="py-3 text-sm text-gray-400">No decisions yet — pick a feature above and click Run routing.</li>
          )}
        </ul>
      </Card>
    </>
  );
}

// ── Tab: Before / After ────────────────────────────────────────────────────

type BAfter = {
  before: { feature_count: number; features: Feature[] };
  after: { feature_count: number; features: Feature[]; hidden_count: number };
  savings: { features_hidden_pct: number; compute: ComputeStat };
};

function BeforeAfter() {
  const [data, setData] = useState<BAfter | null>(null);

  useEffect(() => {
    api.beforeAfter().then((d) => setData(d as BAfter));
  }, []);

  if (!data) return <Card title="Loading…">Pulling demo data.</Card>;

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Surface size — before" value={data.before.feature_count} hint="every default-on feature" />
        <Stat label="Surface size — after"  value={data.after.feature_count} hint="Second Brain-optimised" />
        <Stat label="Features hidden" value={`${data.savings.features_hidden_pct}%`} hint={`${data.after.hidden_count} features`} />
        <Stat label="Cloud calls saved" value={`$${data.savings.compute.saved_usd.toFixed(4)}`} hint={`${data.savings.compute.local_pct}% on-device`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Before Second Brain" subtitle="OEM default — every AI feature surfaced equally" right={<Pill tone="off">noisy</Pill>}>
          <ul className="space-y-2">
            {data.before.features.map((f) => (
              <li key={f.id} className="flex items-center justify-between gap-3 rounded-lg border border-ink-800 bg-ink-950 px-3 py-2">
                <div className="min-w-0">
                  <div className="font-medium">{f.name}</div>
                  <div className="text-xs text-gray-500">{f.category}</div>
                </div>
                <Pill tone={f.compute_class as "light" | "medium" | "heavy"}>{f.compute_class}</Pill>
              </li>
            ))}
          </ul>
        </Card>
        <Card title="After Second Brain" subtitle="Visible to user, ordered by relevance" right={<Pill tone="on">clean</Pill>}>
          <ul className="space-y-2">
            {data.after.features.map((f) => (
              <li key={f.id} className="flex items-center justify-between gap-3 rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-3 py-2">
                <div className="min-w-0">
                  <div className="font-medium">{f.name}</div>
                  <div className="text-xs text-gray-400">{f.category} · {f.events} events / 30d</div>
                </div>
                <Pill tone={f.compute_class as "light" | "medium" | "heavy"}>{f.compute_class}</Pill>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </>
  );
}

// ── Tab: Feedback Loop ─────────────────────────────────────────────────────

function FeedbackPanel() {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [pick, setPick] = useState("");
  const [rating, setRating] = useState("ok");
  const [comment, setComment] = useState("");
  const [list, setList] = useState<{ entries: any[]; improvement_suggestions: any[]; memory_suggestions: any[] }>({ entries: [], improvement_suggestions: [], memory_suggestions: [] });

  const reload = useCallback(async () => {
    const [all, fb] = await Promise.all([api.features(), api.feedbackList()]);
    setFeatures(all.features);
    if (!pick && all.features.length) setPick(all.features[0].id);
    setList(fb);
  }, [pick]);
  useEffect(() => { reload(); }, [reload]);

  return (
    <>
      <Card title="Submit feedback" subtitle="Drives the system's nightly improvement suggestions">
        <div className="grid gap-3 sm:grid-cols-3">
          <label className="flex flex-col gap-1">
            <span className="text-xs uppercase tracking-wide text-gray-500">Feature</span>
            <select value={pick} onChange={(e) => setPick(e.target.value)}
              className="rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm">
              {features.map((f) => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs uppercase tracking-wide text-gray-500">Rating</span>
            <select value={rating} onChange={(e) => setRating(e.target.value)}
              className="rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm">
              {["love", "ok", "annoying", "never_use"].map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs uppercase tracking-wide text-gray-500">Comment (optional)</span>
            <input value={comment} onChange={(e) => setComment(e.target.value)}
              placeholder="e.g. eats battery"
              className="rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm" />
          </label>
        </div>
        <button
          onClick={async () => {
            if (!pick) return;
            await api.feedback({ feature_id: pick, rating, comment: comment || undefined });
            setComment("");
            reload();
          }}
          className="mt-3 rounded-lg border border-emerald-400/60 bg-emerald-400/10 px-4 py-2 text-sm font-medium text-emerald-200 hover:bg-emerald-400/20"
        >
          Submit
        </button>
      </Card>

      {list.improvement_suggestions.length > 0 && (
        <Card title="System-layer recommendations" subtitle="What Second Brain would change in the next optimisation cycle">
          <ul className="space-y-2">
            {list.improvement_suggestions.map((s, i) => (
              <li key={i} className="rounded-xl border border-amber-500/30 bg-amber-500/5 px-4 py-3">
                <div className="flex items-center gap-2">
                  <Pill tone={s.action.startsWith("auto_disable") ? "off" : "on"}>
                    {s.action.replace("_recommended", "")}
                  </Pill>
                  <span className="font-medium">{s.name}</span>
                </div>
                <div className="mt-1 text-xs text-gray-400">{s.reason}</div>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {(list.memory_suggestions?.length ?? 0) > 0 && (
        <Card
          title="Memory-informed recommendations"
          subtitle={"Memory-backed — durable patterns in the last 90d, not flaps on a single bad day"}
        >
          <ul className="space-y-2">
            {list.memory_suggestions.map((s: any, i: number) => (
              <li
                key={i}
                className={
                  "rounded-xl px-4 py-3 " +
                  (s.confidence === "high"
                    ? "border border-rose-500/40 bg-rose-500/5"
                    : "border border-sky-500/30 bg-sky-500/5")
                }
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Pill tone={s.confidence === "high" ? "off" : "on"}>
                    {s.confidence === "high" ? "high confidence" : "medium confidence"}
                  </Pill>
                  <span className="font-medium">{s.name}</span>
                  <span className="text-xs text-gray-400">
                    · disabled {s.signals.disable_count}× · negative ratings {s.signals.negative_ratings}
                  </span>
                </div>
                <ul className="mt-2 space-y-0.5 text-xs text-gray-400">
                  {s.evidence.map((e: string, j: number) => (
                    <li key={j}>• {e}</li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
          <div className="mt-3 rounded-md border border-ink-800 bg-ink-900/40 p-3 text-xs text-gray-400">
            <span className="font-medium text-gray-300">How this wires up:</span>{" "}
            Second Brain&apos;s Feedback Loop (Module 6) queries the memory layer for
            per-feature episodic history — every toggle-off, every rating, every
            context hide in the last <span className="font-mono">{90}</span> days. A
            recommendation surfaces here only when there are at least two durable
            signals, so a single annoyed tap never produces a &quot;auto-hide this?&quot;
            prompt. In production the backend proxies to the memory layer&apos;s MCP
            endpoint <span className="font-mono">/recall?feature_id=…&amp;days=90</span>;
            the demo reads the same local state the memory layer writes.
          </div>
        </Card>
      )}

      <Card title="Recent feedback" subtitle={`${list.entries.length} entries`}>
        <ul className="divide-y divide-ink-800">
          {list.entries.slice(0, 30).map((e, i) => (
            <li key={i} className="flex items-center justify-between gap-3 py-2 text-sm">
              <div>
                <span className="font-medium">{features.find((f) => f.id === e.feature_id)?.name ?? e.feature_id}</span>
                <span className="ml-2 text-xs text-gray-400">{e.comment ?? "—"}</span>
              </div>
              <Pill tone={e.rating === "love" ? "on" : e.rating === "annoying" || e.rating === "never_use" ? "off" : "off"}>
                {e.rating}
              </Pill>
            </li>
          ))}
          {list.entries.length === 0 && (
            <li className="py-2 text-sm text-gray-400">No feedback yet.</li>
          )}
        </ul>
      </Card>
    </>
  );
}

// ── Tab: Pitch Evidence ────────────────────────────────────────────────────

function PitchEvidence() {
  return (
    <>
      <Card title="The problem Second Brain solves" subtitle="Independently sourced; receipts in docs/oem-targets.md">
        <ul className="space-y-3 text-sm">
          <Bullet>
            <strong>73% of iPhone users and 87% of Samsung users</strong> say AI features add little to no value.
            <span className="text-gray-500"> — TechRadar, May 2025</span>
          </Bullet>
          <Bullet>
            <strong>86.5% of iPhone AI users and 94.5% of Samsung users</strong> would not pay to use AI features.
            <span className="text-gray-500"> — TechRadar / SellCell survey</span>
          </Bullet>
          <Bullet>
            Only <strong>11% of US adults</strong> would upgrade their phone for AI features — down 7 pts YoY.
            <span className="text-gray-500"> — ITC.ua, 2025</span>
          </Bullet>
          <Bullet>
            Top complaint about Moto AI specifically: <em>"forced installation as bloatware after system updates"</em> + Perplexity pre-install rejection.
            <span className="text-gray-500"> — MakeUseOf / Chrome-Stats</span>
          </Bullet>
        </ul>
      </Card>

      <Card title="Where Second Brain plugs in" subtitle="Same surface, two complementary layers">
        <ul className="space-y-3 text-sm">
          <Bullet>
            <strong>For OEMs (B2B):</strong> Second Brain sits between user and their AI assistant. Cuts cloud-compute spend by routing every request through Compute Optimizer; lifts engagement by hiding feature clutter; surfaces context-relevant features instead of dumping all 20+ on the home screen.
          </Bullet>
          <Bullet>
            <strong>For users (B2C-feel):</strong> Control Panel they actually own. Toggle off the AI Wallpaper Studio nobody uses, prioritise the categories that match their day. Battery / data / private modes that *the AI assistant respects*.
          </Bullet>
          <Bullet>
            <strong>Companion product (separate repo):</strong> Second Brain MCP server provides the on-device memory + knowledge graph that fixes "Remember This" / "Pay Attention" amnesia. Together these are the two layers Moto AI is missing.
          </Bullet>
        </ul>
      </Card>

      <Card title="Why now" subtitle="Read this in any cold email">
        <p className="text-sm text-gray-300">
          Every OEM is paying for cloud AI compute users won&apos;t pay for. That&apos;s an unsustainable subsidy.
          Second Brain is the only middleware whose explicit success metric is{" "}
          <strong className="text-emerald-300">$ saved per device per month</strong>, not features shipped.
          A pilot on 10,000 devices is a measurable line in next quarter&apos;s P&amp;L.
        </p>
      </Card>
    </>
  );
}

function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <li className="rounded-xl border border-ink-800 bg-ink-950 px-4 py-3">
      <div className="flex gap-3">
        <span className="mt-0.5 text-emerald-400">▸</span>
        <span className="text-gray-200">{children}</span>
      </div>
    </li>
  );
}
