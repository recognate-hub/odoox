"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Check, Sparkles, Zap } from "lucide-react";

export default function PricingSection() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("yearly");

  return (
    <section id="pricing" className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-24 relative">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Zap className="w-3.5 h-3.5" /> Simple Enterprise Pricing
        </span>
        <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
          Start Free. Scale Production Unlimited.
        </h2>
        <p className="text-zinc-400 text-lg mb-8">
          Deploy your Odoo MCP gateway in minutes. No credit card required to start testing.
        </p>

        {/* Toggle */}
        <div className="inline-flex items-center p-1 rounded-full bg-zinc-900 border border-white/10 text-xs font-medium text-zinc-400">
          <button
            onClick={() => setBillingCycle("monthly")}
            className={`px-4 py-2 rounded-full transition-all ${
              billingCycle === "monthly" ? "bg-white/10 text-white font-semibold" : "hover:text-white"
            }`}
          >
            Monthly Billing
          </button>
          <button
            onClick={() => setBillingCycle("yearly")}
            className={`px-4 py-2 rounded-full transition-all flex items-center gap-1.5 ${
              billingCycle === "yearly" ? "bg-lime-400 text-black font-bold shadow-md" : "hover:text-white"
            }`}
          >
            Yearly Billing <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/20 text-black uppercase">20% OFF</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Developer Tier */}
        <div className="rounded-3xl border border-white/10 bg-zinc-900/40 p-8 flex flex-col justify-between hover:border-white/20 transition-all">
          <div>
            <div className="text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Developer Free</div>
            <div className="text-4xl font-extrabold text-white mb-4">
              $0 <span className="text-sm font-normal text-zinc-500">/ forever</span>
            </div>
            <p className="text-zinc-400 text-sm mb-8 leading-relaxed">
              Ideal for developers testing Odoo MCP connections locally with Claude Desktop.
            </p>

            <div className="space-y-3.5 mb-8 text-sm text-zinc-300">
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Up to 1,000 MCP Tool Calls / mo</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>1 Odoo Instance Connection</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Core Sales & CRM MCP Tools</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Community Support</span>
              </div>
            </div>
          </div>

          <Link
            href="/login"
            className="w-full py-3.5 rounded-full text-center text-sm font-semibold text-white bg-white/10 hover:bg-white/15 transition-all border border-white/10"
          >
            Get Started Free
          </Link>
        </div>

        {/* Enterprise Pro Tier */}
        <div className="rounded-3xl border border-lime-500/40 bg-gradient-to-b from-zinc-900 via-zinc-950 to-zinc-900 p-8 flex flex-col justify-between relative shadow-[0_0_40px_rgba(163,230,53,0.15)]">
          <div className="absolute top-0 right-8 -translate-y-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-lime-400 to-emerald-400 text-black text-xs font-bold uppercase tracking-wider shadow-md">
            Most Popular
          </div>

          <div>
            <div className="text-xs font-mono text-lime-400 uppercase tracking-wider mb-2">Pro Gateway</div>
            <div className="text-4xl font-extrabold text-white mb-4">
              {billingCycle === "yearly" ? "$39" : "$49"}{" "}
              <span className="text-sm font-normal text-zinc-500">/ month</span>
            </div>
            <p className="text-zinc-400 text-sm mb-8 leading-relaxed">
              For teams deploying automated LLM production workflows into enterprise Odoo ERP environments.
            </p>

            <div className="space-y-3.5 mb-8 text-sm text-zinc-200">
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span className="font-semibold text-white">Unlimited MCP Tool Executions</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Unlimited Odoo Instance Connections</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Full Catalog of 12+ MCP Tools</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Custom Fine-Grained RBAC & Webhooks</span>
              </div>
              <div className="flex items-center gap-3">
                <Check className="w-4 h-4 text-lime-400 shrink-0" />
                <span>Priority 24/7 SLA Engineering Support</span>
              </div>
            </div>
          </div>

          <Link
            href="/login"
            className="w-full py-3.5 rounded-full text-center text-sm font-bold text-black bg-gradient-to-r from-lime-400 to-emerald-400 hover:opacity-95 transition-all shadow-[0_0_20px_rgba(163,230,53,0.4)]"
          >
            Upgrade to Pro Gateway
          </Link>
        </div>
      </div>
    </section>
  );
}
