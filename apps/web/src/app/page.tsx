import QuickAdd from "@/components/QuickAdd";
import ItemCard from "@/components/ItemCard";
import LiveRefresh from "@/components/LiveRefresh";
import { api } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function Home() {
  let items: Awaited<ReturnType<typeof api.listItems>> | null = null;
  let apiError: string | null = null;
  try {
    items = await api.listItems({ limit: 12 });
  } catch (e) {
    apiError = (e as Error).message;
  }

  return (
    <div className="space-y-8">
      <LiveRefresh />
      <section className="space-y-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Quick add</h1>
          <p className="text-sm text-muted">
            Drop a link or a thought. We&apos;ll fetch it, transcribe it, summarise
            it, and pull out every tool/app/book mentioned.
          </p>
        </div>
        <QuickAdd />
      </section>

      {apiError ? (
        <div className="rounded-xl border border-red-500/40 bg-red-500/5 p-4 text-sm text-red-500">
          <p className="font-medium">Couldn&apos;t reach the API.</p>
          <p className="mt-1 text-red-500/80">{apiError}</p>
          <p className="mt-2 text-muted">
            Set <code className="font-mono">NEXT_PUBLIC_API_BASE_URL</code> on
            Vercel and (optionally) save your API token via the browser console:{" "}
            <code className="font-mono">localStorage.sb_token = &quot;…&quot;</code>.
          </p>
        </div>
      ) : (
        <section className="space-y-3">
          <div className="flex items-baseline justify-between">
            <h2 className="text-lg font-semibold tracking-tight">Recent</h2>
            <Link href="/items" className="text-sm text-accent hover:underline">
              all items →
            </Link>
          </div>
          {items && items.items.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2">
              {items.items.map((it) => (
                <ItemCard key={it.id} item={it} />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted">
              Nothing here yet. Paste a Reel link above to start.
            </div>
          )}
        </section>
      )}
    </div>
  );
}
