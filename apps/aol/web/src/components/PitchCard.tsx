"use client";

/**
 * The 30-second pitch — read it off the screen if you have to.
 *
 * Three short sentences: problem, solution, result. Numbers are
 * calibrated to Lenovo-Motorola Q2 2025 shipments (14.5 M phones)
 * and the local-vs-cloud savings the demo backend produces.
 */
export function PitchCard() {
  return (
    <section className="rounded-2xl border border-emerald-400/30 bg-gradient-to-br from-emerald-400/5 via-ink-900 to-ink-900 p-5">
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">
          The 30-second pitch
        </h2>
        <span className="text-xs text-gray-500">read it out loud · this is the email · this is the interview answer</span>
      </div>

      <ol className="space-y-3 text-sm leading-relaxed text-gray-200">
        <li className="flex gap-3">
          <span className="shrink-0 rounded-full border border-rose-400/40 bg-rose-400/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-rose-300">
            Problem
          </span>
          <span>
            Phones ship with <span className="font-semibold text-gray-50">20-plus AI features</span> nobody asked for.
            Most are <span className="text-gray-50">slow</span>, drain <span className="text-gray-50">battery</span>,
            cost the OEM <span className="text-gray-50">cloud bills</span> — and{" "}
            <span className="text-gray-50">users disable them anyway</span>.
          </span>
        </li>

        <li className="flex gap-3">
          <span className="shrink-0 rounded-full border border-emerald-400/40 bg-emerald-400/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-300">
            Solution
          </span>
          <span>
            AOL is <span className="font-semibold text-gray-50">one drop-in layer</span> — about{" "}
            <span className="font-semibold text-gray-50">131 lines of Kotlin</span> the OEM AI assistant calls before it does anything.
            It <span className="text-gray-50">hides features the user doesn&rsquo;t use</span>, picks{" "}
            <span className="text-gray-50">on-device vs cloud</span> per call, and{" "}
            <span className="text-gray-50">remembers what the user disabled</span> so it doesn&rsquo;t come back.
          </span>
        </li>

        <li className="flex gap-3">
          <span className="shrink-0 rounded-full border border-amber-400/40 bg-amber-400/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-amber-300">
            Result
          </span>
          <span>
            ~<span className="font-semibold text-gray-50">45% of Moto AI calls land on-device</span>:{" "}
            <span className="text-gray-50">faster</span>, <span className="text-gray-50">free</span>,{" "}
            <span className="text-gray-50">private</span>. At Moto&rsquo;s{" "}
            <span className="text-gray-50">14.5 M phones / quarter</span> that&rsquo;s ~$<span className="font-semibold text-gray-50">1.6 M/year</span>{" "}
            in cloud bills saved <span className="text-gray-400">— before counting battery + churn.</span>
          </span>
        </li>
      </ol>

      <div className="mt-4 rounded-xl border border-ink-800 bg-ink-950/80 p-3 text-xs text-gray-400">
        <span className="font-semibold uppercase tracking-wider text-gray-300">The ask:</span>{" "}
        20 minutes with you to walk through the demo and the AIDL contract. Repo + APK ready, no slideware.
      </div>
    </section>
  );
}
