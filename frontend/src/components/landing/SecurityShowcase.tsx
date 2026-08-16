"use client";

import React from "react";
import { ShieldCheck, Lock, Server, Key, Cpu, Zap, ArrowRight } from "lucide-react";

export default function SecurityShowcase() {
  return (
    <section id="security" className="w-full relative py-20 sm:py-32 border-y border-white/5 bg-[#080808]">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[400px] bg-emerald-500/5 blur-[150px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          
          {/* Left Description */}
          <div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-6">
              <ShieldCheck className="w-3.5 h-3.5" /> Zero-Trust Architecture
            </span>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-6 leading-tight">
              Enterprise Security Built In From Day One.
            </h2>

            <p className="text-zinc-400 text-base sm:text-lg mb-10 leading-relaxed">
              OdooX enforces multi-tenant isolation, Supabase JWT verification, and encrypted token injection. Claude never sees your database master credentials.
            </p>

            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-lime-500/10 text-lime-400 shrink-0 border border-lime-500/20">
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-base mb-1">Fernet Secret Encryption</h4>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    Database credentials and API tokens are encrypted symmetrically at rest using 256-bit Fernet keys.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 shrink-0 border border-emerald-500/20">
                  <Lock className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-base mb-1">Supabase Tenant Isolation</h4>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    Every SSE connection validates user JWT context, ensuring multi-tenant isolation and per-user session policies.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Flow Visualization */}
          <div className="flex flex-col items-center justify-center w-full max-w-md mx-auto">
            <div className="w-full space-y-4 font-mono text-xs">
              
              <div className="p-5 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-between shadow-lg">
                <div className="flex items-center gap-3">
                  <Cpu className="w-5 h-5 text-lime-400 shrink-0" />
                  <div>
                    <div className="text-white font-bold text-sm">Claude 3.5 Sonnet</div>
                    <div className="text-zinc-500">Desktop App / API Client</div>
                  </div>
                </div>
                <span className="text-lime-400 text-[10px] bg-lime-950/60 px-2 py-0.5 rounded border border-lime-500/30">
                  Tool Request
                </span>
              </div>

              <div className="flex justify-center my-2">
                <ArrowRight className="w-5 h-5 text-zinc-600 rotate-90" />
              </div>

              <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-lime-950/40 border border-lime-500/30 flex items-center justify-between shadow-2xl relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-lime-400 to-emerald-400"></div>
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-lime-400 shrink-0" />
                  <div>
                    <div className="text-white font-bold text-sm">OdooX Security Gateway</div>
                    <div className="text-emerald-400/80">JWT + Schema Validation</div>
                  </div>
                </div>
                <span className="text-emerald-400 text-[10px] bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                  200 Authorized
                </span>
              </div>

              <div className="flex justify-center my-2">
                <ArrowRight className="w-5 h-5 text-zinc-600 rotate-90" />
              </div>

              <div className="p-5 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-between shadow-lg">
                <div className="flex items-center gap-3">
                  <Server className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <div className="text-white font-bold text-sm">Odoo ERP Instance</div>
                    <div className="text-zinc-500">Native XML-RPC (v12-v18)</div>
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
