import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AOL — AI Optimization Layer",
  description:
    "Middleware that filters, contextualises, and routes the OEM AI assistant.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink-950 text-gray-100">{children}</body>
    </html>
  );
}
