"use client";

import React from "react";
import Link from "next/link";
import SignOutButton from "@/components/SignOutButton";

interface NavbarProps {
  hasToken: boolean;
  isPaid: boolean;
}

export default function Navbar({ hasToken, isPaid }: NavbarProps) {
  return (
    <header className="fixed top-4 inset-x-0 z-50 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between px-4 sm:px-6 py-3 rounded-full border border-white/10 bg-black/70 backdrop-blur-xl shadow-2xl">
        <Link href="/" className="flex items-center gap-3 group shrink-0">
          <div className="relative flex items-center justify-center">
            <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-lime-500 to-emerald-500 opacity-40 blur group-hover:opacity-75 transition duration-300"></div>
            <img src="/logo.png" alt="OdooX" className="relative h-7 w-auto object-contain" />
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-lime-400 font-semibold tracking-wide">
            v2.4 MCP
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
          <a href="#playground" className="hover:text-white transition-colors">Demo</a>
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#tools" className="hover:text-white transition-colors">MCP Tools</a>
          <a href="#security" className="hover:text-white transition-colors">Security</a>
          <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
        </nav>

        <div className="flex items-center gap-3 shrink-0">
          {!hasToken ? (
            <>
              <Link href="/login" className="hidden sm:inline-block text-sm font-medium text-zinc-300 hover:text-white transition-colors px-3 py-1.5">
                Sign In
              </Link>
              <Link
                href="/login"
                className="relative inline-flex items-center justify-center px-4 sm:px-5 py-2 text-xs sm:text-sm font-semibold text-black transition-all bg-gradient-to-r from-lime-400 to-emerald-400 rounded-full hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(163,230,53,0.3)]"
              >
                Get Started
              </Link>
            </>
          ) : isPaid ? (
            <>
              <SignOutButton className="hidden sm:inline-block text-sm font-medium text-zinc-400 hover:text-white transition-colors px-3 py-1.5" />
              <Link
                href="/userdashboard"
                className="relative inline-flex items-center justify-center px-4 sm:px-5 py-2 text-xs sm:text-sm font-semibold text-black transition-all bg-gradient-to-r from-lime-400 to-emerald-400 rounded-full hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(163,230,53,0.3)]"
              >
                Dashboard →
              </Link>
            </>
          ) : (
            <>
              <SignOutButton className="hidden sm:inline-block text-sm font-medium text-zinc-400 hover:text-white transition-colors px-3 py-1.5" />
              <Link
                href="/payment"
                className="relative inline-flex items-center justify-center px-4 sm:px-5 py-2 text-xs sm:text-sm font-semibold text-black transition-all bg-gradient-to-r from-lime-400 to-emerald-400 rounded-full hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(163,230,53,0.3)]"
              >
                Complete Payment
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
