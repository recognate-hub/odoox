"use client";

import React from "react";
import { TrendingUp, Package, FileText, Target, Zap, ArrowRight, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function FeatureBento() {
  return (
    <section id="features" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 relative">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Zap className="w-3.5 h-3.5" /> Core Capabilities
        </span>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Enterprise power, zero friction.
        </h2>
        <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto">
          OdooX translates natural language into secure, validated XML-RPC transactions. Claude becomes an extension of your operations team.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-[280px] lg:auto-rows-[320px]">
        {/* Bento Box 1: Sales (Spans 2 columns on desktop) */}
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ duration: 0.2 }}
          className="lg:col-span-2 rounded-3xl border border-white/10 bg-zinc-900/60 p-8 flex flex-col justify-between overflow-hidden relative group"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-lime-500/10 blur-[80px] rounded-full pointer-events-none group-hover:bg-lime-500/20 transition-all duration-500" />
          
          <div className="relative z-10 max-w-md">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-lime-500 to-emerald-500 flex items-center justify-center mb-6 shadow-lg shadow-lime-500/20">
              <TrendingUp className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">Autonomous Sales & Pipeline</h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Claude evaluates lead potential, updates CRM stages, schedules follow-ups, and drafts quotes directly in Odoo without manual data entry.
            </p>
          </div>

          <div className="relative z-10 mt-6 flex items-center gap-2 text-xs font-mono text-lime-400">
            <span className="px-2 py-1 rounded bg-black border border-white/10">update_lead</span>
            <span className="px-2 py-1 rounded bg-black border border-white/10">create_sale_order</span>
          </div>
        </motion.div>

        {/* Bento Box 2: Inventory */}
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ duration: 0.2 }}
          className="rounded-3xl border border-white/10 bg-zinc-900/60 p-8 flex flex-col justify-between overflow-hidden relative group"
        >
          <div className="relative z-10">
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 text-zinc-400 group-hover:text-emerald-400 transition-colors">
              <Package className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Inventory Intelligence</h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Inspect stock levels, query product variants, and trigger reorder requests before stockouts occur.
            </p>
          </div>
          <div className="relative z-10 flex items-center gap-2 text-xs font-mono text-zinc-500">
            <span className="px-2 py-1 rounded bg-white/5 border border-white/10">get_products</span>
          </div>
        </motion.div>

        {/* Bento Box 3: Invoicing */}
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ duration: 0.2 }}
          className="rounded-3xl border border-white/10 bg-zinc-900/60 p-8 flex flex-col justify-between overflow-hidden relative group"
        >
          <div className="relative z-10">
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 text-zinc-400 group-hover:text-amber-400 transition-colors">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Accounting & Invoices</h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Draft and post customer invoices directly from confirmed sales orders via chat.
            </p>
          </div>
          <div className="relative z-10 flex items-center gap-2 text-xs font-mono text-zinc-500">
            <span className="px-2 py-1 rounded bg-white/5 border border-white/10">generate_invoice</span>
          </div>
        </motion.div>

        {/* Bento Box 4: Security (Spans 2 columns on desktop) */}
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ duration: 0.2 }}
          className="lg:col-span-2 rounded-3xl border border-white/10 bg-[#0C0C0C] p-8 flex flex-col justify-between overflow-hidden relative group"
        >
           <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-zinc-800/20 via-transparent to-transparent pointer-events-none" />

          <div className="relative z-10 flex items-start gap-6">
            <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 text-white">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white mb-3">Enterprise-Grade RBAC</h3>
              <p className="text-sm text-zinc-400 leading-relaxed max-w-md mb-6">
                Every request is validated against your Supabase JWT tenant context. Tool execution is strictly scoped by your configured RBAC policy (Admin, Rep, Viewer).
              </p>
              
              <div className="inline-flex items-center gap-2 text-xs font-mono text-zinc-500 bg-black px-3 py-2 rounded-lg border border-white/5">
                <span className="text-emerald-500">@secure_tool</span>
                <span>(required_role="sales_rep")</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
