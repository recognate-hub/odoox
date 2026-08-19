'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plug, Shield, MessageSquare, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const steps = [
  {
    id: 0,
    title: 'Enter credentials',
    description: "Provide your Odoo URL, database name, and user login. Works with Odoo v12 through v17 — cloud or self-hosted.",
    icon: Plug,
  },
  {
    id: 1,
    title: 'Gateway authenticates',
    description: "OdooX validates your JWT, enforces granular RBAC, applies rate limits, and securely opens an SSE channel.",
    icon: Shield,
  },
  {
    id: 2,
    title: 'Talk to your ERP',
    description: "Claude can now read, create, and update records across CRM, Sales, Inventory, Manufacturing, and more.",
    icon: MessageSquare,
  }
];

export function PlatformSection() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-play logic
  useEffect(() => {
    if (isPaused) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % steps.length);
    }, 5000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPaused, activeIndex]);

  // Visualizations for the Right Canvas
  const renderCanvas = (index: number) => {
    switch (index) {
      case 0:
        return (
          <div className="w-full h-full flex flex-col bg-[#050505] rounded-[32px] overflow-hidden font-mono text-sm relative border border-white/5 m-6 shadow-2xl" style={{ height: 'calc(100% - 48px)', width: 'calc(100% - 48px)' }}>
            <div className="flex items-center gap-2 px-6 py-4 bg-[#0a0a0a] border-b border-white/5 z-10">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
              </div>
              <span className="ml-4 text-white/30 text-xs font-bold tracking-widest uppercase">odoo-connect.sh</span>
            </div>
            <div className="p-8 space-y-6">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 text-white/60">
                <span className="text-primary-container">❯</span> 
                <span>odoo-cli auth login --host api.odoox.com</span>
              </motion.div>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="text-white/80">
                Resolving XML-RPC endpoints... <span className="text-primary-container font-bold">[OK]</span>
              </motion.div>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }} className="text-white/80">
                Authenticating credentials... <span className="text-primary-container font-bold">[OK]</span>
              </motion.div>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }} className="flex items-center gap-2 text-primary-container font-bold">
                <Zap className="w-4 h-4 fill-primary-container" /> Connection established. Handshake complete.
              </motion.div>
            </div>
          </div>
        );
      case 1:
        return (
          <div className="w-full h-full flex items-center justify-center relative">
            {/* Animated Radar Rings */}
            <motion.div 
              className="absolute w-64 h-64 rounded-full border border-primary-container/20"
              animate={{ scale: [1, 2.5], opacity: [1, 0] }}
              transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
            />
            <motion.div 
              className="absolute w-64 h-64 rounded-full border border-primary-container/20"
              animate={{ scale: [1, 2.5], opacity: [1, 0] }}
              transition={{ repeat: Infinity, duration: 3, ease: "linear", delay: 1.5 }}
            />
            
            {/* Center Node */}
            <div className="relative z-10 w-32 h-32 rounded-full bg-black/80 backdrop-blur-xl border border-white/10 flex items-center justify-center shadow-[0_0_40px_rgba(132,204,22,0.15)]">
              <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                <Shield className="w-10 h-10 text-primary-container drop-shadow-[0_0_15px_rgba(132,204,22,0.8)]" />
              </motion.div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="w-full h-full flex flex-col justify-center items-center p-8 relative">
            <div className="w-full max-w-sm space-y-8 relative z-10">
              {/* User Message */}
              <motion.div 
                initial={{ opacity: 0, y: 10, scale: 0.95 }} 
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className="bg-white/5 border border-white/10 rounded-[24px] rounded-tr-none p-6 text-sm ml-auto w-[85%] shadow-xl"
              >
                <p className="text-white/90 font-medium leading-relaxed">How many units of the Pro Server Rack are currently in stock?</p>
              </motion.div>
              
              {/* System Response */}
              <motion.div 
                initial={{ opacity: 0, y: 10, scale: 0.95 }} 
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ delay: 0.8 }}
                className="bg-primary-container/10 border border-primary-container/20 rounded-[24px] rounded-tl-none p-6 text-sm mr-auto w-[90%] shadow-[0_0_30px_rgba(132,204,22,0.1)] relative"
              >
                <div className="absolute -top-4 -left-4 w-10 h-10 rounded-full bg-[#0a0a0a] border border-white/10 shadow-xl flex items-center justify-center z-10">
                   <span className="text-primary-container text-[10px] font-black drop-shadow-[0_0_5px_rgba(132,204,22,0.8)]">AI</span>
                </div>
                <p className="text-primary-container font-bold mb-3 tracking-wider text-xs uppercase">Querying Odoo Inventory...</p>
                <p className="text-white/80 leading-relaxed text-base">There are currently <strong className="text-white">42 units</strong> available in the main WH/Stock location.</p>
              </motion.div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <section className="relative py-24 w-full overflow-hidden" id="platform">
      
      {/* Intense Ambient Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-primary-container/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 relative z-10">
        
        {/* Header */}
        <div className="text-center space-y-6 max-w-3xl mx-auto mb-20">
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white drop-shadow-[0_4px_10px_rgba(0,0,0,0.5)]">
            Three steps. <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-primary drop-shadow-[0_0_30px_rgba(132,204,22,0.3)]">Zero Odoo modules</span> to install.
          </h2>
        </div>

        {/* The Split Screen Container */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          {/* LEFT: Accordion */}
          <div className="lg:col-span-5 space-y-4" onMouseEnter={() => setIsPaused(true)} onMouseLeave={() => setIsPaused(false)}>
            {steps.map((step, index) => {
              const isActive = index === activeIndex;
              return (
                <div 
                  key={step.id}
                  onClick={() => setActiveIndex(index)}
                  className={cn(
                    "relative overflow-hidden rounded-[24px] cursor-pointer transition-all duration-500 border",
                    isActive 
                      ? "bg-white/[0.04] border-white/10 shadow-[0_0_30px_rgba(132,204,22,0.05)]" 
                      : "bg-transparent border-transparent hover:bg-white/[0.02]"
                  )}
                >
                  <div className="p-6 md:p-8 flex items-start gap-6">
                    {/* Icon Container */}
                    <div className={cn(
                      "w-12 h-12 shrink-0 rounded-xl flex items-center justify-center transition-all duration-500 border",
                      isActive 
                        ? "bg-primary-container/10 border-primary-container/30 text-primary-container shadow-[0_0_20px_rgba(132,204,22,0.2)]" 
                        : "bg-white/[0.03] border-white/5 text-white/40"
                    )}>
                      <step.icon className={cn("w-5 h-5", isActive && "drop-shadow-[0_0_8px_rgba(132,204,22,0.6)]")} />
                    </div>

                    <div className="space-y-3">
                      <h3 className={cn(
                        "text-xl font-bold transition-colors duration-500 tracking-wide",
                        isActive ? "text-white" : "text-white/50"
                      )}>
                        {step.title}
                      </h3>
                      
                      {/* Accordion Content */}
                      <AnimatePresence initial={false}>
                        {isActive && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.4, ease: "easeInOut" }}
                            className="overflow-hidden"
                          >
                            <p className="text-white/60 leading-relaxed text-sm pt-2">
                              {step.description}
                            </p>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* RIGHT: Visual Canvas */}
          <div className="lg:col-span-7 h-[500px]">
            <div className="w-full h-full rounded-[40px] bg-[#0a0a0a]/80 backdrop-blur-3xl border border-white/10 shadow-2xl overflow-hidden relative">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeIndex}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.5, ease: "easeInOut" }}
                  className="absolute inset-0 z-10"
                >
                  {renderCanvas(activeIndex)}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
