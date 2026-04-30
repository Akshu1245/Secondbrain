"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiBase } from "@/lib/api";

/**
 * Subscribes to the backend SSE stream and triggers `router.refresh()` whenever
 * an item changes. Cheap real-time updates without rewriting the data layer.
 */
export default function LiveRefresh() {
  const router = useRouter();

  useEffect(() => {
    const token =
      (typeof window !== "undefined" && localStorage.getItem("sb_token")) || "";
    const url = new URL(apiBase() + "/api/events");
    if (token) url.searchParams.set("token", token);
    const es = new EventSource(url.toString());
    es.addEventListener("update", () => router.refresh());
    es.onerror = () => {
      // EventSource auto-reconnects; nothing to do.
    };
    return () => es.close();
  }, [router]);

  return null;
}
