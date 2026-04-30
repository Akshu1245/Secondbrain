"use client";

import Link from "next/link";
import { ExternalLink, Loader2, AlertTriangle } from "lucide-react";
import type { Item } from "@/lib/api";
import { formatRelative, PLATFORM_LABEL } from "@/lib/utils";

export default function ItemCard({ item }: { item: Item }) {
  return (
    <Link
      href={`/items/${item.id}`}
      className="block rounded-xl border border-border bg-card p-4 transition hover:border-accent/50 hover:shadow-sm"
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="line-clamp-2 font-medium leading-tight">
          {item.title || `Item #${item.id}`}
        </h3>
        <Status status={item.status} error={item.error} />
      </div>
      {item.tldr && (
        <p className="mb-2 line-clamp-2 text-sm text-muted">{item.tldr}</p>
      )}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-md bg-background px-1.5 py-0.5 text-muted">
          {PLATFORM_LABEL[item.source_platform || ""] || item.source_platform || "Note"}
        </span>
        {item.source_url && (
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-muted hover:text-accent"
          >
            <ExternalLink className="size-3" />
            source
          </a>
        )}
        {item.tags.slice(0, 4).map((t) => (
          <span key={t.id} className="rounded-md bg-accent/10 px-1.5 py-0.5 text-accent">
            #{t.name}
          </span>
        ))}
        {item.entities.length > 0 && (
          <span className="text-muted">{item.entities.length} entities</span>
        )}
        <span className="ml-auto text-muted">{formatRelative(item.created_at)}</span>
      </div>
    </Link>
  );
}

function Status({
  status,
  error,
}: {
  status: Item["status"];
  error?: string | null;
}) {
  if (status === "ready") return null;
  if (status === "failed")
    return (
      <span
        title={error || "failed"}
        className="inline-flex shrink-0 items-center gap-1 rounded-md bg-red-500/10 px-1.5 py-0.5 text-xs text-red-500"
      >
        <AlertTriangle className="size-3" />
        failed
      </span>
    );
  return (
    <span className="inline-flex shrink-0 items-center gap-1 rounded-md bg-amber-500/10 px-1.5 py-0.5 text-xs text-amber-600 dot-pending">
      <Loader2 className="size-3 animate-spin" />
      {status}
    </span>
  );
}
