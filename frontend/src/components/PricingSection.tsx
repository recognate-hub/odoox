'use client';

import React, { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Sparkles, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';

interface PricingProps {
  hasToken: boolean;
  isPaid: boolean;
}

export function PricingSection({ hasToken, isPaid }: PricingProps) {
  const [singlePrice, setSinglePrice] = useState<number | null>(null);

  useEffect(() => {
      const fetchPrices = async () => {
          try {
              const { data, error } = await supabase.from('app_config').select('*').in('key', ['single_plan_price']);
              if (data && !error) {
                  const single = data.find(d => d.key === 'single_plan_price');
                  if (single) setSinglePrice(parseFloat(single.value));
              }
          } catch (err) {
              console.error('Could not fetch dynamic prices');
          }
      };
      fetchPrices();
  }, []);

  // Determine the correct route and button text based on auth state
  let href = "/login";
  let buttonText = "Get Started / Login";
  
  if (hasToken) {
    if (isPaid) {
      href = "/userdashboard";
      buttonText = "Go to Dashboard";
    } else {
      href = "/payment";
      buttonText = "Unlock Lifetime Access";
    }
  }

  return (
    <section className="relative w-full py-32" id="pricing">
      {/* Ambient background glow for pricing */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(132,204,22,0.1),transparent_50%)] pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-6 space-y-16 relative">
        
        {/* Header */}
        <div className="text-center space-y-6 max-w-2xl mx-auto">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-bold tracking-tight text-white"
          >
            Simple, <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-primary">transparent pricing.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-white/50 text-lg md:text-xl"
          >
            Get 5 years of unrestricted access to the OdooX AI Gateway. No recurring bills, no surprises.
          </motion.p>
        </div>

        {/* Pricing Card */}
        <div className="max-w-lg mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            whileHover={{ y: -5 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="relative group"
          >
            {/* Animated gradient border */}
            <div className="absolute -inset-[1px] rounded-3xl bg-gradient-to-b from-primary-container/50 via-primary-container/10 to-transparent p-[1px] transition-all duration-500 group-hover:from-primary-container/80">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-container/30 to-transparent blur-md" />
            </div>

            <div className="relative rounded-[23px] bg-[#050505]/90 backdrop-blur-2xl p-8 md:p-12 overflow-hidden shadow-[0_0_50px_rgba(132,204,22,0.15)] group-hover:shadow-[0_0_80px_rgba(132,204,22,0.25)] transition-all duration-500">
              
              {/* Internal glow */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/10 blur-[100px] pointer-events-none group-hover:bg-primary-container/20 transition-all duration-500" />
              
              <div className="relative z-10 space-y-8">
                
                {/* Title & Badge */}
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-2xl font-bold text-white tracking-tight">Lifetime Pro Access</h3>
                    <p className="text-sm text-white/60 mt-2 leading-relaxed">Everything you need to seamlessly connect Claude to your Odoo ERP and automate your workflows.</p>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-gradient-to-r from-primary-container to-primary text-black text-[10px] font-bold tracking-[0.1em] uppercase shadow-[0_0_20px_rgba(132,204,22,0.6)] shrink-0">
                    <Sparkles className="w-3 h-3" /> Early Adopter
                  </div>
                </div>

                {/* Price */}
                <div className="bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-6 flex flex-col items-center relative shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-semibold text-primary-container/80 translate-y-[-8px]">₹</span>
                    <span className="text-6xl font-black text-white tracking-tighter drop-shadow-md">
                      {singlePrice === null ? '...' : singlePrice.toLocaleString()}
                    </span>
                  </div>
                  <div className="text-primary-container/80 text-xs mt-3 font-bold tracking-widest uppercase">One-time payment · 5 Years of Access</div>
                </div>

                {/* Features */}
                <ul className="space-y-4 pt-2">
                  {[
                    'Unlimited Claude MCP Queries',
                    'Connect 1 Production Database',
                    '12 Odoo Modules Supported',
                    'End-to-End Encrypted Secure Tunnel',
                    'Free Future Gateway Updates',
                    'Priority Community Support'
                  ].map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <div className="mt-0.5 bg-primary-container/20 rounded-full p-1 shrink-0">
                        <Check className="w-3.5 h-3.5 text-primary-container" />
                      </div>
                      <span className="text-white/80 text-sm font-medium">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <Link 
                  href={href} 
                  className="group/btn relative flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-primary-container to-primary px-6 py-4 text-black font-bold text-lg hover:opacity-90 transition-all duration-300 shadow-[0_0_20px_rgba(132,204,22,0.3)] glow-button"
                >
                  {buttonText}
                  <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                </Link>

              </div>
            </div>
          </motion.div>
        </div>

      </div>
    </section>
  );
}
