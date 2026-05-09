"use client";

import { useState } from "react";

const STEP_2_CODE = `// In your Application or main activity, once.
val aol = AolClient(context).also { it.bind() }`;

const STEP_3_CODE = `// Before EVERY AI call the OEM assistant makes:
val visible = aol.filterSurface(allFeatures, prefs, ctx)

// When the user taps a feature:
val route = aol.routeCompute(featureId, payloadKb, prefs)
//          ^^^^^^^ \"local\" or \"cloud\" — your existing code dispatches as before.

// After the feature finishes:
aol.recordOutcome(featureId, latencyMs, success)`;

/**
 * Concrete how-to-integrate card. Anyone reading this should be able to
 * copy-paste straight into an OEM AI assistant module and have it work.
 */
export function IntegrateCard() {
  return (
    <section className="rounded-2xl border border-ink-800 bg-ink-900/80 p-5">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400/80">
          Integrate it — three steps, ~131 lines
        </h2>
        <span className="text-xs text-gray-500">
          The whole drop-in. No deck, no SDK, no licence dance.
        </span>
      </div>

      <ol className="space-y-4">
        <Step
          n={1}
          title="Drop two files into the OEM assistant module"
          body={
            <>
              <p className="text-sm text-gray-300">
                Both files are shipped in the public repo and are the only thing
                an OEM engineer needs to copy.
              </p>
              <ul className="mt-2 space-y-1 text-xs text-gray-400">
                <li>
                  <FileChip path="docs/oem-pitch/integration/IAolMiddleware.aidl" loc={38} />
                  <span className="ml-2">— the Binder contract: 3 RPCs (filter / route / record).</span>
                </li>
                <li>
                  <FileChip path="docs/oem-pitch/integration/AolClient.kt" loc={93} />
                  <span className="ml-2">— Kotlin client that binds to the service + falls back gracefully.</span>
                </li>
              </ul>
              <p className="mt-2 text-xs text-gray-500">
                That&rsquo;s the entire ~131 LOC drop-in. Verifiable: <code className="rounded bg-ink-950 px-1.5 py-0.5 text-emerald-300">scripts/verify-loc.sh</code>.
              </p>
            </>
          }
        />

        <Step
          n={2}
          title="Bind once when the OEM assistant starts"
          body={<CodeBlock code={STEP_2_CODE} />}
        />

        <Step
          n={3}
          title="Wrap every AI call (3 call sites total)"
          body={
            <>
              <CodeBlock code={STEP_3_CODE} />
              <p className="mt-2 text-xs text-gray-500">
                If Second Brain is not installed or crashes, every call returns the
                unfiltered list + a &ldquo;cloud&rdquo; route — the OEM
                assistant keeps working exactly as today.
              </p>
            </>
          }
        />

        <Step
          n={4}
          title="Verify locally (5 min)"
          body={
            <>
              <CodeBlock
                code={`# clone, build, install on any phone or emulator
git clone https://github.com/Akshu1245/Secondbrain.git
cd Secondbrain/apps/aol-android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk`}
              />
              <p className="mt-2 text-xs text-gray-500">
                Output APK is ~9.5 MB. The Compose UI shows the same six modules this dashboard demos.
              </p>
            </>
          }
        />
      </ol>

      <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <a
          href="https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/integration/AolClient.kt"
          target="_blank"
          rel="noreferrer"
          className="rounded-lg border border-emerald-400/40 bg-emerald-400/10 px-3 py-2 text-center text-sm text-emerald-200 hover:bg-emerald-400/20"
        >
          Read AolClient.kt →
        </a>
        <a
          href="https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/integration/IAolMiddleware.aidl"
          target="_blank"
          rel="noreferrer"
          className="rounded-lg border border-emerald-400/40 bg-emerald-400/10 px-3 py-2 text-center text-sm text-emerald-200 hover:bg-emerald-400/20"
        >
          Read IAolMiddleware.aidl →
        </a>
        <a
          href="https://github.com/Akshu1245/Secondbrain/blob/main/docs/oem-pitch/integration/README.md"
          target="_blank"
          rel="noreferrer"
          className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-2 text-center text-sm text-gray-200 hover:border-emerald-400/40"
        >
          Full integration guide →
        </a>
      </div>
    </section>
  );
}

function Step({
  n,
  title,
  body,
}: {
  n: number;
  title: string;
  body: React.ReactNode;
}) {
  return (
    <li className="flex gap-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-emerald-400/50 bg-emerald-400/10 text-xs font-bold text-emerald-300">
        {n}
      </span>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-semibold text-gray-100">{title}</div>
        <div className="mt-1.5">{body}</div>
      </div>
    </li>
  );
}

function FileChip({ path, loc }: { path: string; loc: number }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <code className="rounded bg-ink-950 px-1.5 py-0.5 text-[11px] text-emerald-300">{path}</code>
      <span className="rounded-full border border-ink-700 px-1.5 py-0.5 text-[10px] text-gray-400">
        {loc} LOC
      </span>
    </span>
  );
}

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="relative">
      <pre className="overflow-x-auto rounded-lg border border-ink-800 bg-ink-950 p-3 text-xs leading-relaxed text-gray-200">
        <code>{code}</code>
      </pre>
      <button
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          } catch {
            /* clipboard might not be available on insecure contexts */
          }
        }}
        className="absolute right-2 top-2 rounded border border-ink-700 bg-ink-900 px-2 py-0.5 text-[10px] uppercase tracking-wider text-gray-300 hover:border-emerald-400/50 hover:text-emerald-300"
      >
        {copied ? "copied" : "copy"}
      </button>
    </div>
  );
}
