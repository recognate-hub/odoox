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
    <section id="playground" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 sm:pt-48 pb-20 relative">
      {/* Immersive Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[600px] bg-gradient-to-b from-lime-500/10 via-emerald-500/5 to-transparent blur-[100px] rounded-full pointer-events-none" />

      {/* Hero Header Text */}
      <div className="text-center max-w-4xl mx-auto mb-20 relative z-10 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-lime-500/20 bg-lime-500/5 text-lime-400 text-xs font-semibold tracking-wide uppercase mb-8 shadow-[0_0_20px_rgba(163,230,53,0.1)]"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Native Model Context Protocol (MCP) Gateway
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.05]"
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
          <div className="w-full sm:w-auto flex-1 flex items-center justify-between gap-3 px-4 py-3 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-300 font-mono text-xs sm:text-sm backdrop-blur-md">
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
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-xs sm:text-sm text-black bg-gradient-to-r from-lime-400 to-emerald-400 hover:opacity-95 transition-all shadow-[0_0_20px_rgba(163,230,53,0.2)] shrink-0"
          >
            Explore Capabilities <ArrowRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>

      {/* FLOATING MAC-OS STYLE TERMINAL WINDOW */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="relative z-20 w-full max-w-6xl mx-auto rounded-2xl border border-white/10 bg-[#0C0C0C]/80 backdrop-blur-2xl shadow-[0_30px_100px_-20px_rgba(0,0,0,1)] overflow-hidden"
      >
        {/* Window Top Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-5 py-3 border-b border-white/10 bg-[#111]/90">
          <div className="flex items-center gap-4">
            {/* Mac Window Dots */}
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <span className="text-xs font-mono text-zinc-500 flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5" /> OdooX Inspector
            </span>
          </div>

          {/* Scenario Tabs inside Window Bar */}
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {SCENARIOS.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => setActiveTab(scenario.id)}
                className={`px-3 py-1 rounded text-[11px] font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  activeTab === scenario.id
                    ? "bg-zinc-800 text-white shadow-inner"
                    : "text-zinc-500 hover:text-white hover:bg-zinc-800/50"
                }`}
              >
                {activeTab === scenario.id && <Play className="w-3 h-3 fill-lime-400 text-lime-400" />}
                {scenario.name}
              </button>
            ))}
          </div>
        </div>

        {/* Playground Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-white/10">
          
          {/* Left Panel: Chat Interface */}
          <div className="p-6 flex flex-col min-h-[400px] bg-zinc-950/40">
            <div className="text-[10px] font-mono text-zinc-600 uppercase tracking-wider mb-5 flex items-center justify-between">
              <span>Interactive Chat</span>
              <span className="text-lime-500/70 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-lime-500 animate-pulse"></span> SSE Streaming
              </span>
            </div>

            {/* User Prompt */}
            <div className="mb-6 flex gap-3">
              <div className="w-7 h-7 rounded bg-zinc-800 flex items-center justify-center text-[10px] font-bold text-zinc-300 shrink-0">
                U
              </div>
              <div className="rounded-xl rounded-tl-none bg-zinc-900 border border-white/5 px-4 py-3 text-sm text-zinc-300">
                {currentScenario.userPrompt}
              </div>
            </div>

            {/* Claude Response */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentScenario.id}
                initial={{ opacity: 0, x: 5 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -5 }}
                transition={{ duration: 0.2 }}
                className="flex gap-3"
              >
                <div className="w-7 h-7 rounded bg-lime-900/50 border border-lime-500/30 flex items-center justify-center text-[10px] font-bold text-lime-400 shrink-0">
                  C
                </div>
                <div className="rounded-xl rounded-tl-none bg-lime-950/20 border border-lime-500/10 px-4 py-3 text-sm text-zinc-300 leading-relaxed">
                  <div className="text-[10px] font-mono text-lime-500/70 mb-1.5 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> Claude 3.5 Sonnet
                  </div>
                  {currentScenario.claudeOutput}
                </div>
              </motion.div>
            </AnimatePresence>

            <div className="mt-auto pt-4 flex items-center justify-between text-[10px] text-zinc-600 font-mono">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-500/70" /> Context Verified
              </span>
            </div>
          </div>

          {/* Right Panel: JSON Trace */}
          <div className="p-6 flex flex-col min-h-[400px] bg-black/60 font-mono text-xs">
            <div className="text-[10px] text-zinc-600 uppercase tracking-wider mb-5 flex items-center justify-between">
              <span>Network Trace</span>
              <span className="text-zinc-500 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                {currentScenario.badge}
              </span>
            </div>

            {/* MCP Call JSON */}
            <div className="mb-4">
              <div className="text-zinc-500 mb-2 flex items-center gap-1.5 text-[10px]">
                <Cpu className="w-3 h-3 text-lime-500/80" /> Tool Invocation:
              </div>
              <div className="p-3 rounded-lg bg-[#050505] border border-white/5 text-lime-400/80 overflow-x-auto text-[11px] leading-relaxed">
                <pre>{JSON.stringify({ tool: currentScenario.toolCallName, args: currentScenario.toolArgs }, null, 2)}</pre>
              </div>
            </div>

            {/* XML-RPC Result JSON */}
            <div>
              <div className="text-zinc-500 mb-2 flex items-center gap-1.5 text-[10px]">
                <Database className="w-3 h-3 text-emerald-500/80" /> Native XML-RPC Result:
              </div>
              <div className="p-3 rounded-lg bg-[#050505] border border-white/5 text-emerald-400/80 overflow-x-auto text-[11px] leading-relaxed">
                <pre>{JSON.stringify(currentScenario.odooResponse, null, 2)}</pre>
              </div>
            </div>

            <div className="mt-auto pt-4 flex items-center justify-between text-zinc-600 text-[10px]">
              <span>Latency: 34ms</span>
              <span>200 OK</span>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
