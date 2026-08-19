'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Kanban, CheckCircle2, Zap, FileText, PackageSearch, MessageSquare } from 'lucide-react';

// --- MOCK UI COMPONENTS ---

const baseMockupVariants = {
  initial: { opacity: 0, scale: 0.95, filter: 'blur(10px)' },
  animate: { opacity: 1, scale: 1, filter: 'blur(0px)' },
  exit: { opacity: 0, scale: 0.95, filter: 'blur(10px)' },
  transition: { duration: 0.4, ease: "easeOut" as const }
};

const CRMMockup = () => (
  <motion.div {...baseMockupVariants} className="w-full h-full relative flex items-center justify-center p-8">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(59,130,246,0.15),transparent_80%)] pointer-events-none" />
    <div className="relative w-full max-w-[500px] h-full max-h-[400px] bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl flex p-4 gap-3">
      <div className="flex-1 space-y-4">
        <div className="flex justify-between items-center px-1">
          <span className="text-white/50 text-[10px] font-bold uppercase tracking-wider">New</span>
        </div>
        <div className="w-full h-16 bg-white/5 rounded-xl border border-white/5" />
        <div className="w-full h-16 bg-white/5 rounded-xl border border-white/5" />
      </div>
      <div className="flex-1 space-y-4">
        <div className="flex justify-between items-center px-1">
          <span className="text-blue-400 text-[10px] font-bold uppercase tracking-wider">Qualified</span>
        </div>
        <div className="w-full h-16 bg-white/5 rounded-xl border border-white/5" />
      </div>
      <div className="flex-1 space-y-4 relative">
        <div className="flex justify-between items-center px-1">
          <span className="text-primary-container text-[10px] font-bold uppercase tracking-wider">Negotiation</span>
        </div>
        <div className="w-full h-16 bg-white/5 border border-dashed border-white/20 rounded-xl" />
        <motion.div 
          className="absolute top-8 left-0 w-full h-16 bg-[#171717] rounded-xl border border-primary-container/30 shadow-[0_10px_30px_rgba(132,204,22,0.2)] p-2 flex flex-col justify-between z-20"
          initial={{ x: "-210%", y: "115%", rotate: -2 }} 
          animate={{ x: 0, y: 0, rotate: 0 }}       
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3, ease: "easeInOut" }}
        >
          <div className="flex justify-between items-start">
            <div className="w-2/3 h-2 bg-white/80 rounded-full" />
            <span className="text-[8px] font-bold text-primary-container">$120k</span>
          </div>
          <div className="w-1/3 h-1.5 bg-white/30 rounded-full" />
        </motion.div>
      </div>
      <motion.div 
        className="absolute -bottom-6 -left-8 bg-black/90 backdrop-blur-2xl border border-white/10 p-3 rounded-2xl rounded-tl-none shadow-2xl z-30 max-w-[240px]"
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, delay: 1.8, repeat: Infinity, repeatDelay: 3.5 }}
      >
        <div className="flex gap-2">
          <div className="w-6 h-6 rounded-full bg-orange-500/20 border border-orange-500/50 flex items-center justify-center shrink-0">
            <span className="text-orange-500 text-[8px] font-black">AI</span>
          </div>
          <div>
            <p className="text-white/90 text-[10px] leading-relaxed">
              Moved the opportunity to <strong className="text-primary-container">Negotiation</strong>.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  </motion.div>
);

const SalesMockup = () => (
  <motion.div {...baseMockupVariants} className="w-full h-full relative flex items-center justify-center p-8">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(34,197,94,0.15),transparent_80%)] pointer-events-none" />
    <div className="relative w-full max-w-[450px] bg-white border border-white/10 rounded-xl shadow-2xl overflow-hidden text-black p-6 space-y-4">
      {/* Invoice Header */}
      <div className="flex justify-between items-start border-b border-gray-200 pb-4">
        <div>
          <div className="text-sm text-gray-500 font-bold uppercase tracking-widest">Invoice</div>
          <div className="text-2xl font-black text-gray-900">INV/2026/0042</div>
        </div>
        <motion.div 
          className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
          initial={{ backgroundColor: '#f3f4f6', color: '#6b7280' }}
          animate={{ backgroundColor: '#22c55e', color: '#ffffff' }}
          transition={{ delay: 2, duration: 0.5 }}
        >
          <motion.span initial={{ opacity: 1 }} animate={{ opacity: 0 }} transition={{ delay: 2, duration: 0.1 }} className="absolute">Draft</motion.span>
          <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.1, duration: 0.1 }}>Posted</motion.span>
        </motion.div>
      </div>
      {/* Lines */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-500 font-bold border-b border-gray-100 pb-1">
          <span>Description</span>
          <span>Amount</span>
        </div>
        <div className="flex justify-between text-sm font-medium">
          <span>Consulting Services</span>
          <span>$12,500.00</span>
        </div>
        <div className="flex justify-between text-sm font-medium text-gray-400">
          <span>Server Setup</span>
          <span>$3,200.00</span>
        </div>
      </div>
      <div className="pt-4 border-t border-gray-200 flex justify-end">
        <div className="text-xl font-black">$15,700.00</div>
      </div>
      {/* Action Overlay */}
      <motion.div 
        className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black text-white px-4 py-2 rounded-lg text-xs font-bold shadow-xl flex items-center gap-2"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 2.5, type: 'spring', stiffness: 200, damping: 20 }}
      >
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        Processing Payment via OdooX...
      </motion.div>
    </div>
  </motion.div>
);

const InventoryMockup = () => (
  <motion.div {...baseMockupVariants} className="w-full h-full relative flex items-center justify-center p-8">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(234,179,8,0.15),transparent_80%)] pointer-events-none" />
    <div className="relative w-full max-w-[500px] h-full max-h-[350px] bg-[#111111] border border-white/10 rounded-2xl shadow-2xl flex flex-col p-6 space-y-4">
      <div className="text-sm font-bold text-white/80 border-b border-white/10 pb-2">Bill of Materials: <span className="text-yellow-500">Pro Server Rack</span></div>
      
      {/* BOM Tree */}
      <div className="space-y-3 relative before:absolute before:inset-y-0 before:left-4 before:w-px before:bg-white/10">
        
        {/* Parent */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-yellow-500/20 border border-yellow-500/50 flex items-center justify-center">
            <PackageSearch className="w-4 h-4 text-yellow-500" />
          </div>
          <div className="flex-1">
            <div className="text-sm text-white font-medium">Pro Server Rack <span className="text-xs text-white/40 ml-2">x1</span></div>
          </div>
          <div className="text-xs text-yellow-500 bg-yellow-500/10 px-2 py-0.5 rounded">Build</div>
        </div>

        {/* Child 1 */}
        <motion.div 
          className="relative z-10 flex items-center gap-3 pl-8"
          initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}
        >
          <div className="w-6 h-6 rounded border border-white/20 bg-white/5 flex items-center justify-center">
            <div className="w-3 h-3 bg-white/20 rounded-sm" />
          </div>
          <div className="flex-1"><div className="text-xs text-white/80">Steel Frame <span className="text-xs text-white/40 ml-2">x1</span></div></div>
          <div className="text-xs text-green-400">In Stock: 42</div>
        </motion.div>

        {/* Child 2 */}
        <motion.div 
          className="relative z-10 flex items-center gap-3 pl-8"
          initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.8 }}
        >
          <div className="w-6 h-6 rounded border border-white/20 bg-white/5 flex items-center justify-center">
            <div className="w-3 h-3 bg-white/20 rounded-sm" />
          </div>
          <div className="flex-1"><div className="text-xs text-white/80">Cooling Unit <span className="text-xs text-white/40 ml-2">x2</span></div></div>
          <div className="text-xs text-red-400">Shortage: -1</div>
        </motion.div>

        {/* AI Action */}
        <motion.div 
          className="relative z-10 pl-8 mt-4"
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 2 }}
        >
          <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 flex gap-3 items-start">
            <div className="w-5 h-5 rounded-full bg-orange-500 flex items-center justify-center shrink-0 mt-0.5">
              <span className="text-white text-[8px] font-black">AI</span>
            </div>
            <div className="text-xs text-white/80 leading-relaxed">
              Detected a shortage of Cooling Units. Initiated `create_stock_move` from WH/Stock/Components to reserve inventory.
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  </motion.div>
);

const DiscussMockup = () => (
  <motion.div {...baseMockupVariants} className="w-full h-full relative flex items-center justify-center p-8">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(236,72,153,0.15),transparent_80%)] pointer-events-none" />
    <div className="relative w-full max-w-[400px] h-[450px] bg-[#0d0d0d] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
      <div className="p-4 border-b border-white/10 bg-white/5">
        <div className="text-sm font-bold text-white">Chatter: crm.lead #1042</div>
        <div className="text-xs text-white/40">Acme Corp Website Redesign</div>
      </div>
      <div className="flex-1 p-4 space-y-4 overflow-hidden relative flex flex-col justify-end">
        {/* User Message */}
        <div className="flex gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0 border border-blue-500/30">
            <span className="text-blue-400 text-[10px] font-bold">JD</span>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none p-3 text-xs text-white/80">
            Did the client send the signed NDA yet? Can someone check?
          </div>
        </div>
        
        {/* Claude Typing... */}
        <motion.div 
          className="flex gap-3"
          initial={{ opacity: 1 }} animate={{ opacity: 0, display: 'none' }} transition={{ delay: 2 }}
        >
          <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center shrink-0 border border-orange-500/30">
            <span className="text-orange-500 text-[10px] font-black">AI</span>
          </div>
          <div className="bg-orange-500/10 border border-orange-500/20 rounded-2xl rounded-tl-none p-3 flex items-center gap-1">
            <motion.div className="w-1.5 h-1.5 bg-orange-500/50 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} />
            <motion.div className="w-1.5 h-1.5 bg-orange-500/50 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
            <motion.div className="w-1.5 h-1.5 bg-orange-500/50 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
          </div>
        </motion.div>

        {/* Claude Message */}
        <motion.div 
          className="flex gap-3"
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 2.1 }}
        >
          <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center shrink-0 border border-orange-500/30">
            <span className="text-orange-500 text-[10px] font-black">AI</span>
          </div>
          <div className="bg-orange-500/10 border border-orange-500/20 rounded-2xl rounded-tl-none p-3 text-xs text-white/90">
            Yes, I checked the attachments via `get_attachment`. The signed NDA was uploaded 2 hours ago. I have updated the lead status.
          </div>
        </motion.div>
      </div>
      <div className="p-3 border-t border-white/10 bg-white/5">
        <div className="w-full h-8 bg-white/5 rounded-full border border-white/10 flex items-center px-3">
          <span className="text-[10px] text-white/30">Type a message...</span>
        </div>
      </div>
    </div>
  </motion.div>
);

const ToolkitMockup = () => (
  <motion.div {...baseMockupVariants} className="w-full h-full relative flex items-center justify-center p-8">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(168,85,247,0.15),transparent_80%)] pointer-events-none" />
    <div className="relative w-full max-w-[500px] h-full max-h-[380px] bg-[#050505] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 bg-[#0a0a0a] border-b border-white/5 shrink-0">
        <div className="flex gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
          <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
          <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
        </div>
        <span className="ml-2 text-white/40 text-[10px] font-mono tracking-widest uppercase">odoox-tracer — active</span>
      </div>
      
      <div className="p-4 font-mono text-[10px] space-y-2 relative flex-1">
        {[
          { time: '10:42:01.05', type: 'INFO', msg: 'Incoming request via generic toolkit' },
          { time: '10:42:01.07', type: 'AUTH', msg: 'JWT Verified [role=admin]' },
          { time: '10:42:01.08', type: 'RBAC', msg: 'Policy allows access to model: fleet.vehicle' },
        ].map((log, i) => (
          <motion.div key={i} className="flex gap-2 text-white/50" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.2 }}>
            <span className="hidden sm:inline">[{log.time}]</span>
            <span className={log.type === 'AUTH' ? 'text-yellow-400' : log.type === 'RBAC' ? 'text-purple-400' : 'text-blue-400'}>[{log.type}]</span>
            <span className="truncate">{log.msg}</span>
          </motion.div>
        ))}

        <motion.div 
          className="mt-4 flex flex-col sm:flex-row gap-1 sm:gap-4 text-primary-container font-bold bg-primary-container/10 p-2 rounded border border-primary-container/20 overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.0 }}
        >
          <span className="hidden sm:inline">[EXEC]</span>
          <span className="truncate">search_read fleet.vehicle</span>
        </motion.div>

        <div className="mt-2 pl-2 space-y-1 overflow-hidden h-24 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#050505] z-10" />
          {[...Array(6)].map((_, i) => (
            <motion.div key={`data-${i}`} className="text-white/40 truncate text-[8px]" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: -40 }} transition={{ duration: 2, delay: 1.2 + (i * 0.1), repeat: Infinity, ease: "linear" }}>
              {`{"id": ${100 + i}, "license_plate": "XYZ-${900 + i}", "model": "Tesla Model 3"}`}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  </motion.div>
);


// --- MAIN COMPONENT ---

export function FeatureShowcaseSection() {
  const [activeTab, setActiveTab] = useState(0);

  const featureContent = [
    {
      tabTitle: "CRM",
      title: <>CRM that works <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-200">while you sleep.</span></>,
      icon: <Kanban className="w-6 h-6" />,
      iconBg: "bg-blue-500/10 border-blue-500/20 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.2)]",
      bullets: ["Search and filter leads by name, stage, or expected revenue.", "Create, update, and log internal notes on opportunities.", "Aggregate funnel metrics grouped dynamically."],
      Mockup: CRMMockup
    },
    {
      tabTitle: "Sales",
      title: <>Automate <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-200">Sales & Invoicing.</span></>,
      icon: <FileText className="w-6 h-6" />,
      iconBg: "bg-green-500/10 border-green-500/20 text-green-400 shadow-[0_0_15px_rgba(34,197,94,0.2)]",
      bullets: ["Create customer quotes and add order lines automatically.", "Draft, post, and register payments for invoices.", "Retrieve entire quoting history for any partner."],
      Mockup: SalesMockup
    },
    {
      tabTitle: "Inventory",
      title: <>Manage your <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-200">Inventory & Mfg.</span></>,
      icon: <PackageSearch className="w-6 h-6" />,
      iconBg: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400 shadow-[0_0_15px_rgba(234,179,8,0.2)]",
      bullets: ["Check real-time stock availability across warehouses.", "Create manufacturing orders and manage Bills of Materials.", "Process automated stock moves and value inventory."],
      Mockup: InventoryMockup
    },
    {
      tabTitle: "Chatter",
      title: <>Talk to your <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-pink-200">Chatter & Comms.</span></>,
      icon: <MessageSquare className="w-6 h-6" />,
      iconBg: "bg-pink-500/10 border-pink-500/20 text-pink-400 shadow-[0_0_15px_rgba(236,72,153,0.2)]",
      bullets: ["Read and post messages on any record's chatter.", "Create Discuss channels and read message history.", "Send automated outbound emails directly from Claude."],
      Mockup: DiscussMockup
    },
    {
      tabTitle: "Toolkit",
      title: <>The generic <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-purple-200">toolkit.</span></>,
      icon: <Zap className="w-6 h-6" />,
      iconBg: "bg-purple-500/10 border-purple-500/20 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.2)]",
      bullets: ["Read and write any permitted Odoo model.", "Batch create and update tools optimized for bulk.", "Execute powerful server workflow methods."],
      Mockup: ToolkitMockup
    }
  ];

  return (
    <section className="relative w-full py-24" id="features">
      <div className="max-w-7xl mx-auto px-6 relative space-y-16">
        
        {/* Section Header */}
        <div className="text-center space-y-6">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-white">
            A module for <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-blue-400">every workflow.</span>
          </h2>
          <p className="text-white/50 text-lg md:text-xl max-w-2xl mx-auto">
            OdooX securely connects Claude to 14 different Odoo applications, giving you an end-to-end ERP copilot.
          </p>
        </div>

        {/* Interactive Tab Bar */}
        <div className="flex justify-start md:justify-center overflow-x-auto pb-4 scrollbar-hide -mx-6 px-6 md:mx-0 md:px-0">
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 p-2 rounded-2xl w-max">
            {featureContent.map((f, i) => {
              const isActive = activeTab === i;
              return (
                <button
                  key={i}
                  onClick={() => setActiveTab(i)}
                  className={`relative flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-medium transition-colors ${
                    isActive ? "text-white" : "text-white/40 hover:text-white/80"
                  }`}
                >
                  {isActive && (
                    <motion.div 
                      layoutId="activeTabIndicator"
                      className="absolute inset-0 bg-white/10 border border-white/10 rounded-xl"
                      transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                  )}
                  <span className="relative z-10 flex items-center gap-2">
                    <span className={isActive ? "" : "opacity-50 grayscale"}>{f.icon}</span>
                    {f.tabTitle}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Area (2-Column Grid) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center bg-[#050505] border border-white/5 rounded-[40px] p-6 lg:p-12 shadow-2xl">
          
          {/* Left Column: Text Content */}
          <div className="lg:col-span-5 h-[400px] flex flex-col justify-center">
            <AnimatePresence mode="wait">
              <motion.div 
                key={activeTab}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                className="space-y-8"
              >
                <h3 className="text-4xl xl:text-5xl font-bold text-white tracking-tight leading-tight">
                  {featureContent[activeTab].title}
                </h3>
                
                <ul className="space-y-4">
                  {featureContent[activeTab].bullets.map((b, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <div className="mt-1 bg-white/5 rounded-full p-1 shrink-0"><CheckCircle2 className="w-4 h-4 text-white/50" /></div>
                      <span className="text-white/80 text-lg leading-relaxed">{b}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Right Column: Morphing Mockup */}
          <div className="lg:col-span-7 h-[450px] lg:h-[600px] w-full relative">
            <div className="w-full h-full rounded-3xl bg-black/40 border border-white/5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_30px_60px_rgba(0,0,0,0.5)] overflow-hidden relative">
              
              {/* Top Dashboard Bar */}
              <div className="absolute top-0 inset-x-0 h-12 border-b border-white/5 bg-white/[0.02] flex items-center px-6 z-50">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <div className="mx-auto px-4 py-1 rounded-full bg-white/5 text-[10px] text-white/40 font-mono flex items-center gap-2 tracking-widest uppercase">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse" />
                  ODOOX_RUNTIME — {featureContent[activeTab].tabTitle}
                </div>
              </div>

              {/* The Morphing Canvas Area */}
              <div className="absolute inset-0 pt-12">
                <AnimatePresence mode="wait">
                  {activeTab === 0 && <CRMMockup key="0" />}
                  {activeTab === 1 && <SalesMockup key="1" />}
                  {activeTab === 2 && <InventoryMockup key="2" />}
                  {activeTab === 3 && <DiscussMockup key="3" />}
                  {activeTab === 4 && <ToolkitMockup key="4" />}
                </AnimatePresence>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
