'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion';
import { 
  Kanban, ShoppingCart, Package, Factory, 
  FileText, Wrench, Users, BarChart2,
  Database, GitMerge, Globe, ShieldAlert,
  Activity, ArrowRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

const modules = [
  // Left Side
  { id: 'sales', label: 'Sales', icon: ShoppingCart, x: 12, y: 30 },
  { id: 'crm', label: 'CRM', icon: Kanban, x: 8, y: 55 },
  { id: 'dashboards', label: 'Dashboards', icon: BarChart2, x: 18, y: 80 },
  { id: 'website', label: 'Website', icon: Globe, x: 28, y: 45 },
  { id: 'contacts', label: 'Contacts', icon: Users, x: 32, y: 68 },

  // Right Side
  { id: 'workflows', label: 'Workflows', icon: GitMerge, x: 88, y: 30 },
  { id: 'inventory', label: 'Inventory', icon: Package, x: 92, y: 55 },
  { id: 'invoicing', label: 'Invoicing', icon: FileText, x: 82, y: 80 },
  { id: 'security', label: 'Security', icon: ShieldAlert, x: 72, y: 45 },
  { id: 'manufacturing', label: 'Manufacturing', icon: Factory, x: 68, y: 68 },

  // Bottom Center
  { id: 'purchase', label: 'Purchase', icon: Wrench, x: 42, y: 85 },
  { id: 'models', label: 'Models', icon: Database, x: 58, y: 85 },
];

export function ModuleEcosystemSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Parallax mouse tracking
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth springs for the parallax movement
  const springConfig = { damping: 25, stiffness: 150 };
  const smoothMouseX = useSpring(mouseX, springConfig);
  const smoothMouseY = useSpring(mouseY, springConfig);

  // Background layer parallax (moves opposite to mouse, softly)
  const bgX = useTransform(smoothMouseX, [-500, 500], [15, -15]);
  const bgY = useTransform(smoothMouseY, [-500, 500], [15, -15]);

  // Foreground layer parallax (moves with mouse, aggressively)
  const fgX = useTransform(smoothMouseX, [-500, 500], [-30, 30]);
  const fgY = useTransform(smoothMouseY, [-500, 500], [-30, 30]);

  // SVG lines parallax (middle ground)
  const svgX = useTransform(smoothMouseX, [-500, 500], [-10, 10]);
  const svgY = useTransform(smoothMouseY, [-500, 500], [-10, 10]);

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
      className="relative w-full h-[700px] overflow-hidden flex items-center justify-center cursor-crosshair"
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Background Deep Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(132,204,22,0.03)_0%,transparent_70%)] pointer-events-none" />

      {/* Header Info (Stays fixed at top) */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 text-center space-y-4 z-50 pointer-events-none w-full max-w-3xl px-6">
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white drop-shadow-[0_4px_10px_rgba(0,0,0,0.5)]">
          40+ tools across <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-primary">13 Odoo modules.</span>
        </h2>
        <p className="text-white/60 text-sm md:text-base font-mono">
          Hover over nodes to explore the ecosystem
        </p>
      </div>

      {/* PARALLAX LAYER 1: The Connecting SVG Lines */}
      <motion.div 
        className="absolute inset-0 z-10 pointer-events-none"
        style={{ x: svgX, y: svgY }}
      >
        <svg className="w-full h-full">
          <defs>
            <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(132,204,22,0.5)" />
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
                {/* Base line */}
                <line 
                  x1="50%" y1="50%" 
                  x2={`${mod.x}%`} y2={`${mod.y}%`}
                  stroke="rgba(255,255,255,0.05)"
                  strokeWidth="1"
                />
                
                {/* Animated Data Packet (only when hovered) */}
                {isHovered && (
                  <motion.circle
                    r="3"
                    fill="#84cc16"
                    filter="url(#glow)"
                  >
                    <animateMotion
                      dur="1s"
                      repeatCount="indefinite"
                      path={`M ${window.innerWidth/2} ${window.innerHeight/2} L ${(window.innerWidth * mod.x) / 100} ${(window.innerHeight * mod.y) / 100}`}
                    />
                  </motion.circle>
                )}

                {/* Hover Highlight Line */}
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

      {/* PARALLAX LAYER 2: The Orbital Nodes */}
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
              {/* The Node */}
              <motion.div 
                className={cn(
                  "relative flex flex-col items-center justify-center gap-2 transition-all duration-300",
                  isFaded && "opacity-20 scale-95 grayscale"
                )}
                animate={{ 
                  y: [0, -5, 0],
                }}
                transition={{ 
                  duration: 4, 
                  repeat: Infinity, 
                  ease: "easeInOut",
                  delay: mod.x * 0.05 // Randomize floating phase
                }}
              >
                {/* Node Orb */}
                <div className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center border backdrop-blur-md transition-all duration-300 relative z-10",
                  isHovered 
                    ? "bg-primary-container/20 border-primary-container shadow-[0_0_30px_rgba(132,204,22,0.4)] scale-125" 
                    : "bg-white/[0.03] border-white/10 hover:border-white/30"
                )}>
                  <mod.icon className={cn(
                    "w-5 h-5 transition-colors duration-300",
                    isHovered ? "text-primary-container drop-shadow-[0_0_8px_rgba(132,204,22,1)]" : "text-white/40"
                  )} />
                </div>
                
                {/* Node Label */}
                <span className={cn(
                  "text-xs font-medium tracking-wide transition-colors duration-300 absolute -bottom-6 whitespace-nowrap",
                  isHovered ? "text-white drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]" : "text-white/30"
                )}>
                  {mod.label}
                </span>

                {/* Tooltip Popover */}
                <AnimatePresence>
                  {isHovered && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10, scale: 0.9 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 5, scale: 0.95 }}
                      className="absolute top-full left-1/2 -translate-x-1/2 mt-8 w-48 bg-black/80 backdrop-blur-2xl border border-primary-container/30 rounded-xl p-4 shadow-2xl z-50 pointer-events-none"
                    >
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-black/80 border-t border-l border-primary-container/30 rotate-45" />
                      <div className="relative z-10">
                        <h4 className="text-primary-container font-bold text-sm mb-1">{mod.label} Tools</h4>
                        <p className="text-white/60 text-xs">Access endpoints, run workflows, and aggregate {mod.label.toLowerCase()} records securely.</p>
                        <div className="mt-3 flex items-center gap-1 text-[10px] text-white/40 uppercase tracking-widest font-mono">
                          <Activity className="w-3 h-3" /> System Ready
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

      {/* PARALLAX LAYER 3: The Central Gateway Nexus */}
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
          {/* Outer Pulsing Rings */}
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
          
          {/* Inner Glow */}
          <div className="absolute w-32 h-32 rounded-full bg-primary-container/20 blur-[30px]" />
          
          {/* The Core Nexus */}
          <div className="w-24 h-24 rounded-full bg-black/90 backdrop-blur-3xl border border-primary-container/50 shadow-[0_0_50px_rgba(132,204,22,0.3),inset_0_0_20px_rgba(132,204,22,0.2)] flex items-center justify-center relative z-10">
            <motion.div 
              className="w-12 h-12 rounded-full bg-primary-container blur-[10px] absolute"
              animate={{ opacity: [0.4, 0.8, 0.4], scale: [0.8, 1.2, 0.8] }}
              transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
            />
            <Activity className="w-8 h-8 text-white relative z-10 drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
          </div>
          
          {/* Core Label */}
          <div className="absolute -bottom-12 text-center whitespace-nowrap">
            <span className="text-primary-container font-bold tracking-widest uppercase text-sm drop-shadow-[0_0_8px_rgba(132,204,22,0.5)]">OdooX Gateway</span>
          </div>
        </div>
      </motion.div>

    </section>
  );
}
