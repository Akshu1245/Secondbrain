import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Second Brain × Moto AI — 60-second tour",
  description:
    "Self-guided walkthrough of how Second Brain improves each Moto AI surface — for an OEM PM who has 60 seconds.",
};

const REPO_BASE = "https://github.com/Akshu1245/Secondbrain/blob/main";
const APPENDIX = `${REPO_BASE}/docs/oem-pitch/moto-specific.md`;
const ONEPAGER = `${REPO_BASE}/docs/oem-pitch/one-pager.md`;
const PITCH_DECK = `${REPO_BASE}/docs/oem-pitch/pitch-deck.md`;
const INTEGRATION = `${REPO_BASE}/docs/oem-pitch/integration/README.md`;

type Module = {
  n: number;
  title: string;
  oneLine: string;
  today: string;
  withAol: string;
  motoFeatures: { name: string; routed: string }[];
  demoLink?: { href: string; label: string };
};

const MODULES: Module[] = [
  {
    n: 1,
    title: "Usage Tracker",
    oneLine: "Per-feature event log on the device, refreshed every 30 days.",
    today:
      "Cloud telemetry knows which Moto AI features get used. The device doesn't, so UI decisions can't react in <50 ms.",
    withAol:
      "On-device counters for each feature×day. Drives Smart Filter and Context Engine without a network round-trip.",
    motoFeatures: [
      { name: "Catch Me Up", routed: "tracked" },
      { name: "Pay Attention", routed: "tracked" },
      { name: "Remember This", routed: "tracked" },
      { name: "Magic Canvas", routed: "tracked" },
      { name: "Ask or Search", routed: "tracked" },
      { name: "Next Move + Smart Connect", routed: "tracked" },
    ],
    demoLink: { href: "/?tab=before-after", label: "See in demo →" },
  },
  {
    n: 2,
    title: "Smart Feature Filter",
    oneLine:
      "Hides features with <3 events / 30 days unless they're in a user-priority category.",
    today:
      "Moto AI prompt bar shows all 9+ features regardless of usage. Reddit complaints about Moto AI cluster around 'too many AI things I don't use.'",
    withAol:
      "Prompt bar drops from 9 → 4–5 on a power user, 9 → 2 on a Catch-Me-Up-only user. Nobody loses a favourite.",
    motoFeatures: [
      { name: "Magic Canvas (low usage)", routed: "hidden by default" },
      { name: "Image Studio (low usage)", routed: "hidden by default" },
      { name: "Look and Talk (specialist)", routed: "hidden by default" },
      { name: "Catch Me Up (heavy usage)", routed: "kept visible" },
      { name: "Smart Reply (heavy usage)", routed: "kept visible" },
    ],
    demoLink: { href: "/?tab=control", label: "Toggle in demo →" },
  },
  {
    n: 3,
    title: "Context Engine",
    oneLine:
      "(time_of_day, activity) → top-3 surfaced features. Rule-based, no ML.",
    today:
      "Pay Attention requires the user to remember to launch it before a meeting. Most miss the start.",
    withAol:
      "Morning + on calendar → Pay Attention surfaces. Commute + headphones → Smart Connect + Ask. Rules cleared by legal in days, not quarters.",
    motoFeatures: [
      { name: "Pay Attention", routed: "auto-suggested at meeting start" },
      { name: "Catch Me Up", routed: "morning surface" },
      { name: "Smart Connect", routed: "commute + media surface" },
      { name: "Look and Talk", routed: "evening + media surface" },
    ],
    demoLink: { href: "/?tab=context", label: "See current context →" },
  },
  {
    n: 4,
    title: "Compute Optimizer",
    oneLine:
      "Per-call rule-based local-vs-cloud routing with battery / data / private-mode overrides.",
    today:
      "Catch Me Up + Smart Reply + Remember This are cloud-only on Moto today. ~50 invocations / device / day × 14.5 M Q2 2025 shipments = a seven-figure annual cloud-AI line.",
    withAol:
      "~45% of calls stay on-device. Heavy generative tasks (Pay Attention, Image Studio) stay cloud — the routing knows the difference.",
    motoFeatures: [
      { name: "Catch Me Up (light)", routed: "→ local" },
      { name: "Smart Reply (light)", routed: "→ local" },
      { name: "Remember This (light)", routed: "→ local" },
      { name: "Pay Attention (heavy)", routed: "→ cloud (correct)" },
      { name: "Image Studio (heavy)", routed: "→ cloud (correct)" },
      { name: "Live Caption", routed: "→ local for English/Hindi" },
    ],
    demoLink: { href: "/?tab=compute", label: "Watch a live decision →" },
  },
  {
    n: 5,
    title: "Control Panel",
    oneLine: "User-visible Settings page: Private / Battery / Data + category prioritisation.",
    today:
      "Galaxy AI is being pushed into a paid SKU. Moto AI has no equivalent trust artefact — no 'AI you can turn off' surface.",
    withAol:
      "Three top-level toggles plus 2-of-5 category prioritisation. Direct response to the 'my AI is reading my messages' churn driver.",
    motoFeatures: [
      { name: "Private mode", routed: "every call local" },
      { name: "Battery saver", routed: "heavy → cloud, speculative → off" },
      { name: "Data saver", routed: "non-heavy → local until Wi-Fi" },
    ],
    demoLink: { href: "/?tab=control", label: "Try the toggles →" },
  },
  {
    n: 6,
    title: "Feedback Loop",
    oneLine:
      "{love / ok / annoying / never_use} → automatic policy suggestions on the device.",
    today:
      "Moto AI beta program collects 'did you like this feature' qualitative. No per-invocation, per-context signal.",
    withAol:
      "3+ 'annoying' → auto-prompt to disable. 5+ 'love' → promote to top of the prompt bar. Policy from the user, not from product.",
    motoFeatures: [
      { name: "Annoying signal → Smart Filter", routed: "auto-hide" },
      { name: "Love signal → Smart Filter", routed: "auto-pin" },
      { name: "Never-use signal → Filter", routed: "permanent hide" },
    ],
    demoLink: { href: "/?tab=feedback", label: "See the loop →" },
  },
];

const HEADLINE_NUMBERS = [
  { label: "Of Moto AI calls stay on-device", value: "~45 %", hint: "from the live demo, after honest-numbers fix" },
  { label: "Integration code", value: "131 LOC", hint: "AolClient.kt + IAolMiddleware.aidl, cloc-verified" },
  { label: "Lenovo-Motorola Q2 2025 shipments", value: "14.5 M", hint: "TechInsights, Sep 2025" },
  { label: "Module count", value: "6", hint: "Usage / Filter / Context / Compute / Control / Feedback" },
];

export default function TourPage() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <header className="mb-10">
        <p className="text-xs uppercase tracking-widest text-emerald-400">
          60-second tour · for an OEM PM with no time
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-gray-50 sm:text-4xl">
          Second Brain × Moto AI
        </h1>
        <p className="mt-3 max-w-3xl text-base text-gray-300">
          A 6-module middleware that routes ~45% of Moto AI calls on-device,
          hides features the user never touches, and surfaces the right
          feature at the right time. Drop-in via AIDL in <strong>131 lines</strong>.
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {HEADLINE_NUMBERS.map((s) => (
            <div
              key={s.label}
              className="rounded-xl border border-ink-800 bg-ink-900/70 px-4 py-3"
            >
              <div className="text-xs uppercase tracking-wide text-gray-500">
                {s.label}
              </div>
              <div className="mt-1 text-2xl font-semibold text-gray-50">
                {s.value}
              </div>
              <div className="mt-1 text-xs text-gray-500">{s.hint}</div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-3 text-sm">
          <Link
            href="/"
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-emerald-300 hover:bg-emerald-500/20"
          >
            Open the live dashboard →
          </Link>
          <a
            href={APPENDIX}
            className="rounded-lg border border-ink-800 bg-ink-900 px-3 py-2 text-gray-300 hover:bg-ink-800"
          >
            Full Moto-specific appendix
          </a>
          <a
            href={INTEGRATION}
            className="rounded-lg border border-ink-800 bg-ink-900 px-3 py-2 text-gray-300 hover:bg-ink-800"
          >
            AIDL + Kotlin reference
          </a>
        </div>
      </header>

      <ol className="space-y-6">
        {MODULES.map((m) => (
          <li
            key={m.n}
            className="rounded-2xl border border-ink-800 bg-ink-900/70 p-6"
          >
            <div className="flex items-baseline gap-3">
              <span className="text-xs font-medium uppercase tracking-widest text-gray-500">
                Module {m.n}
              </span>
              <h2 className="text-lg font-semibold text-gray-50">{m.title}</h2>
            </div>
            <p className="mt-2 text-sm text-gray-300">{m.oneLine}</p>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-ink-800 bg-ink-950/60 p-4">
                <div className="text-xs uppercase tracking-wide text-rose-400/80">
                  On Moto today
                </div>
                <p className="mt-1 text-sm text-gray-300">{m.today}</p>
              </div>
              <div className="rounded-xl border border-emerald-700/40 bg-emerald-900/15 p-4">
                <div className="text-xs uppercase tracking-wide text-emerald-300">
                  With Second Brain
                </div>
                <p className="mt-1 text-sm text-gray-200">{m.withAol}</p>
              </div>
            </div>

            <div className="mt-4">
              <div className="text-xs uppercase tracking-wide text-gray-500">
                Moto AI features touched
              </div>
              <ul className="mt-2 flex flex-wrap gap-2">
                {m.motoFeatures.map((f) => (
                  <li
                    key={f.name}
                    className="rounded-full border border-ink-800 bg-ink-950 px-3 py-1 text-xs text-gray-300"
                  >
                    <span className="font-medium text-gray-100">{f.name}</span>
                    <span className="ml-2 text-gray-500">{f.routed}</span>
                  </li>
                ))}
              </ul>
            </div>

            {m.demoLink && (
              <div className="mt-4">
                <Link
                  href={m.demoLink.href}
                  className="text-xs font-medium text-emerald-300 hover:text-emerald-200"
                >
                  {m.demoLink.label}
                </Link>
              </div>
            )}
          </li>
        ))}
      </ol>

      <section className="mt-12 rounded-2xl border border-emerald-700/40 bg-emerald-900/15 p-6">
        <h2 className="text-lg font-semibold text-gray-50">The ask</h2>
        <p className="mt-2 max-w-3xl text-sm text-gray-200">
          A 90-day pilot on <strong>10 000 razr / edge units</strong> in one
          geography (India is the natural fit given Q2 2025 +43% YoY growth).
          Drop in <code>AolClient.kt</code> + <code>IAolMiddleware.aidl</code>{" "}
          as a silent A/B alongside the current Moto AI. Decision gate at week
          12 on per-device licence + audited rev-share on the cloud-spend
          delta.
        </p>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <a
            href="mailto:rashisolutions1245@gmail.com?subject=Moto%20AI%20%C3%97%20Second Brain%20pilot%20%E2%80%94%20intro%20call"
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-emerald-300 hover:bg-emerald-500/20"
          >
            Email Akshay (rashisolutions1245@gmail.com) →
          </a>
          <a
            href={ONEPAGER}
            className="rounded-lg border border-ink-800 bg-ink-900 px-3 py-2 text-gray-300 hover:bg-ink-800"
          >
            One-pager
          </a>
          <a
            href={PITCH_DECK}
            className="rounded-lg border border-ink-800 bg-ink-900 px-3 py-2 text-gray-300 hover:bg-ink-800"
          >
            Pitch deck (10 slides)
          </a>
        </div>
      </section>

      <footer className="mt-10 text-center text-xs text-gray-500">
        Live demo:{" "}
        <Link href="/" className="text-gray-400 hover:text-gray-200">
          out-ujjsjvxm.devinapps.com
        </Link>{" "}
        · API:{" "}
        <a
          href="https://aol-api-yfdwxezt.fly.dev/docs"
          className="text-gray-400 hover:text-gray-200"
        >
          aol-api-yfdwxezt.fly.dev/docs
        </a>{" "}
        · Repo:{" "}
        <a
          href="https://github.com/Akshu1245/Secondbrain"
          className="text-gray-400 hover:text-gray-200"
        >
          github.com/Akshu1245/Secondbrain
        </a>
      </footer>
    </main>
  );
}
