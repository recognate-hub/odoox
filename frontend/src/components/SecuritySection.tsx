'use client';

import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, Shield, BarChart2, FileText } from 'lucide-react';

const features = [
  {
    icon: Lock,
    title: "JWT Authentication",
    description: "Every SSE connection is authenticated via Bearer token or query parameter. No token, no access.",
    color: "from-blue-500/20 to-blue-500/0",
    iconColor: "text-blue-400"
  },
  {
    icon: Shield,
    title: "Policy-as-Code RBAC",
    description: "A declarative JSON policy engine controls which roles can execute which tools — and which Odoo models they can touch.",
    color: "from-green-500/20 to-green-500/0",
    iconColor: "text-green-400"
  },
  {
    icon: BarChart2,
    title: "Per-User Rate Limiting",
    description: "Redis-backed rate limiting with automatic in-memory fallback. 100 calls per 60-second window, per user.",
    color: "from-purple-500/20 to-purple-500/0",
    iconColor: "text-purple-400"
  },
  {
    icon: FileText,
    title: "Full Audit Trail",
    description: "Every tool invocation is logged with user ID, role, action, execution time, and success/failure status.",
    color: "from-orange-500/20 to-orange-500/0",
    iconColor: "text-orange-400"
  }
];

export function SecuritySection() {
  return (
    <section className="relative w-full py-24" id="security">
      <div className="max-w-7xl mx-auto px-6 space-y-16">
        
        {/* Header */}
        <div className="text-center space-y-6 max-w-3xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-bold tracking-widest uppercase mb-4"
          >
            <Shield className="w-4 h-4" /> Zero Trust Architecture
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-bold tracking-tight text-white"
          >
            Enterprise security is <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-200">not optional.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-white/50 text-lg md:text-xl"
          >
            Every single tool call passes through five layers of verification before touching your Odoo database. No exceptions.
          </motion.p>
        </div>

        {/* 2026 Security Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <SecurityCard key={i} feature={feature} index={i} />
          ))}
        </div>

      </div>
    </section>
  );
}

function SecurityCard({ feature, index }: { feature: any, index: number }) {
  const Icon = feature.icon;
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  // Spotlight hover effect
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (cardRef.current) {
      const rect = cardRef.current.getBoundingClientRect();
      setMousePosition({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      <div 
        ref={cardRef}
        onMouseMove={handleMouseMove}
        className="group relative h-full rounded-3xl bg-[#0a0a0a] border border-white/5 overflow-hidden p-8 hover:border-white/20 transition-colors"
      >
        {/* Dynamic Spotlight */}
        <div 
          className="absolute inset-0 z-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
          style={{
            background: `radial-gradient(circle 250px at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.03), transparent 80%)`
          }}
        />

        {/* Background Color Glow */}
        <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${feature.color} blur-3xl opacity-50 group-hover:opacity-100 transition-opacity duration-500`} />

        <div className="relative z-10 space-y-6">
          <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
            <Icon className={`w-6 h-6 ${feature.iconColor}`} />
          </div>
          
          <div className="space-y-3">
            <h3 className="text-xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-white/60 transition-all duration-300">
              {feature.title}
            </h3>
            <p className="text-white/50 leading-relaxed text-sm group-hover:text-white/70 transition-colors duration-300">
              {feature.description}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
