"use client";

import { useEffect, useState } from "react";
import { Save, Check } from "lucide-react";
import { api } from "@/lib/api";

export default function Settings() {
  const [apiUrl, setApiUrl] = useState("");
  const [token, setToken] = useState("");
  const [saved, setSaved] = useState(false);
  const [health, setHealth] = useState<{ ok: boolean; version: string; llm: string } | null>(null);
  const [healthErr, setHealthErr] = useState<string | null>(null);

  useEffect(() => {
    setApiUrl(localStorage.getItem("sb_api_url") || process.env.NEXT_PUBLIC_API_BASE_URL || "");
    setToken(localStorage.getItem("sb_token") || "");
  }, []);

  async function check() {
    setHealth(null);
    setHealthErr(null);
    try {
      setHealth(await api.health());
    } catch (e) {
      setHealthErr((e as Error).message);
    }
  }

  function save() {
    if (apiUrl) {
      localStorage.setItem("sb_api_url", apiUrl);
      (window as unknown as { __SB_API__?: string }).__SB_API__ = apiUrl;
    } else {
      localStorage.removeItem("sb_api_url");
    }
    if (token) localStorage.setItem("sb_token", token);
    else localStorage.removeItem("sb_token");
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>

      <section className="space-y-2">
        <label className="block text-sm font-medium">API base URL</label>
        <input
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="https://second-brain-api.onrender.com"
          className="w-full rounded-lg border border-border bg-card px-3 py-2 outline-none focus:border-accent/60"
        />
        <p className="text-xs text-muted">
          Defaults to <code className="font-mono">NEXT_PUBLIC_API_BASE_URL</code> from
          your Vercel environment.
        </p>
      </section>

      <section className="space-y-2">
        <label className="block text-sm font-medium">API token</label>
        <input
          value={token}
          onChange={(e) => setToken(e.target.value)}
          type="password"
          placeholder="leave blank if backend is in open mode"
          className="w-full rounded-lg border border-border bg-card px-3 py-2 outline-none focus:border-accent/60"
        />
      </section>

      <div className="flex items-center gap-3">
        <button
          onClick={save}
          className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white"
        >
          {saved ? <Check className="size-4" /> : <Save className="size-4" />}
          {saved ? "Saved" : "Save"}
        </button>
        <button
          onClick={check}
          className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-card"
        >
          Test connection
        </button>
      </div>

      {health && (
        <pre className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-3 text-xs text-emerald-700 dark:text-emerald-400">
          {JSON.stringify(health, null, 2)}
        </pre>
      )}
      {healthErr && (
        <p className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-xs text-red-500">
          {healthErr}
        </p>
      )}
    </div>
  );
}
