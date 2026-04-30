"use client";

// Web Share Target landing page. Manifest registers /share?url=...&text=...&title=...
// On submit we hand off to /api/ingest. We render a tiny "saving…" view so the
// share-sheet flow feels instant on mobile.

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import QuickAdd from "@/components/QuickAdd";

export const dynamic = "force-dynamic";

export default function SharePage() {
  return (
    <Suspense fallback={<p className="text-sm text-muted">Loading…</p>}>
      <ShareInner />
    </Suspense>
  );
}

function ShareInner() {
  const sp = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "saving" | "ok" | "error">("idle");
  const [err, setErr] = useState<string | null>(null);

  const url = sp.get("url") || sp.get("link") || "";
  const text = sp.get("text") || "";
  const title = sp.get("title") || "";

  const initial = [title, text, url].filter(Boolean).join("\n").trim();

  useEffect(() => {
    if (!initial) return;
    setStatus("saving");
    const lastWord = initial.split(/\s+/).at(-1) || "";
    const isUrl = /^https?:\/\//i.test(lastWord);
    const payload = isUrl
      ? {
          url: lastWord,
          title: title || undefined,
          text: text || undefined,
        }
      : { text: initial };
    api
      .ingest(payload)
      .then((it) => {
        setStatus("ok");
        setTimeout(() => router.push(`/items/${it.id}`), 800);
      })
      .catch((e) => {
        setErr((e as Error).message);
        setStatus("error");
      });
  }, [initial, router, text, title]);

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">
        Saving to your second brain…
      </h1>
      {initial && (
        <pre className="whitespace-pre-wrap rounded-xl border border-border bg-card p-4 text-sm">
          {initial}
        </pre>
      )}
      {status === "saving" && <p className="text-sm text-muted">Processing…</p>}
      {status === "ok" && (
        <p className="text-sm text-emerald-600">Saved. Redirecting…</p>
      )}
      {status === "error" && (
        <div className="space-y-3">
          <p className="text-sm text-red-500">{err}</p>
          <p className="text-sm text-muted">You can also paste it manually:</p>
          <QuickAdd initialText={initial} />
        </div>
      )}
      {!initial && (
        <p className="text-sm text-muted">
          This is the share-target endpoint. Share content into the app from your OS share sheet to land here.
        </p>
      )}
    </div>
  );
}
