"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, RefreshCw, LayoutDashboard } from 'lucide-react';

const bentoItems = [
  {
    title: "Military-Grade Security",
    description: "Built-in RBAC ensures Claude only accesses what the authenticated user is allowed to see. Every query is scoped.",
    icon: <Shield className="w-6 h-6 text-lime-400" />,
    colSpan: "md:col-span-8",
  },
  {
    title: "Zero Latency",
    description: "Direct XML-RPC connections to Odoo instances bypass traditional heavy REST APIs.",
    icon: <Zap className="w-6 h-6 text-amber-400" />,
    colSpan: "md:col-span-4",
  },
  {
    title: "Bi-Directional Sync",
    description: "Read, write, update, and delete. Total CRUD capability exposed through safe MCP tool definitions.",
    icon: <RefreshCw className="w-6 h-6 text-blue-400" />,
    colSpan: "md:col-span-4",
  },
  {
    title: "Instant Dashboards",
    description: "Generate beautiful data visualizations natively in Claude's UI by streaming Odoo analytics data.",
    icon: <LayoutDashboard className="w-6 h-6 text-purple-400" />,
    colSpan: "md:col-span-8",
  }
];

export default function ModernBento() {
  return (
    <section className="w-full max-w-7xl mx-auto py-32 px-6">
      <div className="mb-16">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white mb-4">Enterprise Grade by Default.</h2>
        <p className="text-xl text-zinc-400 max-w-2xl">We stripped away the complexity. What remains is a robust, secure, and blazing-fast bridge between your AI and your data.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[280px]">
        {bentoItems.map((item, index) => (
          <motion.div
            key={index}
            whileHover={{ y: -5, transition: { duration: 0.2 } }}
            className={`relative group rounded-3xl border border-white/5 bg-[#121212] overflow-hidden ${item.colSpan} p-8 flex flex-col justify-between`}
          >
            {/* Subtle Hover Gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="relative z-10 w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6">
              {item.icon}
            </div>

            <div className="relative z-10">
              <h3 className="text-2xl font-semibold text-white mb-3">{item.title}</h3>
              <p className="text-zinc-400 leading-relaxed">
                {item.description}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
