import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Second Brain — the memory + routing layer for OEM AI",
  description:
    "Plugs into an OEM AI assistant. Persistent memory under Catch-Me-Up / Pay-Attention / Remember-This + per-call on-device-vs-cloud routing.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink-950 text-gray-100">{children}</body>
    </html>
  );
}
