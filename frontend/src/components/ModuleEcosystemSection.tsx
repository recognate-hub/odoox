'use client';

import React, { useState, useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion';
import { 
  Kanban, ShoppingCart, Package, Factory, 
  FileText, Wrench, Users, BarChart2,
  Database, ShieldAlert, Activity, MessageSquare, 
  ScanBarcode, Calendar, Briefcase, Calculator, 
  ShieldCheck, Sparkles, Zap, Bot, Cpu, TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

const modules = [
  // ── Left Orbit (CRM, Sales, Discuss, Contacts) ───────────────────────
  { id: 'crm', label: 'CRM & Pipeline', count: '8 tools', icon: Kanban, x: 8, y: 48 },
  { id: 'sales', label: 'Sales & Quotes', count: '3 tools', icon: ShoppingCart, x: 14, y: 26 },
  { id: 'discuss', label: 'Discuss & Chatter', count: '4 tools', icon: MessageSquare, x: 14, y: 72 },
  { id: 'contacts', label: 'Contacts 360', count: '3 tools', icon: Users, x: 26, y: 38 },
  { id: 'calendar', label: 'Calendar & Meets', count: '2 tools', icon: Calendar, x: 26, y: 62 },

  // ── Right Orbit (Manufacturing, Inventory, Invoicing, Planning) ──────
  { id: 'manufacturing', label: 'Manufacturing MRP', count: '18 tools', icon: Factory, x: 92, y: 48 },
  { id: 'inventory', label: 'Inventory & Stock', count: '8 tools', icon: Package, x: 86, y: 26 },
  { id: 'invoicing', label: 'Invoicing & Pay', count: '4 tools', icon: FileText, x: 86, y: 72 },
  { id: 'barcode', label: 'Barcode Logistics', count: '2 tools', icon: ScanBarcode, x: 74, y: 38 },
  { id: 'planning', label: 'Planning & MPS', count: '2 tools', icon: Cpu, x: 74, y: 62 },

  // ── Top Orbit (Projects, Accounting, Quality, Intelligence) ──────────
  { id: 'projects', label: 'Projects & Tasks', count: '7 tools', icon: Briefcase, x: 38, y: 16 },
  { id: 'accounting', label: 'Accounting Core', count: '7 tools', icon: Calculator, x: 50, y: 12 },
  { id: 'quality', label: 'Quality Control', count: '9 tools', icon: ShieldCheck, x: 62, y: 16 },

  // ── Bottom Orbit (Purchase, Maintenance, HR, FinOps, Meta-Engine) ────
  { id: 'purchase', label: 'Purchase & POs', count: '4 tools', icon: ShoppingCart, x: 34, y: 84 },
  { id: 'maintenance', label: 'Equipment & Maint', count: '3 tools', icon: Wrench, x: 44, y: 88 },
  { id: 'hr', label: 'HR & Employees', count: '10 tools', icon: Users, x: 56, y: 88 },
  { id: 'finops', label: 'FinOps & Budget', count: '2 tools', icon: TrendingUp, x: 66, y: 84 },

  // ── Inner Satellites (Meta-Engine, Prompts, Schema) ──────────────────
  { id: 'generic', label: 'Universal Meta-Engine', count: '8 tools', icon: Zap, x: 36, y: 50 },
  { id: 'prompts', label: 'MCP Prompts & Workflows', count: '5 prompts', icon: Bot, x: 64, y: 50 },
];

export function ModuleEcosystemSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Parallax mouse tracking
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 150 };
  const smoothMouseX = useSpring(mouseX, springConfig);
  const smoothMouseY = useSpring(mouseY, springConfig);

  const bgX = useTransform(smoothMouseX, [-500, 500], [12, -12]);
  const bgY = useTransform(smoothMouseY, [-500, 500], [12, -12]);

  const fgX = useTransform(smoothMouseX, [-500, 500], [-20, 20]);
  const fgY = useTransform(smoothMouseY, [-500, 500], [-20, 20]);

  const svgX = useTransform(smoothMouseX, [-500, 500], [-8, 8]);
  const svgY = useTransform(smoothMouseY, [-500, 500], [-8, 8]);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    mouseX.set(e.clientX - centerX);
    mouseY.set(e.clientY - centerY);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <section 
      id="ecosystem"
      className="relative w-full py-16 flex flex-col items-center justify-center bg-black/20 overflow-hidden"
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Background Deep Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(132,204,22,0.04)_0%,transparent_70%)] pointer-events-none" />

      {/* 1. Header Info (Clean Normal Flow - Zero Overlap) */}
      <div className="text-center space-y-4 relative z-30 max-w-4xl mx-auto px-6 mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary-container/30 bg-primary-container/10 text-primary-container text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" /> Full Enterprise ERP Coverage
        </div>
        <h2 className="text-3xl sm:text-4xl md:text-6xl font-bold tracking-tight text-white">
          100+ native tools across <br className="hidden sm:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container via-[#acf847] to-primary">
            24 Odoo modules.
          </span>
        </h2>
        <p className="text-white/60 text-sm md:text-base font-mono max-w-xl mx-auto">
          Hover over any node to explore tools and live MCP endpoints
        </p>
      </div>

      {/* 2. Constellation Interactive Canvas */}
      <div className="w-full h-[620px] relative overflow-x-auto overflow-y-hidden scrollbar-hide cursor-crosshair">
        <div className="min-w-[1000px] w-full h-full relative">
          
          {/* Connecting SVG Lines */}
          <motion.div 
            className="absolute inset-0 z-10 pointer-events-none"
            style={{ x: svgX, y: svgY }}
          >
            <svg className="w-full h-full">
              <defs>
                <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="rgba(132,204,22,0.6)" />
                  <stop offset="100%" stopColor="rgba(255,255,255,0.05)" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              
              {modules.map((mod) => {
                const isHovered = hoveredNode === mod.id;
                return (
                  <g key={`line-${mod.id}`}>
                    <line 
                      x1="50%" y1="50%" 
                      x2={`${mod.x}%`} y2={`${mod.y}%`}
                      stroke="rgba(255,255,255,0.06)"
                      strokeWidth="1"
                    />
                    
                    {isHovered && (
                      <motion.circle
                        r="3.5"
                        fill="#84cc16"
                        filter="url(#glow)"
                        initial={{ cx: "50%", cy: "50%", opacity: 0 }}
                        animate={{ 
                          cx: ["50%", `${mod.x}%`], 
                          cy: ["50%", `${mod.y}%`],
                          opacity: [0, 1, 0]
                        }}
                        transition={{
                          duration: 1.2,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                      />
                    )}

                    <motion.line 
                      x1="50%" y1="50%" 
                      x2={`${mod.x}%`} y2={`${mod.y}%`}
                      stroke="url(#line-gradient)"
                      strokeWidth="2"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: isHovered ? 1 : 0 }}
                      transition={{ duration: 0.3 }}
                    />
                  </g>
                );
              })}
            </svg>
          </motion.div>

          {/* Orbital Nodes */}
          <motion.div 
            className="absolute inset-0 z-20 pointer-events-none"
            style={{ x: bgX, y: bgY }}
          >
            {modules.map((mod) => {
              const isHovered = hoveredNode === mod.id;
              const isFaded = hoveredNode !== null && !isHovered;

              return (
                <div 
                  key={mod.id}
                  className="absolute pointer-events-auto"
                  style={{ left: `${mod.x}%`, top: `${mod.y}%`, transform: 'translate(-50%, -50%)' }}
                  onMouseEnter={() => setHoveredNode(mod.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                >
                  <motion.div 
                    className={cn(
                      "relative flex flex-col items-center justify-center gap-1.5 transition-all duration-300",
                      isFaded && "opacity-20 scale-95 grayscale"
                    )}
                    animate={{ y: [0, -4, 0] }}
                    transition={{ 
                      duration: 3.5, 
                      repeat: Infinity, 
                      ease: "easeInOut",
                      delay: (mod.x + mod.y) * 0.02 
                    }}
                  >
                    <div className={cn(
                      "w-11 h-11 rounded-full flex items-center justify-center border backdrop-blur-md transition-all duration-300 relative z-10",
                      isHovered 
                        ? "bg-primary-container/20 border-primary-container shadow-[0_0_30px_rgba(132,204,22,0.5)] scale-125" 
                        : "bg-white/[0.03] border-white/10 hover:border-white/30"
                    )}>
                      <mod.icon className={cn(
                        "w-4 h-4 transition-colors duration-300",
                        isHovered ? "text-primary-container drop-shadow-[0_0_8px_rgba(132,204,22,1)]" : "text-white/50"
                      )} />
                    </div>
                    
                    <div className="flex flex-col items-center absolute -bottom-8 whitespace-nowrap pointer-events-none">
                      <span className={cn(
                        "text-[11px] font-medium tracking-wide transition-colors duration-300",
                        isHovered ? "text-white font-semibold drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]" : "text-white/40"
                      )}>
                        {mod.label}
                      </span>
                    </div>

                    <AnimatePresence>
                      {isHovered && (
                        <motion.div 
                          initial={{ opacity: 0, y: 10, scale: 0.9 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, y: 5, scale: 0.95 }}
                          className="absolute top-full left-1/2 -translate-x-1/2 mt-10 w-52 bg-black/90 backdrop-blur-2xl border border-primary-container/40 rounded-xl p-4 shadow-[0_10px_40px_rgba(0,0,0,0.8)] z-50 pointer-events-none"
                        >
                          <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-black/90 border-t border-l border-primary-container/40 rotate-45" />
                          <div className="relative z-10 space-y-1">
                            <div className="flex items-center justify-between">
                              <h4 className="text-primary-container font-bold text-xs">{mod.label}</h4>
                              <span className="text-[9px] bg-primary-container/20 text-primary-container px-1.5 py-0.5 rounded font-mono font-bold">{mod.count}</span>
                            </div>
                            <p className="text-white/60 text-[11px] leading-relaxed">Type-safe FastMCP endpoints with multi-tenant RBAC and XML-RPC integration.</p>
                            <div className="pt-2 flex items-center gap-1 text-[9px] text-white/40 uppercase tracking-widest font-mono">
                              <Activity className="w-3 h-3 text-primary-container" /> System Operational
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                </div>
              );
            })}
          </motion.div>

          {/* Central Gateway Nexus */}
          <motion.div 
            className="absolute top-1/2 left-1/2 z-30 pointer-events-none"
            style={{ 
              x: fgX, 
              y: fgY,
              translateX: "-50%",
              translateY: "-50%" 
            }}
          >
            <div className="relative flex items-center justify-center">
              <motion.div 
                className="absolute w-64 h-64 rounded-full border border-primary-container/10 border-dashed"
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 40, ease: "linear" }}
              />
              <motion.div 
                className="absolute w-48 h-48 rounded-full border border-primary-container/20 border-dotted"
                animate={{ rotate: -360 }}
                transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
              />
              
              <div className="absolute w-32 h-32 rounded-full bg-primary-container/20 blur-[30px]" />
              
              <div className="w-24 h-24 rounded-full bg-black/90 backdrop-blur-3xl border border-primary-container/50 shadow-[0_0_50px_rgba(132,204,22,0.4),inset_0_0_20px_rgba(132,204,22,0.2)] flex items-center justify-center relative z-10">
                <motion.div 
                  className="w-12 h-12 rounded-full bg-primary-container blur-[10px] absolute"
                  animate={{ opacity: [0.4, 0.9, 0.4], scale: [0.8, 1.2, 0.8] }}
                  transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                />
                <Activity className="w-8 h-8 text-white relative z-10 drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
              </div>
              
              <div className="absolute -bottom-10 text-center whitespace-nowrap">
                <span className="text-primary-container font-bold tracking-widest uppercase text-xs drop-shadow-[0_0_8px_rgba(132,204,22,0.6)]">ODOOX GATEWAY</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
