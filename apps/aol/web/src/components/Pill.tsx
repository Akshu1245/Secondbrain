import type { ReactNode } from "react";

const tone = {
  light:  "bg-emerald-500/15 text-emerald-300 border-emerald-500/40",
  medium: "bg-sky-500/15    text-sky-300    border-sky-500/40",
  heavy:  "bg-rose-500/15   text-rose-300   border-rose-500/40",
  on:     "bg-emerald-500/15 text-emerald-300 border-emerald-500/40",
  off:    "bg-zinc-500/15   text-zinc-300   border-zinc-500/30",
  cloud:  "bg-violet-500/15 text-violet-300 border-violet-500/40",
  local:  "bg-amber-500/15   text-amber-300   border-amber-500/40",
} as const;

export function Pill({
  children,
  tone: t = "off",
}: {
  children: ReactNode;
  tone?: keyof typeof tone;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${tone[t]}`}
    >
      {children}
    </span>
  );
}
