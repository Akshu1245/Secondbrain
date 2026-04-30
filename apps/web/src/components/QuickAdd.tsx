"use client";

import { useState } from "react";
import { Send, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function QuickAdd({
  initialText,
  onSubmitted,
}: {
  initialText?: string;
  onSubmitted?: (id: number) => void;
}) {
  const router = useRouter();
  const [value, setValue] = useState(initialText ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text) return;
    setBusy(true);
    setError(null);
    try {
      const url = /^https?:\/\//i.test(text) ? text : undefined;
      const item = await api.ingest({ text: url ? undefined : text, url });
      setValue("");
      if (onSubmitted) onSubmitted(item.id);
      router.refresh();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-border bg-card shadow-sm focus-within:border-accent/60 focus-within:shadow"
    >
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Paste a Reel / YouTube / TikTok link, an article URL, or just a thought…"
        rows={3}
        className="w-full resize-none rounded-2xl bg-transparent p-4 outline-none placeholder:text-muted"
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === "Enter") submit(e);
        }}
      />
      <div className="flex items-center justify-between border-t border-border p-3">
        <span className="text-xs text-muted">⌘/Ctrl + Enter to save</span>
        <button
          type="submit"
          disabled={busy || !value.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white shadow-sm transition disabled:opacity-50 hover:opacity-90"
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
          Save
        </button>
      </div>
      {error && (
        <div className="border-t border-border p-3 text-xs text-red-500">{error}</div>
      )}
    </form>
  );
}
