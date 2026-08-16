"use client";

import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const features = [
  {
    title: "Autonomous Sales Pipelines",
    description: "Expose create_lead, update_lead, and get_leads directly to Claude. Let AI agents manage your pipeline automatically through secure MCP routes.",
    code: `Claude > Call tool: create_lead\n\n{\n  "name": "Enterprise Deal",\n  "email": "ceo@acme.com"\n}\n\nOdooX > Lead #145 Created.`
  },
  {
    title: "Real-time Operations AI",
    description: "Grant instant access to inventory and calendar. Ask Claude to analyze stock levels, predict shortages dynamically, and autonomously book appointments.",
    code: `Claude > Call tool: get_products\n\n{\n  "domain": [["qty_available", "<", 10]]\n}\n\nOdooX > Returned 3 low-stock items.`
  },
  {
    title: "Universal Compatibility",
    description: "Zero setup. Works perfectly with Odoo v12 through v17 using standard XML-RPC. No custom modules required on your server.",
    code: `Version: Odoo 16.0 Enterprise\nProtocol: XML-RPC\nLatency: 42ms\nStatus: Connected flawlessly.`
  }
];

export default function StickyFeatures() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Calculate opacity and y for text blocks based on scroll progress (0 to 1)
  // We have 3 features.
  // F1 active: 0 - 0.33
  // F2 active: 0.33 - 0.66
  // F3 active: 0.66 - 1.0

  return (
    <section ref={containerRef} className="relative w-full h-[300vh] bg-[#0a0a0a]" id="features">
      {/* Sticky Container */}
      <div className="sticky top-0 h-screen w-full flex items-center overflow-hidden">
        <div className="max-w-7xl mx-auto w-full px-6 flex flex-col md:flex-row items-center gap-16 relative">
          
          {/* Left Text Column */}
          <div className="w-full md:w-1/2 flex flex-col justify-center relative h-[300px]">
            {features.map((feature, index) => {
              const start = index / features.length;
              const end = (index + 1) / features.length;
              const fadeStart = start - 0.1;
              const fadeEnd = end + 0.1;

              // eslint-disable-next-line react-hooks/rules-of-hooks
              const opacity = useTransform(
                scrollYProgress,
                [fadeStart, start, end - 0.1, fadeEnd],
                [0, 1, 1, 0]
              );

              // eslint-disable-next-line react-hooks/rules-of-hooks
              const y = useTransform(
                scrollYProgress,
                [fadeStart, start, end - 0.1, fadeEnd],
                [40, 0, 0, -40]
              );

              // eslint-disable-next-line react-hooks/rules-of-hooks
              const pointerEvents = useTransform(
                scrollYProgress,
                (v) => (v >= start && v <= end) ? 'auto' : 'none'
              );

              return (
                <motion.div 
                  key={index}
                  style={{ opacity, y, pointerEvents }}
                  className="absolute inset-0 flex flex-col justify-center"
                >
                  <h3 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">
                    {feature.title}
                  </h3>
                  <p className="text-xl text-zinc-400 leading-relaxed max-w-lg">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>

          {/* Right Visual Column (Mock Terminal) */}
          <div className="w-full md:w-1/2 h-[400px] relative rounded-2xl border border-white/10 bg-[#0f0f0f] shadow-2xl overflow-hidden backdrop-blur-md">
            <div className="absolute top-0 w-full h-12 border-b border-white/10 bg-black/40 flex items-center px-4 gap-2">
               <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
               <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
               <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
               <div className="ml-4 text-xs font-mono text-zinc-500">mcp-server-odoo</div>
            </div>
            
            <div className="p-6 pt-16 h-full w-full relative">
               {features.map((feature, index) => {
                  const start = index / features.length;
                  const end = (index + 1) / features.length;
                  
                  // eslint-disable-next-line react-hooks/rules-of-hooks
                  const opacity = useTransform(
                    scrollYProgress,
                    [start - 0.1, start, end - 0.1, end + 0.1],
                    [0, 1, 1, 0]
                  );

                  return (
                    <motion.div
                       key={index}
                       style={{ opacity }}
                       className="absolute inset-x-6 top-16"
                    >
                       <pre className="font-mono text-sm leading-relaxed whitespace-pre-wrap">
                         {feature.code.split('\n').map((line, i) => {
                           if (line.startsWith('Claude >')) return <div key={i} className="text-lime-400 mb-2">{line}</div>;
                           if (line.startsWith('OdooX >')) return <div key={i} className="text-blue-400 mt-2">{line}</div>;
                           if (line.includes('{') || line.includes('}')) return <div key={i} className="text-zinc-500">{line}</div>;
                           if (line.includes(':')) {
                             const [key, val] = line.split(':');
                             return <div key={i}><span className="text-pink-400">{key}:</span><span className="text-amber-200">{val}</span></div>;
                           }
                           return <div key={i} className="text-zinc-300 pl-4">{line}</div>;
                         })}
                       </pre>
                    </motion.div>
                  )
               })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
