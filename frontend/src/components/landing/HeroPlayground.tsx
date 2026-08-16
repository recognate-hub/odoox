"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Check, Copy, Terminal, Cpu, Database, ShieldCheck, Sparkles, ArrowRight } from "lucide-react";

interface Scenario {
  id: string;
  name: string;
  badge: string;
  userPrompt: string;
  toolCallName: string;
  toolArgs: Record<string, unknown>;
  odooResponse: Record<string, unknown>;
  claudeOutput: string;
}

const SCENARIOS: Scenario[] = [
  {
    id: "sales",
    name: "Autonomous CRM",
    badge: "create_lead / update_lead",
    userPrompt: "Find all new leads over $10,000 in revenue and qualify HeartCareNet to qualified stage.",
    toolCallName: "update_lead",
    toolArgs: {
      lead_id: 142,
      stage_id: 2,
      probability: 99,
      notes: "Auto-qualified by Claude via OdooX MCP"
    },
    odooResponse: {
      status: "success",
      id: 142,
      model: "crm.lead",
      updated_fields: ["stage_id", "probability"],
      timestamp: "2026-08-16T22:50:00Z"
    },
    claudeOutput: "I've inspected your CRM pipeline. Lead #142 (HeartCareNet) with expected revenue of $10,000 has been moved to the 'Qualified' stage and updated to 99% probability."
  },
  {
    id: "products",
    name: "Inventory Search",
    badge: "get_products",
    userPrompt: "Which products in stock have quantity under 15 units?",
    toolCallName: "get_products",
    toolArgs: {
      domain: [["qty_available", "<", 15]],
      limit: 5,
      fields: ["name", "qty_available", "list_price"]
    },
    odooResponse: {
      total_found: 2,
      products: [
        { id: 88, name: "Custom Steel Bracket", qty_available: 4, list_price: 120.00 },
        { id: 91, name: "Hydraulic Seal Kit", qty_available: 11, list_price: 45.50 }
      ]
    },
    claudeOutput: "Found 2 low-stock products: 'Custom Steel Bracket' (4 units left) and 'Hydraulic Seal Kit' (11 units left). Would you like me to trigger a procurement order?"
  },
  {
    id: "calendar",
    name: "Calendar Booking",
    badge: "schedule_meeting",
    userPrompt: "Book a 30-minute sync with SANJAY N tomorrow at 2 PM regarding software licensing.",
    toolCallName: "schedule_meeting",
    toolArgs: {
      name: "Software Licensing Review",
      partner_id: 49,
      start: "2026-08-17 14:00:00",
      stop: "2026-08-17 14:30:00"
    },
    odooResponse: {
      status: "created",
      event_id: 802,
      attendees: ["sanjay@example.com"],
      calendar_model: "calendar.event"
    },
    claudeOutput: "Meeting scheduled! Event #802 created in Odoo Calendar for tomorrow at 2:00 PM with SANJAY N."
  },
  {
    id: "dashboard",
    name: "Sales Analytics",
    badge: "get_sales_dashboard",
    userPrompt: "Give me an executive summary of current sales revenue and active quotes.",
    toolCallName: "get_sales_dashboard",
    toolArgs: {
      timeframe: "this_month",
      include_pipeline: true
    },
    odooResponse: {
      total_revenue: 145000.00,
      active_quotes: 14,
      win_rate: "68.5%",
      top_rep: "RECOGNATE"
    },
    claudeOutput: "Here is your Odoo Sales Dashboard: Total revenue this month is $145,000 across 14 active quotes with a 68.5% win rate. Top performing rep: RECOGNATE."
  }
];

export default function HeroPlayground() {
  const [activeTab, setActiveTab] = useState<string>("sales");
  const [copied, setCopied] = useState<boolean>(false);
  const currentScenario = SCENARIOS.find((s) => s.id === activeTab) || SCENARIOS[0];

  const copySnippet = () => {
    navigator.clipboard.writeText(`npx odoox-mcp-gateway`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="playground" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 sm:pt-40 pb-20 sm:pb-28 relative">
      {/* Background Radial Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-lime-500/10 via-emerald-500/10 to-transparent blur-[140px] rounded-full pointer-events-none" />

      {/* Hero Header Text */}
      <div className="text-center max-w-4xl mx-auto mb-16 relative z-10 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold tracking-wide uppercase mb-6"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Native Model Context Protocol (MCP) Gateway
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.1]"
        >
          Give Claude Full Agency Over Your{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-lime-400 via-emerald-300 to-teal-200">
            Odoo ERP
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-base sm:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed mb-10"
        >
          Zero custom Odoo modules required. Execute bi-directional CRM leads, inventory queries, calendar bookings, and invoicing securely using native XML-RPC.
        </motion.p>

        {/* Quick CLI Copy Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-lg mx-auto"
        >
          <div className="w-full sm:w-auto flex-1 flex items-center justify-between gap-3 px-4 py-3 rounded-full bg-zinc-900/90 border border-white/10 text-zinc-300 font-mono text-xs sm:text-sm">
            <div className="flex items-center gap-2 overflow-hidden">
              <span className="text-lime-400 font-bold">$</span>
              <span className="truncate">npx odoox-mcp-gateway</span>
            </div>
            <button
              onClick={copySnippet}
              className="p-1.5 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white transition-colors shrink-0"
              title="Copy Command"
            >
              {copied ? <Check className="w-4 h-4 text-lime-400" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>

          <a
            href="#features"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-full font-semibold text-xs sm:text-sm text-black bg-gradient-to-r from-lime-400 to-emerald-400 hover:opacity-95 transition-all shadow-[0_0_20px_rgba(163,230,53,0.3)] shrink-0"
          >
            Explore Capabilities <ArrowRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>

      {/* INTERACTIVE DEMO CONTAINER */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.4 }}
        className="relative z-10 rounded-3xl border border-white/10 bg-gradient-to-b from-zinc-900/90 via-zinc-950/95 to-black p-4 sm:p-6 backdrop-blur-2xl shadow-2xl overflow-hidden"
      >
        {/* Top Window Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <span className="text-xs font-mono text-zinc-400 flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-lime-400" /> OdooX MCP Live Inspector
            </span>
          </div>

          {/* Scenario Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
            {SCENARIOS.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => setActiveTab(scenario.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === scenario.id
                    ? "bg-lime-400 text-black font-semibold shadow-md"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {activeTab === scenario.id && <Play className="w-3 h-3 fill-black" />}
                {scenario.name}
              </button>
            ))}
          </div>
        </div>

        {/* Playground Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-6">
          {/* Left Column: Simulated User & Claude Chat */}
          <div className="lg:col-span-6 flex flex-col justify-between rounded-2xl border border-white/5 bg-zinc-950/60 p-5 font-sans min-h-[380px]">
            <div>
              <div className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>1. Claude Interaction Window</span>
                <span className="text-lime-400 font-semibold flex items-center gap-1 text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-lime-400 animate-ping"></span> Live SSE Connected
                </span>
              </div>

              {/* User Prompt Bubble */}
              <div className="mb-6 flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-zinc-700 to-zinc-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
                  U
                </div>
                <div className="rounded-2xl rounded-tl-none bg-zinc-900 border border-white/10 px-4 py-3 text-xs sm:text-sm text-zinc-200">
                  {currentScenario.userPrompt}
                </div>
              </div>

              {/* Claude Response Bubble */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentScenario.id}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.3 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-lime-500 to-emerald-600 flex items-center justify-center text-xs font-bold text-black shrink-0 shadow-lg">
                    C
                  </div>
                  <div className="rounded-2xl rounded-tl-none bg-lime-950/30 border border-lime-500/20 px-4 py-3 text-xs sm:text-sm text-zinc-200 leading-relaxed">
                    <div className="text-xs font-mono text-lime-400 mb-1 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Claude 3.5 Sonnet
                    </div>
                    {currentScenario.claudeOutput}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Micro Specs Footer */}
            <div className="pt-4 border-t border-white/5 flex items-center justify-between text-[11px] text-zinc-500 font-mono">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> RBAC Enforced
              </span>
              <span>Protocol: Standard SSE / JSON-RPC</span>
            </div>
          </div>

          {/* Right Column: Real-time MCP Payload Inspector */}
          <div className="lg:col-span-6 flex flex-col justify-between rounded-2xl border border-white/5 bg-zinc-950/90 p-5 font-mono text-xs overflow-hidden min-h-[380px]">
            <div>
              <div className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>2. MCP Tool Execution Payload</span>
                <span className="text-zinc-400 bg-white/5 px-2 py-0.5 rounded border border-white/10 text-[11px]">
                  {currentScenario.badge}
                </span>
              </div>

              {/* Tool Arguments */}
              <div className="mb-4">
                <div className="text-zinc-500 mb-1.5 flex items-center gap-1.5 text-[11px]">
                  <Cpu className="w-3.5 h-3.5 text-lime-400" /> Action Payload (Tool Call):
                </div>
                <div className="p-3 rounded-xl bg-black border border-white/10 text-lime-300 overflow-x-auto text-[11px]">
                  <pre>{JSON.stringify({ tool: currentScenario.toolCallName, args: currentScenario.toolArgs }, null, 2)}</pre>
                </div>
              </div>

              {/* Odoo Backend Response */}
              <div>
                <div className="text-zinc-500 mb-1.5 flex items-center gap-1.5 text-[11px]">
                  <Database className="w-3.5 h-3.5 text-emerald-400" /> Odoo XML-RPC Result:
                </div>
                <div className="p-3 rounded-xl bg-black border border-white/10 text-emerald-300 overflow-x-auto text-[11px]">
                  <pre>{JSON.stringify(currentScenario.odooResponse, null, 2)}</pre>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-zinc-500 text-[11px]">
              <span>Response Time: 34ms</span>
              <span>Odoo API Status: 200 OK</span>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
