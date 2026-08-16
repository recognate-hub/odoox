"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Wrench, Shield, ChevronRight, Code2 } from "lucide-react";

interface MCPTool {
  name: string;
  odooModel: string;
  role: string;
  description: string;
  sampleCall: string;
}

const MCP_TOOLS: MCPTool[] = [
  {
    name: "create_lead",
    odooModel: "crm.lead",
    role: "sales_rep",
    description: "Creates a new opportunity or lead record in Odoo CRM with custom fields and contact tagging.",
    sampleCall: `create_lead({ name: "Acme Corp Deal", email: "contact@acme.com", expected_revenue: 50000 })`
  },
  {
    name: "update_lead",
    odooModel: "crm.lead",
    role: "sales_rep",
    description: "Updates probability, stage, expected closing date, or status notes on existing opportunities.",
    sampleCall: `update_lead({ lead_id: 142, stage_id: 2, probability: 95 })`
  },
  {
    name: "get_leads",
    odooModel: "crm.lead",
    role: "viewer",
    description: "Queries CRM records using standard Odoo domain filters (e.g. stage, expected revenue, sales rep).",
    sampleCall: `get_leads({ domain: [["probability", ">=", 80]], limit: 10 })`
  },
  {
    name: "get_products",
    odooModel: "product.template",
    role: "viewer",
    description: "Fetches product catalog items, stock on hand, standard pricing, and variant attributes.",
    sampleCall: `get_products({ domain: [["qty_available", "<", 10]], fields: ["name", "qty_available"] })`
  },
  {
    name: "schedule_meeting",
    odooModel: "calendar.event",
    role: "sales_rep",
    description: "Books events directly into Odoo Calendar and dispatches attendee email invitations.",
    sampleCall: `schedule_meeting({ name: "Demo Call", start: "2026-08-17 14:00:00", stop: "2026-08-17 14:30:00" })`
  },
  {
    name: "get_sales_dashboard",
    odooModel: "sale.order",
    role: "admin",
    description: "Generates high-level revenue summaries, quote counts, win rates, and top performing sales reps.",
    sampleCall: `get_sales_dashboard({ timeframe: "this_month", include_pipeline: true })`
  },
  {
    name: "generate_invoice",
    odooModel: "account.move",
    role: "admin",
    description: "Drafts and posts customer invoices directly from confirmed sales orders or custom line items.",
    sampleCall: `generate_invoice({ partner_id: 42, lines: [{ name: "SaaS License", price: 99.00 }] })`
  },
  {
    name: "list_customers",
    odooModel: "res.partner",
    role: "viewer",
    description: "Searches customer database by commercial entity name, email address, VAT number, or phone.",
    sampleCall: `list_customers({ name_filter: "Globex", limit: 5 })`
  }
];

export default function ToolRegistryGrid() {
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null);

  return (
    <section id="tools" className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32 relative">
      <div className="text-center mb-16">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Wrench className="w-3.5 h-3.5" /> Complete Tool Catalog
        </span>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-4">
          12+ Native MCP Tools
        </h2>
        <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto">
          Expose every core Odoo workflow to Claude with strong typing, Pydantic validation, and fine-grained RBAC.
        </p>
      </div>

      <div className="border-t border-white/10 divide-y divide-white/5">
        {MCP_TOOLS.map((tool) => (
          <motion.div
            key={tool.name}
            onClick={() => setSelectedTool(tool)}
            className="group cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between py-5 hover:bg-white/[0.02] transition-colors -mx-4 px-4 rounded-xl"
          >
            <div className="flex-1 pr-6 mb-4 sm:mb-0">
              <div className="flex items-center gap-3 mb-1.5">
                <span className="font-mono text-base font-semibold text-lime-400">
                  {tool.name}
                </span>
                <span className="px-2 py-0.5 rounded bg-zinc-800 text-[10px] font-mono text-zinc-400 uppercase tracking-wider">
                  {tool.odooModel}
                </span>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed max-w-2xl">
                {tool.description}
              </p>
            </div>

            <div className="flex items-center gap-6 shrink-0">
              <span className="flex items-center gap-1.5 text-xs font-mono text-emerald-400/80 bg-emerald-950/30 px-2.5 py-1 rounded border border-emerald-500/20">
                <Shield className="w-3 h-3" /> {tool.role}
              </span>
              <ChevronRight className="w-5 h-5 text-zinc-600 group-hover:text-lime-400 transition-colors" />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Tool Detail Modal */}
      <AnimatePresence>
        {selectedTool && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-xl rounded-3xl border border-lime-500/30 bg-zinc-950 p-6 sm:p-8 shadow-2xl relative overflow-hidden"
            >
              <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
                <div className="flex items-center gap-2">
                  <Code2 className="w-5 h-5 text-lime-400" />
                  <h3 className="font-mono text-base sm:text-lg font-bold text-white">{selectedTool.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedTool(null)}
                  className="px-3 py-1 text-xs font-semibold text-zinc-400 hover:text-white rounded-lg bg-white/5 hover:bg-white/10"
                >
                  Close ✕
                </button>
              </div>

              <div className="space-y-4 font-sans text-sm">
                <div>
                  <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider block mb-1">Description</span>
                  <p className="text-zinc-300 text-xs sm:text-sm leading-relaxed">{selectedTool.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider block mb-1">Target Odoo Model</span>
                    <span className="font-mono text-xs text-lime-400 bg-lime-950/40 px-2.5 py-1 rounded border border-lime-500/20 inline-block">
                      {selectedTool.odooModel}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider block mb-1">Required Role</span>
                    <span className="font-mono text-xs text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded border border-emerald-500/20 inline-flex items-center gap-1">
                      <Shield className="w-3 h-3" /> {selectedTool.role}
                    </span>
                  </div>
                </div>

                <div className="pt-2">
                  <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider block mb-1">Sample MCP Request</span>
                  <div className="p-3 rounded-xl bg-black border border-white/10 font-mono text-xs text-lime-300 overflow-x-auto">
                    <code>{selectedTool.sampleCall}</code>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </section>
  );
}
