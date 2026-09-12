import React from "react";
import {
  ShieldAlert,
  CalendarClock,
  TrendingUp,
  CreditCard,
  FileSearch,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col justify-between">
      {/* Navbar */}
      <header className="border-b border-border/50 bg-background/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold">
              🛡️
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Bill<span className="text-primary">Guard</span>
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              Sprint 1: Architecture Ready
            </span>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-sm text-muted-foreground hover:text-white transition"
            >
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 flex-1 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          AI-Powered Financial Guardian
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-3xl leading-tight">
          Never Miss a Bill. Never Pay an Unnoticed Price Hike.
        </h1>

        <p className="mt-6 text-lg text-muted-foreground max-w-2xl">
          BillGuard continuously monitors your recurring subscriptions, utility bills,
          and expenses. Ingest receipts via Gemini Vision, detect abnormal spikes, and receive
          smart deadline alerts before late fees hit.
        </p>

        {/* Dashboard Preview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mt-16 text-left">
          <div className="p-6 rounded-xl border border-border bg-card/60 shadow-lg">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center mb-4">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Multimodal Bill OCR</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Upload invoices in PDF or image format. Gemini Flash automatically extracts biller name, amount, and due dates.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-border bg-card/60 shadow-lg">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center mb-4">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Spike & Anomaly Detector</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Flags sudden rate hikes on utility bills and silent renewal fee jumps before the charges execute.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-border bg-card/60 shadow-lg">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
              <CalendarClock className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Automated Alerts</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Scheduled background reminders delivered 7 days, 3 days, and 1 day prior via email and Telegram bot.
            </p>
          </div>
        </div>

        {/* System Status Tracker */}
        <div className="w-full max-w-5xl mt-12 p-6 rounded-xl border border-border bg-card/30 text-left">
          <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">
            Architecture & Foundation Status (Lead: Lena Noby)
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>PostgreSQL Models</span>
            </div>
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>FastAPI App & CORS</span>
            </div>
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>OpenAPI Contract Spec</span>
            </div>
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>Next.js 14 Scaffolding</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-6 text-center text-xs text-muted-foreground">
        © 2026 BillGuard Team • Built with Next.js 14, FastAPI & Google Gemini
      </footer>
    </main>
  );
}
