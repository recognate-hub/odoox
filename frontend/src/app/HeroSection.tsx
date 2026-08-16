"use client";

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

interface Props {
  hasToken: boolean;
  isPaid: boolean;
}

export default function HeroSection({ hasToken, isPaid }: Props) {
  return (
    <section className="relative w-full min-h-screen flex flex-col items-center justify-center pt-20 px-6 overflow-hidden">
      {/* Absolute Background Elements */}
      <div className="absolute inset-0 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-lime-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-0 w-full h-1/2 bg-gradient-to-t from-[#0a0a0a] to-transparent z-10" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-20 flex flex-col items-center text-center max-w-4xl mx-auto"
      >
        <div className="mb-8 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm text-sm text-zinc-300">
          <span className="flex h-2 w-2 rounded-full bg-lime-500 animate-pulse"></span>
          Now supporting Claude 3.5 Sonnet Integration
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 mb-8 leading-[1.1]">
          The infrastructure for <br />
          AI-driven ERP.
        </h1>

        <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed">
          Connect Claude and other LLMs directly to your Odoo backend using the standard Model Context Protocol. Zero latency, military-grade security.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4">
          {!hasToken ? (
              <Link href="/login" className="bg-white text-black px-8 py-3 rounded-full font-medium hover:bg-zinc-200 transition-colors">
                Start Building
              </Link>
          ) : isPaid ? (
              <Link href="/userdashboard" className="bg-white text-black px-8 py-3 rounded-full font-medium hover:bg-zinc-200 transition-colors">
                Go to Dashboard
              </Link>
          ) : (
              <Link href="/payment" className="bg-lime-400 text-black px-8 py-3 rounded-full font-medium shadow-[0_0_15px_rgba(163,230,53,0.3)] hover:scale-105 transition-transform">
                Unlock Pro Access
              </Link>
          )}
          <a href="#features" className="text-zinc-400 hover:text-white px-8 py-3 font-medium transition-colors">
            Explore Features →
          </a>
        </div>
      </motion.div>

      {/* Hero Abstract Graphic */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-0 mt-20 w-full max-w-5xl rounded-t-[2rem] border border-white/10 border-b-0 bg-gradient-to-b from-white/[0.03] to-transparent p-4 backdrop-blur-3xl overflow-hidden"
      >
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        <div className="w-full aspect-[2/1] rounded-[1.5rem] bg-[#0f0f0f] border border-white/5 shadow-2xl overflow-hidden flex items-center justify-center relative">
           {/* Abstract MCP Architecture Visualization */}
           <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
           
           <div className="flex items-center gap-8 md:gap-16 relative z-10">
              <div className="flex flex-col items-center gap-3">
                 <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-center shadow-lg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-zinc-400"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                 </div>
                 <span className="text-xs font-mono text-zinc-500">Claude AI</span>
              </div>
              
              {/* Animated Connection Line */}
              <div className="w-24 md:w-48 h-[2px] bg-white/10 relative overflow-hidden">
                <motion.div 
                  className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-lime-500 to-transparent"
                  animate={{ left: ['-100%', '200%'] }}
                  transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                />
              </div>

              <div className="flex flex-col items-center gap-3">
                 <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-zinc-800 to-black border border-white/20 flex items-center justify-center shadow-[0_0_30px_rgba(163,230,53,0.15)] relative">
                    <div className="absolute inset-0 bg-lime-500/10 blur-xl rounded-full" />
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white relative z-10"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                 </div>
                 <span className="text-xs font-mono text-zinc-300">MCP Gateway</span>
              </div>

              <div className="w-24 md:w-48 h-[2px] bg-white/10 relative overflow-hidden">
                <motion.div 
                  className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-blue-500 to-transparent"
                  animate={{ left: ['-100%', '200%'] }}
                  transition={{ repeat: Infinity, duration: 2, ease: "linear", delay: 0.5 }}
                />
              </div>

              <div className="flex flex-col items-center gap-3">
                 <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-center shadow-lg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-zinc-400"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
                 </div>
                 <span className="text-xs font-mono text-zinc-500">Odoo Database</span>
              </div>
           </div>
        </div>
      </motion.div>
    </section>
  );
}
