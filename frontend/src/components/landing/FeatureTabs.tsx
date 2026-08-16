"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, Package, FileText, Lock, CheckCircle2, Zap } from "lucide-react";

const FEATURES = [
  {
    id: "crm",
    title: "Sales & Pipeline Agency",
    icon: TrendingUp,
    badge: "CRM & Sales",
    headline: "Transform static leads into closing deals autonomously.",
    description: "Claude evaluates lead potential, updates stages, schedules follow-up calls, and drafts quotes directly in Odoo without manual data entry.",
    highlights: [
      "Auto-qualify incoming opportunities based on revenue signals",
      "Update lead stages and probabilities in real-time",
      "Draft Odoo Sales Orders directly from conversation threads",
      "Query win/loss ratios and historical deal timelines"
    ],
    codeSnippet: `// Sales Pipeline Tool Call
const result = await mcp.callTool("update_lead", {
  lead_id: 145,
  stage_id: 3, // Moved to 'Qualified'
  probability: 95
});`
  },
  {
    id: "operations",
    title: "Inventory & Logistics",
    icon: Package,
    badge: "Inventory & Warehouse",
    headline: "Instant stock intelligence & replenishment triggers.",
    description: "Inspect warehouse stock levels, query product variants, predict stockouts, and trigger manufacturing or purchase orders instantly.",
    highlights: [
      "Filter low-stock products by location or custom domains",
      "Inspect manufacturing orders and Bill of Materials (BOM)",
      "Trigger automated reorder requests before stockouts occur",
      "Full XML-RPC support for stock.quant and product.template"
    ],
    codeSnippet: `// Inventory Search Tool Call
const stock = await mcp.callTool("get_products", {
  domain: [["qty_available", "<", 10]],
  fields: ["name", "qty_available", "reorder_min"]
});`
  },
  {
    id: "financials",
    title: "Invoicing & Accounting",
    icon: FileText,
    badge: "Accounting",
    headline: "Automate invoice generation and reconciliation summaries.",
    description: "Allow your AI agents to query draft invoices, verify payment statuses via integrated Razorpay webhooks, and summarize revenue metrics.",
    highlights: [
      "Fetch draft and posted customer invoices",
      "Generate new invoices automatically from confirmed sales orders",
      "Verify subscription payment statuses in real-time",
      "Executive financial dashboards in natural language"
    ],
    codeSnippet: `// Financial Metrics Tool Call
const dashboard = await mcp.callTool("get_sales_dashboard", {
  timeframe: "this_quarter",
  include_unpaid_invoices: true
});`
  },
  {
    id: "security",
    title: "Granular RBAC & Security",
    icon: Lock,
    badge: "Enterprise Security",
    headline: "Bank-grade policy enforcement on every tool invocation.",
    description: "Every request is validated against your Supabase JWT tenant context. Tool execution is strictly scoped by your configured RBAC policy.",
    highlights: [
      "Role-Based Access Control (Admin, Sales Rep, Viewer)",
      "Input schema validation & prompt injection blacklisting",
      "Full audit trail for every tool call executed by Claude",
      "Zero plain-text password storage; Fernet encrypted secrets"
    ],
    codeSnippet: `// RBAC Policy Enforcement
@secure_tool(required_role="sales_rep")
async function update_lead(context: TenantContext, params: LeadSchema) {
  // Executed within tenant-isolated XML-RPC session
}`
  }
];

export default function FeatureTabs() {
  const [activeTab, setActiveTab] = useState<string>("crm");
  const current = FEATURES.find((f) => f.id === activeTab) || FEATURES[0];

  return (
    <section id="features" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 relative">
      <div className="text-center max-w-3xl mx-auto mb-14">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Zap className="w-3.5 h-3.5" /> Native MCP Pillars
        </span>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-4">
          Built for Enterprise Performance & Scale
        </h2>
        <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto">
          Unleash the full power of your ERP. OdooX equips AI agents with direct, secure, and instant operational tools.
        </p>
      </div>

      {/* Feature Navigation Pills */}
      <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
        {FEATURES.map((feature) => {
          const Icon = feature.icon;
          const isActive = activeTab === feature.id;
          return (
            <button
              key={feature.id}
              onClick={() => setActiveTab(feature.id)}
              className={`flex items-center gap-2.5 px-5 py-2.5 rounded-full text-xs sm:text-sm font-semibold transition-all ${
                isActive
                  ? "bg-gradient-to-r from-lime-400 to-emerald-400 text-black shadow-[0_0_20px_rgba(163,230,53,0.3)] scale-105"
                  : "bg-zinc-900/80 border border-white/10 text-zinc-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-black" : "text-lime-400"}`} />
              {feature.title}
            </button>
          );
        })}
      </div>

      {/* Active Feature Display Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={current.id}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -15 }}
          transition={{ duration: 0.3 }}
          className="rounded-3xl border border-white/10 bg-gradient-to-b from-zinc-900/80 to-zinc-950/90 p-6 sm:p-10 lg:p-12 backdrop-blur-xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-96 h-96 bg-lime-500/5 blur-[120px] rounded-full pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            {/* Left Content */}
            <div className="lg:col-span-7">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-6">
                <Zap className="w-3.5 h-3.5" /> {current.badge}
              </span>

              <h3 className="text-2xl sm:text-4xl font-bold text-white mb-4 leading-tight">
                {current.headline}
              </h3>

              <p className="text-zinc-400 text-sm sm:text-base mb-8 leading-relaxed">
                {current.description}
              </p>

              <div className="space-y-3">
                {current.highlights.map((point, index) => (
                  <div key={index} className="flex items-start gap-3 text-xs sm:text-sm text-zinc-300">
                    <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-lime-400 shrink-0 mt-0.5" />
                    <span>{point}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Code Display */}
            <div className="lg:col-span-5">
              <div className="rounded-2xl border border-white/10 bg-black/90 p-5 sm:p-6 font-mono text-xs text-lime-300 shadow-2xl relative">
                <div className="flex items-center justify-between text-zinc-500 text-[11px] pb-3 mb-4 border-b border-white/10">
                  <span>{current.id}_mcp_tool.ts</span>
                  <span className="text-lime-400">TypeScript / Python</span>
                </div>
                <pre className="overflow-x-auto leading-relaxed text-zinc-300 text-xs">
                  <code>{current.codeSnippet}</code>
                </pre>
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
