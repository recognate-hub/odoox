"use client";

import React from "react";
import { ShieldCheck, Lock, Server, Key, Cpu, Zap, ArrowRight } from "lucide-react";

export default function SecurityShowcase() {
  return (
    <section id="security" className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-24 relative">
      <div className="rounded-3xl border border-white/10 bg-gradient-to-b from-zinc-950 via-zinc-900/50 to-zinc-950 p-8 sm:p-14 relative overflow-hidden shadow-2xl">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-emerald-500/10 blur-[150px] rounded-full pointer-events-none" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
          {/* Left Description */}
          <div className="lg:col-span-6">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-6">
              <ShieldCheck className="w-3.5 h-3.5" /> Zero-Trust Architecture
            </span>

            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-6 leading-tight">
              Enterprise Security Built In From Day One.
            </h2>

            <p className="text-zinc-400 text-base sm:text-lg mb-8 leading-relaxed">
              OdooX enforces multi-tenant isolation, Supabase JWT verification, and encrypted token injection. Claude never sees your database master credentials.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="p-2.5 rounded-xl bg-lime-500/10 text-lime-400 shrink-0">
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm mb-1">Fernet Secret Encryption</h4>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Database credentials and API tokens are encrypted symmetrically at rest using 256-bit Fernet keys.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 shrink-0">
                  <Lock className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm mb-1">Supabase Tenant Isolation</h4>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Every SSE connection validates user JWT context, ensuring multi-tenant isolation and per-user session policies.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Flow Visualization */}
          <div className="lg:col-span-6 flex flex-col items-center justify-center">
            <div className="w-full space-y-3 font-mono text-xs">
              <div className="p-4 rounded-2xl bg-zinc-900/90 border border-white/10 flex items-center justify-between shadow-lg">
                <div className="flex items-center gap-3">
                  <Cpu className="w-5 h-5 text-lime-400" />
                  <div>
                    <div className="text-white font-bold">Claude 3.5 Sonnet</div>
                    <div className="text-zinc-500 text-[11px]">Desktop App / API Client</div>
                  </div>
                </div>
                <span className="text-lime-400 text-[10px] bg-lime-950/60 px-2 py-0.5 rounded border border-lime-500/30">
                  Tool Request
                </span>
              </div>

              <div className="flex justify-center my-1">
                <ArrowRight className="w-4 h-4 text-zinc-600 rotate-90" />
              </div>

              <div className="p-4 rounded-2xl bg-lime-950/30 border border-lime-500/30 flex items-center justify-between shadow-xl relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-lime-400"></div>
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-lime-400" />
                  <div>
                    <div className="text-white font-bold">OdooX MCP Security Layer</div>
                    <div className="text-zinc-400 text-[11px]">JWT Auth + Pydantic Schema Validation</div>
                  </div>
                </div>
                <span className="text-emerald-400 text-[10px] bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                  200 Authorized
                </span>
              </div>

              <div className="flex justify-center my-1">
                <ArrowRight className="w-4 h-4 text-zinc-600 rotate-90" />
              </div>

              <div className="p-4 rounded-2xl bg-zinc-900/90 border border-white/10 flex items-center justify-between shadow-lg">
                <div className="flex items-center gap-3">
                  <Server className="w-5 h-5 text-emerald-400" />
                  <div>
                    <div className="text-white font-bold">Odoo ERP Instance</div>
                    <div className="text-zinc-500 text-[11px]">Native XML-RPC (v12-v18)</div>
                  </div>
                </div>
                <span className="text-zinc-400 text-[10px] bg-white/5 px-2 py-0.5 rounded border border-white/10">
                  Direct Response
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
