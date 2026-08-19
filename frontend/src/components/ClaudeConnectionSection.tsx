'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { KeyRound, Terminal, Power, Bot } from 'lucide-react';

const steps = [
  {
    icon: <KeyRound className="w-5 h-5" />,
    title: "1. Generate API Key",
    description: "Sign in to your OdooX Dashboard, navigate to your workspace, and generate a new secure API Key.",
    iconBg: "bg-blue-500/10 text-blue-400 border-blue-500/20"
  },
  {
    icon: <Terminal className="w-5 h-5" />,
    title: "2. Open Connectors",
    description: "Open Claude Desktop, navigate to Connectors, and choose 'Custom Connector'.",
    iconBg: "bg-purple-500/10 text-purple-400 border-purple-500/20"
  },
  {
    icon: <Bot className="w-5 h-5" />,
    title: "3. Configure ODOOX",
    description: "Set the connector name to 'ODOOX' and paste your entire API key.",
    iconBg: "bg-orange-500/10 text-orange-400 border-orange-500/20"
  },
  {
    icon: <Power className="w-5 h-5" />,
    title: "4. Click Connect",
    description: "Click the connect button. Claude will immediately have access to your Odoo data.",
    iconBg: "bg-green-500/10 text-green-400 border-green-500/20"
  }
];

export function ClaudeConnectionSection() {
  return (
    <section className="relative w-full py-24" id="connect">
      {/* Decorative Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] bg-orange-500/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10 space-y-16">
        
        <div className="text-center space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-white/80"
          >
            <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
            Seamless Integration
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-bold tracking-tight text-white"
          >
            How to connect with <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-200">Claude Desktop.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-white/50 text-lg max-w-2xl mx-auto"
          >
            Get up and running in under 2 minutes. No complex installations or custom Odoo modules required.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * index, type: 'spring', stiffness: 100 }}
              className="relative group bg-[#0a0a0a] border border-white/10 rounded-3xl p-8 hover:bg-[#111111] hover:border-white/20 transition-all duration-300"
            >
              {/* Connector line for large screens */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-px bg-white/10 z-0" />
              )}
              
              <div className="relative z-10 flex flex-col items-center text-center space-y-6">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border ${step.iconBg} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  {step.icon}
                </div>
                <div className="space-y-3">
                  <h3 className="text-xl font-bold text-white">{step.title}</h3>
                  <p className="text-sm text-white/50 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
