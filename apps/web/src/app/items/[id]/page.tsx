import { api } from "@/lib/api";
import LiveRefresh from "@/components/LiveRefresh";
import { ExternalLink } from "lucide-react";
import { formatRelative, PLATFORM_LABEL } from "@/lib/utils";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function ItemPage(props: { params: Promise<{ id: string }> }) {
  const { id } = await props.params;
  const itemId = Number.parseInt(id, 10);
  if (!Number.isFinite(itemId)) notFound();

  let item;
  try {
    item = await api.getItem(itemId);
  } catch {
    notFound();
  }

  return (
    <article className="space-y-6">
      <LiveRefresh />
      <header className="space-y-2">
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
          <span className="rounded-md bg-card px-1.5 py-0.5">
            {PLATFORM_LABEL[item.source_platform || ""] || item.kind}
          </span>
          <span>{formatRelative(item.created_at)}</span>
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-accent hover:underline"
            >
              <ExternalLink className="size-3" />
              source
            </a>
          )}
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">{item.title || `Item #${item.id}`}</h1>
        {item.tldr && <p className="text-base text-muted">{item.tldr}</p>}
      </header>

      {item.status !== "ready" && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 text-sm text-amber-600">
          Status: <strong>{item.status}</strong>
          {item.error ? ` — ${item.error}` : ""}
        </div>
      )}

      {item.summary && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">
            Summary
          </h2>
          <pre className="whitespace-pre-wrap rounded-xl border border-border bg-card p-4 text-sm leading-relaxed">
            {item.summary}
          </pre>
        </section>
      )}

      {item.entities.length > 0 && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">
            Entities
          </h2>
          <ul className="grid gap-2 sm:grid-cols-2">
            {item.entities.map((e) => (
              <li
                key={e.id}
                className="rounded-lg border border-border bg-card p-2 text-sm"
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-medium">{e.name}</span>
                  <span className="text-xs text-muted">{e.entity_type}</span>
                </div>
                {e.canonical_url && (
                  <a
                    href={e.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-accent hover:underline"
                  >
                    {e.canonical_url}
                  </a>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {item.tags.length > 0 && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">
            Tags
          </h2>
          <div className="flex flex-wrap gap-2">
            {item.tags.map((t) => (
              <span
                key={t.id}
                className="rounded-md bg-accent/10 px-2 py-0.5 text-xs text-accent"
              >
                #{t.name}
              </span>
            ))}
          </div>
        </section>
      )}

      {item.raw_text && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">
            Full text
          </h2>
          <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap rounded-xl border border-border bg-card p-4 text-sm leading-relaxed">
            {item.raw_text}
          </pre>
        </section>
      )}
    </article>
  );
}
