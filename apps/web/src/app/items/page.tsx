import ItemCard from "@/components/ItemCard";
import LiveRefresh from "@/components/LiveRefresh";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Items() {
  const data = await api.listItems({ limit: 100 });
  return (
    <div className="space-y-4">
      <LiveRefresh />
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">All items</h1>
        <span className="text-sm text-muted">{data.total} total</span>
      </header>
      {data.items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted">
          Empty. Add something from the home page.
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {data.items.map((it) => (
            <ItemCard key={it.id} item={it} />
          ))}
        </div>
      )}
    </div>
  );
}
