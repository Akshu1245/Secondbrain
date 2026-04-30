// Typed API client for the Second Brain backend.
// Works on both the server (during RSC) and in the browser.

export type ItemKind = "reel" | "video" | "article" | "note" | "voice";
export type ItemStatus = "pending" | "processing" | "ready" | "failed";
export type EntityType =
  | "tool"
  | "app"
  | "website"
  | "book"
  | "person"
  | "place"
  | "concept";

export interface Tag {
  id: number;
  name: string;
}

export interface Entity {
  id: number;
  name: string;
  entity_type: EntityType;
  description?: string | null;
  canonical_url?: string | null;
  mention_count: number;
}

export interface Item {
  id: number;
  kind: ItemKind;
  source_url?: string | null;
  source_platform?: string | null;
  title?: string | null;
  author?: string | null;
  summary?: string | null;
  tldr?: string | null;
  raw_text?: string | null;
  media_path?: string | null;
  duration_sec?: number | null;
  status: ItemStatus;
  error?: string | null;
  created_at: string;
  updated_at: string;
  tags: Tag[];
  entities: Entity[];
}

export interface ItemList {
  items: Item[];
  total: number;
}

export interface SearchHit {
  item: Item;
  score: number;
  snippet: string | null;
}

export interface SearchResponse {
  query: string;
  hits: SearchHit[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: "item" | "entity" | "tag";
  meta?: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  kind: "mentions" | "tagged";
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const DEFAULT_BASE = "http://localhost:8000";

export function apiBase(): string {
  if (typeof window !== "undefined") {
    return (
      localStorage.getItem("sb_api_url") ||
      (window as unknown as { __SB_API__?: string }).__SB_API__ ||
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      DEFAULT_BASE
    );
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_BASE;
}

function authHeaders(): HeadersInit {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("sb_token") || ""
      : process.env.SECOND_BRAIN_API_TOKEN || "";
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(apiBase() + path, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => request<{ ok: boolean; version: string; llm: string }>("/api/health"),

  ingest: (body: { text?: string; url?: string; title?: string }) =>
    request<Item>("/api/ingest", { method: "POST", body: JSON.stringify(body) }),

  listItems: (params: Record<string, string | number | undefined> = {}) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params))
      if (v !== undefined && v !== "") q.set(k, String(v));
    const qs = q.toString();
    return request<ItemList>(`/api/items${qs ? `?${qs}` : ""}`);
  },

  getItem: (id: number) => request<Item>(`/api/items/${id}`),

  deleteItem: (id: number) =>
    request<{ ok: boolean }>(`/api/items/${id}`, { method: "DELETE" }),

  search: (q: string, mode: "hybrid" | "lexical" | "semantic" = "hybrid", k = 20) =>
    request<SearchResponse>(
      `/api/search?q=${encodeURIComponent(q)}&mode=${mode}&k=${k}`,
    ),

  tools: () => request<Entity[]>("/api/tools"),

  entities: (entity_type?: string) =>
    request<Entity[]>(
      `/api/entities${entity_type ? `?entity_type=${entity_type}` : ""}`,
    ),

  graph: (limit_items = 200) =>
    request<GraphResponse>(`/api/graph?limit_items=${limit_items}`),
};
