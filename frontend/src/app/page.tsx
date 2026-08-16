import React from "react";
import { cookies } from "next/headers";
import Navbar from "@/components/landing/Navbar";
import HeroPlayground from "@/components/landing/HeroPlayground";
import FeatureBento from "@/components/landing/FeatureBento";
import ToolRegistryGrid from "@/components/landing/ToolRegistryGrid";
import SecurityShowcase from "@/components/landing/SecurityShowcase";
import PricingSection from "@/components/landing/PricingSection";
import FaqSection from "@/components/landing/FaqSection";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

export default async function Home() {
  const cookieStore = await cookies();
  const hasToken = cookieStore.has("access_token");
  const isPaid = cookieStore.get("is_paid")?.value === "true";

  return (
    <div className="min-h-screen bg-[#030303] text-zinc-100 font-sans selection:bg-lime-500/30 overflow-x-hidden">
      {/* Top Navbar */}
      <Navbar hasToken={hasToken} isPaid={isPaid} />

      {/* Hero with Interactive MCP Live Playground */}
      <HeroPlayground />

      {/* Feature Bento Grid */}
      <FeatureBento />

      {/* Architecture & Security Showcase */}
      <SecurityShowcase />

      {/* Tool Registry Grid */}
      <ToolRegistryGrid />

      {/* Pricing Section */}
      <PricingSection />

      {/* FAQ Section */}
      <FaqSection />

      {/* Bottom CTA Banner - Immersive layout */}
      <section className="w-full relative py-24 sm:py-32 border-t border-white/5 bg-gradient-to-b from-[#050505] to-[#0A0A0A]">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-lime-500/10 via-transparent to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-3xl mx-auto flex flex-col items-center px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-6">
            <Sparkles className="w-3.5 h-3.5" /> Instant 3-Minute Deployment
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Ready to automate your Odoo ERP with Claude?
          </h2>
          <p className="text-base sm:text-lg text-zinc-400 mb-10 max-w-2xl">
            Join leading enterprise teams connecting AI agents to production data with zero custom code.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto">
            {!hasToken ? (
              <Link
                href="/login"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-sm text-black bg-gradient-to-r from-lime-400 to-emerald-400 hover:scale-105 transition-transform shadow-[0_0_30px_rgba(163,230,53,0.3)]"
              >
                Get Started Free <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <Link
                href="/userdashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-sm text-black bg-gradient-to-r from-lime-400 to-emerald-400 hover:scale-105 transition-transform shadow-[0_0_30px_rgba(163,230,53,0.3)]"
              >
                Go to Dashboard <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full border-t border-white/5 bg-black py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="OdooX" className="h-6 w-auto opacity-70" />
            <span className="text-xs text-zinc-500 font-mono">© 2026 Recognate Inc.</span>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-zinc-400 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            All MCP Gateways Operational (XML-RPC 200 OK)
          </div>

          <div className="flex gap-6 text-xs sm:text-sm text-zinc-500">
            <Link href="#playground" className="hover:text-white transition-colors">Demo</Link>
            <Link href="#features" className="hover:text-white transition-colors">Features</Link>
            <Link href="#security" className="hover:text-white transition-colors">Security</Link>
            <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
          </div>
        </div>
      </footer>

      {/* AEO: JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "OdooX",
            "operatingSystem": "Web, Windows, macOS",
            "applicationCategory": "BusinessApplication",
            "description": "Enterprise Model Context Protocol Gateway connecting Claude AI to Odoo ERP.",
            "offers": {
              "@type": "Offer",
              "price": "49.00",
              "priceCurrency": "USD"
            }
          })
        }}
      />
    </div>
  );
}
