'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';

export function Footer() {
  return (
    <footer className="relative w-full border-t border-white/5 bg-[#030303] overflow-hidden pt-24 pb-12 mt-32">
      
      {/* Background Ambient Glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary-container/10 blur-[150px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10 space-y-16">
        
        {/* Top Section: Giant Brand Logo */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-8 border-b border-white/5 pb-16">
          <Link href="/" className="hover:opacity-80 transition-opacity">
            <img 
              src="/logo.png" 
              alt="OdooX Logo" 
              className="h-12 w-auto object-contain"
            />
            <div className="mt-2 text-white/40 text-sm max-w-sm">
              The missing Model Context Protocol gateway. Connect Claude to your entire Odoo ERP stack securely.
            </div>
          </Link>
          
          <div className="flex gap-4">
            {['Twitter', 'GitHub', 'Discord'].map((social) => (
              <a 
                key={social}
                href="#" 
                className="w-12 h-12 rounded-full border border-white/10 bg-white/5 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all"
              >
                <span className="text-xs font-bold">{social[0]}</span>
              </a>
            ))}
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4">
          <div className="space-y-4">
            <h4 className="text-white font-bold text-sm tracking-widest uppercase">Product</h4>
            <div className="flex flex-col gap-3">
              <Link href="#features" className="text-white/50 hover:text-white transition-colors text-sm">Features</Link>
              <Link href="#ecosystem" className="text-white/50 hover:text-white transition-colors text-sm">Ecosystem</Link>
              <Link href="#security" className="text-white/50 hover:text-white transition-colors text-sm">Security</Link>
              <Link href="#pricing" className="text-white/50 hover:text-white transition-colors text-sm">Pricing</Link>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="text-white font-bold text-sm tracking-widest uppercase">Developers</h4>
            <div className="flex flex-col gap-3">
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Documentation</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">API Reference</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm flex items-center gap-2">
                Status <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              </Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">GitHub</Link>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-white font-bold text-sm tracking-widest uppercase">Company</h4>
            <div className="flex flex-col gap-3">
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">About Recognate</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Blog</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Careers</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Contact</Link>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-white font-bold text-sm tracking-widest uppercase">Legal</h4>
            <div className="flex flex-col gap-3">
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Privacy Policy</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Terms of Service</Link>
              <Link href="#" className="text-white/50 hover:text-white transition-colors text-sm">Cookie Policy</Link>
            </div>
          </div>
        </div>

        {/* Bottom Copyright */}
        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-white/40">
          <div>
            © {new Date().getFullYear()} Recognate. All rights reserved.
          </div>
          <div>
            OdooX is not affiliated with, endorsed by, or sponsored by Odoo S.A.
          </div>
        </div>

      </div>
    </footer>
  );
}
