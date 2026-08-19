import React from 'react';
import Link from 'next/link';
import { cookies } from 'next/headers';
import { GlassHero } from '@/components/GlassHero';
import { TopNav } from '@/components/TopNav';
import { ModuleEcosystemSection } from '@/components/ModuleEcosystemSection';
import { FeatureShowcaseSection } from '@/components/FeatureShowcaseSection';
import { ClaudeConnectionSection } from '@/components/ClaudeConnectionSection';
import { SecuritySection } from '@/components/SecuritySection';
import { PricingSection } from '@/components/PricingSection';
import { Footer } from '@/components/Footer';
import { 
  Plug, Shield, MessageSquare, 
  Kanban, CheckCircle2, BarChart2, Check, Zap, Lock, 
  Factory, ShoppingCart, Users, FileText, Package, Wrench
} from 'lucide-react';

export default async function Home() {
  const cookieStore = await cookies();
  const hasToken = cookieStore.has('access_token');
  const isPaid = cookieStore.get('is_paid')?.value === 'true';

  return (
    <div className="font-body-md text-body-md antialiased overflow-x-hidden selection:bg-primary-container selection:text-black">
      {/* Ambient Background Glows */}
      <div className="fixed inset-0 z-[-1] pointer-events-none bg-grid-pattern opacity-20"></div>
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-container/10 blur-[120px] z-[-1] pointer-events-none"></div>
      <div className="fixed bottom-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-primary-container/5 blur-[100px] z-[-1] pointer-events-none"></div>

      {/* 1. TopNavBar */}
      <TopNav hasToken={hasToken} isPaid={isPaid} />

      {/* Hero Section - Full Width */}
      <section className="relative w-full pt-20 pb-10">
        <GlassHero hasToken={hasToken} isPaid={isPaid} />
      </section>

      {/* Main Content Wrapper */}
      <main className="pb-24 px-margin-safe max-w-container-max mx-auto space-y-[120px]">

        {/* 4. Module Ecosystem Bento */}
        <ModuleEcosystemSection />

        {/* 5. Feature Showcase Cinematic Boards */}
        <FeatureShowcaseSection />

        {/* Claude Connection Instructions */}
        <ClaudeConnectionSection />

        {/* Security Section */}
        <SecuritySection />

        {/* Pricing Section */}
        <PricingSection hasToken={hasToken} isPaid={isPaid} />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
