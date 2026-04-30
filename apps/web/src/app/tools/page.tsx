import { api } from "@/lib/api";
import LiveRefresh from "@/components/LiveRefresh";
import { Wrench } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function ToolsPage() {
  const tools = await api.tools();
  return (
    <div className="space-y-4">
      <LiveRefresh />
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Tool memory</h1>
        <span className="text-sm text-muted">
          {tools.length} tools / apps / websites
        </span>
      </header>
      {tools.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted">
          No tools extracted yet.
        </div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tools.map((t) => (
            <li
              key={t.id}
              className="rounded-xl border border-border bg-card p-3"
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-2 font-medium">
                  <Wrench className="size-4 text-accent" />
                  {t.name}
                </span>
                <span className="rounded-md bg-background px-1.5 py-0.5 text-xs text-muted">
                  {t.entity_type}
                </span>
              </div>
              {t.description && (
                <p className="line-clamp-2 text-xs text-muted">{t.description}</p>
              )}
              <p className="mt-1 text-xs text-muted">
                {t.mention_count} mention{t.mention_count === 1 ? "" : "s"}
              </p>
              {t.canonical_url && (
                <a
                  href={t.canonical_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-1 block truncate text-xs text-accent hover:underline"
                >
                  {t.canonical_url}
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
