"use client";

import { useEffect, useState } from "react";
import { Search as SearchIcon, Loader2 } from "lucide-react";
import { api, type SearchResponse } from "@/lib/api";
import ItemCard from "@/components/ItemCard";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [mode, setMode] = useState<"hybrid" | "lexical" | "semantic">("hybrid");
  const [busy, setBusy] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!q.trim()) {
      setData(null);
      return;
    }
    const t = setTimeout(async () => {
      setBusy(true);
      setErr(null);
      try {
        setData(await api.search(q, mode));
      } catch (e) {
        setErr((e as Error).message);
      } finally {
        setBusy(false);
      }
    }, 250);
    return () => clearTimeout(t);
  }, [q, mode]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Search</h1>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search by meaning or keywords…"
            className="w-full rounded-lg border border-border bg-card py-2 pl-9 pr-3 outline-none focus:border-accent/60"
            autoFocus
          />
        </div>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value as typeof mode)}
          className="rounded-lg border border-border bg-card px-3 py-2 text-sm"
        >
          <option value="hybrid">Hybrid</option>
          <option value="lexical">Lexical (keywords)</option>
          <option value="semantic">Semantic (meaning)</option>
        </select>
      </div>

      {err && <div className="text-sm text-red-500">{err}</div>}
      {busy && (
        <div className="flex items-center gap-2 text-sm text-muted">
          <Loader2 className="size-4 animate-spin" />
          searching…
        </div>
      )}

      {data && data.hits.length > 0 ? (
        <ul className="space-y-3">
          {data.hits.map((h) => (
            <li key={h.item.id} className="space-y-1">
              <ItemCard item={h.item} />
              {h.snippet && (
                <p
                  className="px-1 text-xs text-muted"
                  dangerouslySetInnerHTML={{ __html: h.snippet }}
                />
              )}
            </li>
          ))}
        </ul>
      ) : data && q.trim() ? (
        <p className="text-sm text-muted">No results.</p>
      ) : null}
    </div>
  );
}
