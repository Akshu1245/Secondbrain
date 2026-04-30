import { api } from "@/lib/api";
import GraphView from "@/components/GraphView";

export const dynamic = "force-dynamic";

export default async function GraphPage() {
  const data = await api.graph(200);
  return (
    <div className="space-y-4">
      <header className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Knowledge graph</h1>
        <span className="text-sm text-muted">
          {data.nodes.length} nodes · {data.edges.length} edges
        </span>
      </header>
      {data.nodes.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted">
          The graph fills in as items are processed.
        </div>
      ) : (
        <GraphView data={data} />
      )}
    </div>
  );
}
