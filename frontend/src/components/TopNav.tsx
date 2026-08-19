'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import SignOutButton from '@/components/SignOutButton';
import { cn } from '@/lib/utils';

interface TopNavProps {
  hasToken: boolean;
  isPaid: boolean;
}

export function TopNav({ hasToken, isPaid }: TopNavProps) {
  const [scrolled, setScrolled] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }

      // Hide if scrolling down and past 100px. Show if scrolling up.
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setHidden(true);
      } else {
        setHidden(false);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.nav 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: hidden ? -100 : 0, opacity: hidden ? 0 : 1 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={cn(
        "fixed left-1/2 -translate-x-1/2 z-50 transition-all duration-300 w-[95%] max-w-7xl rounded-full border border-white/10 flex justify-between items-center px-4 h-16",
        scrolled 
          ? "top-4 bg-black/60 backdrop-blur-3xl shadow-[0_20px_40px_rgba(0,0,0,0.5)]" 
          : "top-6 bg-white/5 backdrop-blur-xl shadow-lg"
      )}
    >
      {/* Left side: Logo & Badge */}
      <Link href="/" className="flex items-center hover:opacity-100 transition-opacity group z-10 shrink-0">
        <img 
          src="/logo.png" 
          alt="OdooX Logo" 
          className="h-10 w-auto object-contain"
        />
        <div className="hidden sm:flex items-center gap-1.5 ml-4 px-3 py-1 rounded-full border border-white/5 bg-white/[0.02] backdrop-blur-sm group-hover:bg-white/[0.05] group-hover:border-white/10 transition-all shadow-[0_0_10px_rgba(255,255,255,0.02)]">
          <span className="text-[8px] font-semibold text-white/40 uppercase tracking-widest">Powered by</span>
          <span className="text-[9px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-primary tracking-widest uppercase">Recognate</span>
        </div>
      </Link>

      {/* Center: Absolutely Centered Navigation Links */}
      <div className="hidden lg:flex absolute left-1/2 -translate-x-1/2 items-center gap-1 bg-white/[0.02] border border-white/5 p-1 rounded-full backdrop-blur-md shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
        <Link 
          className="px-6 py-2 text-xs font-semibold text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all" 
          href="#ecosystem"
        >
          Ecosystem
        </Link>
        <Link 
          className="px-6 py-2 text-xs font-semibold text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all" 
          href="#features"
        >
          Features
        </Link>
        <Link 
          className="px-6 py-2 text-xs font-semibold text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all" 
          href="#security"
        >
          Security
        </Link>
        <Link 
          className="px-6 py-2 text-xs font-semibold text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-all" 
          href="#pricing"
        >
          Pricing
        </Link>
      </div>
      
      {/* Right side: Auth Buttons */}
      <div className="flex items-center gap-2 z-10 shrink-0">
        {!hasToken ? (
          <>
            <Link 
              className="text-xs font-semibold text-white/60 hover:text-white px-5 py-2.5 transition-colors hidden md:block" 
              href="/login"
            >
              Log In
            </Link>
            <Link 
              className="bg-gradient-to-r from-primary-container to-primary text-black text-xs px-7 py-2.5 rounded-full font-bold hover:shadow-[0_0_20px_rgba(132,204,22,0.4)] transition-all" 
              href="/login"
            >
              Get Started
            </Link>
          </>
        ) : isPaid ? (
          <>
            <SignOutButton className="text-xs font-semibold text-white/60 hover:text-white px-5 py-2.5 transition-colors hidden md:block" />
            <Link 
              className="bg-gradient-to-r from-primary-container to-primary text-black text-xs px-7 py-2.5 rounded-full font-bold hover:shadow-[0_0_20px_rgba(132,204,22,0.4)] transition-all" 
              href="/userdashboard"
            >
              Dashboard
            </Link>
          </>
        ) : (
          <>
            <SignOutButton className="text-xs font-semibold text-white/60 hover:text-white px-5 py-2.5 transition-colors hidden md:block" />
            <Link 
              className="bg-gradient-to-r from-primary-container to-primary text-black text-xs px-7 py-2.5 rounded-full font-bold hover:shadow-[0_0_20px_rgba(132,204,22,0.4)] transition-all" 
              href="/payment"
            >
              Upgrade
            </Link>
          </>
        )}
      </div>
    </motion.nav>
  );
}
