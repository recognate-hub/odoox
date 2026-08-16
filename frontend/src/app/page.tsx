import React from 'react';
import Link from "next/link";
import { cookies } from "next/headers";
import SignOutButton from "@/components/SignOutButton";
import HeroSection from './HeroSection';
import StickyFeatures from './StickyFeatures';
import ModernBento from './ModernBento';

export default async function Home() {
  const cookieStore = await cookies();
  const hasToken = cookieStore.has('access_token');
  const isPaid = cookieStore.get('is_paid')?.value === 'true';

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-50 font-sans selection:bg-lime-500/30">
      
      {/* Premium Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-black/40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <img src="/logo.png" alt="OdooX" className="h-8 w-auto opacity-90 hover:opacity-100 transition-opacity" />
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium">
            {!hasToken ? (
              <>
                <Link href="/login" className="text-zinc-400 hover:text-white transition-colors">Login</Link>
                <Link href="/login" className="bg-white text-black px-4 py-2 rounded-full hover:scale-105 transition-transform">Get Started</Link>
              </>
            ) : isPaid ? (
              <>
                <SignOutButton className="text-zinc-400 hover:text-white transition-colors" />
                <Link href="/userdashboard" className="bg-white text-black px-4 py-2 rounded-full hover:scale-105 transition-transform">Dashboard</Link>
              </>
            ) : (
              <>
                <SignOutButton className="text-zinc-400 hover:text-white transition-colors" />
                <Link href="/payment" className="bg-lime-400 text-black px-4 py-2 rounded-full hover:scale-105 transition-transform shadow-[0_0_20px_rgba(163,230,53,0.3)]">Complete Payment</Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="relative z-10 flex flex-col items-center w-full">
        <HeroSection hasToken={hasToken} isPaid={isPaid} />
        <StickyFeatures />
        <ModernBento />
        
        {/* World-Class CTA */}
        <section className="w-full max-w-5xl mx-auto py-32 px-6 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-lime-500/5 blur-3xl pointer-events-none rounded-full" />
          <div className="relative border border-white/10 bg-white/[0.02] backdrop-blur-2xl rounded-3xl p-16 text-center shadow-2xl flex flex-col items-center overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-px bg-gradient-to-r from-transparent via-lime-500/50 to-transparent" />
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">Connect Claude to your ERP today.</h2>
            <p className="text-zinc-400 text-lg mb-10 max-w-xl">No native Python modules required. Start querying your production data natively through the Model Context Protocol in 3 minutes.</p>
            {!hasToken ? (
                <Link href="/login" className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-all shadow-[0_0_30px_rgba(255,255,255,0.2)]">
                  Start Building Now
                </Link>
            ) : (
                <Link href="/userdashboard" className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-all shadow-[0_0_30px_rgba(255,255,255,0.2)]">
                  Go to Dashboard
                </Link>
            )}
          </div>
        </section>
      </main>

      <footer className="w-full border-t border-white/5 bg-black py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <img src="/logo.png" alt="OdooX" className="h-6 opacity-50 grayscale" />
          <div className="flex gap-6 text-sm text-zinc-500">
            <span>© 2026 Recognate</span>
            <Link href="#" className="hover:text-zinc-300">Terms</Link>
            <Link href="#" className="hover:text-zinc-300">Privacy</Link>
          </div>
        </div>
      </footer>
      
      {/* AEO: JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "OdooX",
            "operatingSystem": "Web, Windows, macOS",
            "applicationCategory": "BusinessApplication",
            "description": "Securely connect Claude AI and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol.",
            "offers": {
              "@type": "Offer",
              "price": "49.00",
              "priceCurrency": "USD"
            }
          })
        }}
      />
    </div>
  );
}
