"use client";

import React, { useState } from "react";
import { ChevronDown, HelpCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const FAQS = [
  {
    q: "Do I need to install any custom Python modules on my Odoo server?",
    a: "No! OdooX communicates with your Odoo instance strictly via native XML-RPC protocol (port 8069 / HTTPS). It requires zero custom module installations on your Odoo backend."
  },
  {
    q: "Which Odoo versions are supported?",
    a: "OdooX natively supports Odoo Community and Enterprise versions v12, v13, v14, v15, v16, v17, and v18."
  },
  {
    q: "How does Claude connect to OdooX?",
    a: "OdooX exposes a standardized Model Context Protocol (MCP) server over SSE (Server-Sent Events) or stdio. You simply paste your OdooX workspace token into your Claude Desktop or MCP client config."
  },
  {
    q: "Is my Odoo password stored securely?",
    a: "Yes. All database credentials and access tokens are symmetrically encrypted at rest using 256-bit Fernet encryption. Plaintext passwords are never logged or stored."
  },
  {
    q: "Can I limit what tools Claude is allowed to execute?",
    a: "Absolutely. OdooX features built-in Role-Based Access Control (RBAC). You can assign user roles (Admin, Sales Rep, Viewer) to restrict tool access so Claude cannot perform unauthorized updates."
  }
];

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 relative">
      <div className="text-center max-w-3xl mx-auto mb-14">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-lime-500/30 bg-lime-500/10 text-lime-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <HelpCircle className="w-3.5 h-3.5" /> Got Questions?
        </span>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-4">
          Frequently Asked Questions
        </h2>
        <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto">
          Everything you need to know about setting up OdooX with Claude.
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-4">
        {FAQS.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div
              key={idx}
              className="rounded-2xl border border-white/10 bg-zinc-900/50 overflow-hidden transition-colors"
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full px-6 py-5 flex items-center justify-between text-left font-semibold text-white text-sm sm:text-base hover:text-lime-400 transition-colors gap-4"
              >
                <span>{faq.q}</span>
                <ChevronDown className={`w-5 h-5 text-zinc-400 transition-transform duration-300 shrink-0 ${isOpen ? "rotate-180 text-lime-400" : ""}`} />
              </button>

              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="px-6 pb-6 text-xs sm:text-sm text-zinc-400 leading-relaxed border-t border-white/5 pt-4">
                      {faq.a}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}
