"use client";

import { useState } from "react";

const SUBJECT = "AOL — one drop-in layer that hides the AI features users never open";

const BODY = `Hey,

Saw this and thought of you — Akshay built a working OEM-side
"AI optimisation layer" that hides the AI features users never open,
runs the rest on-device when it can, and remembers what the user
disabled so it doesn't come back.

Live demo + 30-second pitch:
https://out-gwumfbso.devinapps.com/

Repo + buildable Android APK + the 131-line drop-in:
https://github.com/Akshu1245/Secondbrain

Why it matters: ~45% of Moto AI calls land on-device after AOL runs in
front of them. At Moto's 14.5 M phones / quarter that's roughly
$1.6 M/year in cloud bills saved — before counting battery and churn.
Same architecture works for Galaxy AI / OnePlus / Nothing.

If you know someone on the OEM assistant team (Lenovo MBG, Samsung
Mobile, etc.) it'd be a 20-minute call worth taking.

— forwarded by`;

/**
 * Pre-filled "forward this to someone" card. The whole point: anyone
 * looking at the page should be able to send it onward in 5 seconds
 * without writing a sentence themselves.
 */
export function ForwardCard() {
  const [copied, setCopied] = useState<string | null>(null);

  async function copy(label: string, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);
      setTimeout(() => setCopied(null), 1500);
    } catch {
      /* ignore */
    }
  }

  const mailtoHref = `mailto:?subject=${encodeURIComponent(SUBJECT)}&body=${encodeURIComponent(BODY)}`;
  const linkedInHref = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent("https://out-gwumfbso.devinapps.com/")}`;
  const xHref = `https://twitter.com/intent/tweet?text=${encodeURIComponent("AOL — a drop-in layer that hides the AI features phone users never open, and runs the rest on-device. Working demo + APK:")}&url=${encodeURIComponent("https://out-gwumfbso.devinapps.com/")}`;

  return (
    <section className="rounded-2xl border border-sky-500/30 bg-gradient-to-br from-sky-500/5 via-ink-900 to-ink-900 p-5">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-400/80">
          Forward this to someone
        </h2>
        <span className="text-xs text-gray-500">
          Pre-filled subject + body. Click → copy → paste → send.
        </span>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500">Subject</div>
          <div className="mt-1 flex items-center gap-2">
            <code className="flex-1 truncate rounded-lg border border-ink-800 bg-ink-950 px-3 py-2 text-xs text-gray-100">
              {SUBJECT}
            </code>
            <button
              onClick={() => copy("subject", SUBJECT)}
              className="rounded border border-ink-700 bg-ink-900 px-2 py-1 text-[10px] uppercase tracking-wider text-gray-300 hover:border-sky-400/50 hover:text-sky-300"
            >
              {copied === "subject" ? "copied" : "copy"}
            </button>
          </div>
        </div>

        <div className="flex items-end gap-2">
          <a
            href={mailtoHref}
            className="rounded-lg border border-sky-400/50 bg-sky-400/10 px-3 py-2 text-sm text-sky-200 hover:bg-sky-400/20"
          >
            Open in mail client →
          </a>
          <a
            href={linkedInHref}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-2 text-sm text-gray-200 hover:border-sky-400/40"
          >
            LinkedIn
          </a>
          <a
            href={xHref}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-ink-700 bg-ink-900 px-3 py-2 text-sm text-gray-200 hover:border-sky-400/40"
          >
            X
          </a>
        </div>
      </div>

      <div className="mt-3">
        <div className="flex items-center justify-between">
          <div className="text-xs uppercase tracking-wider text-gray-500">Body</div>
          <button
            onClick={() => copy("body", BODY)}
            className="rounded border border-ink-700 bg-ink-900 px-2 py-1 text-[10px] uppercase tracking-wider text-gray-300 hover:border-sky-400/50 hover:text-sky-300"
          >
            {copied === "body" ? "copied" : "copy body"}
          </button>
        </div>
        <pre className="mt-1 overflow-x-auto rounded-lg border border-ink-800 bg-ink-950 p-3 text-xs leading-relaxed text-gray-200 whitespace-pre-wrap">
{BODY}
        </pre>
      </div>
    </section>
  );
}
