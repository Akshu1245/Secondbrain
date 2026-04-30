import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { Brain, Search, Wrench, Network, Plus, Settings as SettingsIcon } from "lucide-react";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Second Brain",
  description:
    "Capture Instagram Reels, articles, voice memos and notes — AI summarises, extracts tools, and makes it all searchable by meaning.",
  applicationName: "Second Brain",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "Second Brain" },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fafafa" },
    { media: "(prefers-color-scheme: dark)", color: "#08080c" },
  ],
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="mx-auto flex h-14 max-w-5xl items-center gap-4 px-4">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <Brain className="size-5 text-accent" />
              <span>Second Brain</span>
            </Link>
            <nav className="ml-auto flex items-center gap-1 text-sm">
              <NavLink href="/" icon={<Plus className="size-4" />}>Add</NavLink>
              <NavLink href="/search" icon={<Search className="size-4" />}>Search</NavLink>
              <NavLink href="/tools" icon={<Wrench className="size-4" />}>Tools</NavLink>
              <NavLink href="/graph" icon={<Network className="size-4" />}>Graph</NavLink>
              <NavLink href="/settings" icon={<SettingsIcon className="size-4" />}>Settings</NavLink>
            </nav>
          </div>
        </header>
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">{children}</main>
        <footer className="border-t border-border py-4 text-center text-xs text-muted">
          <span>Second Brain — open-source, AGPL-3.0</span>
        </footer>
      </body>
    </html>
  );
}

function NavLink({
  href,
  icon,
  children,
}: {
  href: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-foreground/80 hover:bg-card hover:text-foreground transition-colors"
    >
      {icon}
      <span className="hidden sm:inline">{children}</span>
    </Link>
  );
}
