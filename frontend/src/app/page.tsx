import React from 'react';
import styles from "./Home.module.css";
import Link from "next/link";
import { cookies } from "next/headers";
import SignOutButton from "@/components/SignOutButton";

export default async function Home() {
  const cookieStore = await cookies();
  const hasToken = cookieStore.has('access_token');
  const isPaid = cookieStore.get('is_paid')?.value === 'true';

  return (
    <div className={styles.container}>
      {/* Dynamic Background with subtle glow */}
      <div className={styles.background}>
        <div className={styles.ambientGlow}></div>
        <div className={styles.glowOrb1}></div>
        <div className={styles.glowOrb2}></div>
        <div className={styles.gridPattern}></div>
      </div>
      
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.brand}>
            <Link href="/">
                <img src="/logo.png" alt="OdooX - The Enterprise AI Gateway for Odoo ERP" style={{ height: '36px', width: 'auto' }} />
            </Link>
          </div>
          <nav className={styles.nav}>

            {!hasToken ? (
              <>
                <Link href="/login" className={styles.navLink}>Login</Link>
                <Link href="/login" className={styles.primaryButtonSmall}>Get Started</Link>
              </>
            ) : isPaid ? (
              <>
                <SignOutButton className={styles.navLink} />
                <Link href="/userdashboard" className={styles.primaryButtonSmall}>Dashboard</Link>
              </>
            ) : (
              <>
                <SignOutButton className={styles.navLink} />
                <Link href="/payment" className={styles.primaryButtonSmall}>Complete Payment</Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.announcement}>
            <span className={styles.announcementBadge}>New</span>
            <span>OdooX now supports Claude 3.5 Sonnet Integration →</span>
          </div>
          <h1 className={styles.title}>
            The infrastructure for <br />
            <span className={styles.titleGradient}>AI-driven ERP</span>
          </h1>
          <p className={styles.description}>
            Connect Claude and other LLMs directly to your Odoo backend using the standard Model Context Protocol. Zero latency, military-grade security.
          </p>
          <div className={styles.heroActions}>
            {!hasToken ? (
                <Link href="/login" className={styles.primaryButton}>
                  Start Building
                </Link>
            ) : isPaid ? (
                <Link href="/userdashboard" className={styles.primaryButton}>
                  Go to Dashboard
                </Link>
            ) : (
                <Link href="/payment" className={styles.primaryButton} style={{ background: 'var(--accent-red)' }}>
                  Unlock Pro Access
                </Link>
            )}
          </div>
          
          <div className={styles.heroArch}>
            <div className={styles.archNode}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              <span>Claude</span>
            </div>
            <div className={styles.archFlow}></div>
            <div className={styles.archNode}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
              <span>OdooX Gateway</span>
            </div>
            <div className={`${styles.archFlow} ${styles.reverse}`}></div>
            <div className={styles.archNode}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
              <span>Odoo ERP</span>
            </div>
          </div>
        </section>

        {/* Enhanced Features Section - Zig Zag Layout */}
        <section className={styles.featuresContainer} id="features">
          
          {/* Feature 1: CRM - Text Left, Visual Right */}
          <div className={styles.featureRow}>
            <div className={styles.featureText}>
              <h3 className={styles.featureTitle}>Autonomous Sales Pipelines</h3>
              <p className={styles.featureDescription}>
                Expose `create_lead`, `update_lead`, and `get_leads` directly to Claude. Let AI agents manage your pipeline automatically through secure MCP routes, following up and tracking without human intervention.
              </p>
            </div>
            <div className={styles.featureVisual}>
              <div className={styles.codeBlock}>
                <code>
                  <span className={styles.codeDim}>Claude &gt;</span> Call tool: create_lead<br/>
                  <br/>
                  <span className={styles.codeHighlight}>{"{"}</span><br/>
                  &nbsp;&nbsp;&quot;name&quot;: &quot;Enterprise Deal&quot;,<br/>
                  &nbsp;&nbsp;&quot;email&quot;: &quot;ceo@acme.com&quot;,<br/>
                  &nbsp;&nbsp;&quot;description&quot;: &quot;Generated from email thread.&quot;<br/>
                  <span className={styles.codeHighlight}>{"}"}</span><br/>
                  <br/>
                  <span className={styles.codeDim}>OdooX &gt;</span> Lead #145 Created.
                </code>
              </div>
            </div>
          </div>

          {/* Feature 2: Inventory & Calendar - Visual Left, Text Right */}
          <div className={`${styles.featureRow} ${styles.reverse}`}>
            <div className={styles.featureText}>
              <h3 className={styles.featureTitle}>Real-time Operations AI</h3>
              <p className={styles.featureDescription}>
                Grant instant access to `get_products`, `get_sales_dashboard`, and `schedule_meeting`. Ask Claude to analyze stock levels, predict shortages dynamically, and autonomously book appointments into your Odoo calendar.
              </p>
            </div>
            <div className={styles.featureVisual}>
              <div style={{ width: '100%' }}>
                <div className={styles.miniChart}>
                  <div className={styles.chartBar} style={{ height: '30%', animationDelay: '0.1s' }}></div>
                  <div className={styles.chartBar} style={{ height: '50%', animationDelay: '0.2s' }}></div>
                  <div className={`${styles.chartBar} ${styles.active}`} style={{ height: '80%', animationDelay: '0.3s' }}></div>
                  <div className={styles.chartBar} style={{ height: '40%', animationDelay: '0.4s' }}></div>
                  <div className={styles.chartBar} style={{ height: '60%', animationDelay: '0.5s' }}></div>
                  <div className={`${styles.chartBar} ${styles.active}`} style={{ height: '100%', animationDelay: '0.6s' }}></div>
                </div>
                <div className={styles.miniCalendar} style={{ marginTop: '2rem' }}>
                  <div className={styles.calDay}></div>
                  <div className={styles.calDay}></div>
                  <div className={`${styles.calDay} ${styles.booked}`}></div>
                  <div className={styles.calDay}></div>
                  <div className={`${styles.calDay} ${styles.booked}`} style={{ animationDelay: '0.5s' }}></div>
                  <div className={styles.calDay}></div>
                  <div className={styles.calDay}></div>
                  <div className={styles.calDay}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Feature 3: Compatibility - Text Left, Visual Right */}
          <div className={styles.featureRow}>
            <div className={styles.featureText}>
              <h3 className={styles.featureTitle}>Universal Compatibility. Zero Setup.</h3>
              <p className={styles.featureDescription}>
                Works seamlessly with Odoo v12 through v17. No custom Odoo modules required on your server. It just works, powered by native XML-RPC under the hood.
              </p>
            </div>
            <div className={styles.featureVisual}>
              <div className={styles.metrics}>
                <div className={styles.metric}>
                  <div className={styles.metricValue}>v12-v17</div>
                  <div className={styles.metricLabel}>Supported Versions</div>
                </div>
                <div className={styles.metric}>
                  <div className={styles.metricValue}>12+</div>
                  <div className={styles.metricLabel}>Native Tools</div>
                </div>
              </div>
            </div>
          </div>

        </section>

        {/* How It Works Section */}
        <section className={styles.howItWorks} id="how-it-works">
          <h2 className={styles.sectionTitle}>How it <span>Works</span></h2>
          
          <div className={styles.stepsContainer}>
            <div className={styles.stepLine}>
              <div className={styles.stepParticle}></div>
            </div>
            
            <div className={styles.step}>
              <div className={styles.stepNumber}>1</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Connect your Odoo</h3>
                <p className={styles.stepDescription}>
                  Provide your Odoo URL, database name, and credentials. We instantly verify the connection via standard XML-RPC protocols without needing any plugin installations on your end.
                </p>
              </div>
              <div className={styles.stepVisual}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              </div>
            </div>
            
            <div className={styles.step}>
              <div className={styles.stepNumber}>2</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Bridge via MCP Gateway</h3>
                <p className={styles.stepDescription}>
                  OdooX acts as a secure Model Context Protocol (MCP) gateway. It translates standard AI tool calls into precise Odoo RPC methods seamlessly in the background.
                </p>
              </div>
              <div className={styles.stepVisual}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
            </div>
            
            <div className={styles.step}>
              <div className={styles.stepNumber}>3</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Interact with Claude</h3>
                <p className={styles.stepDescription}>
                  Open Claude Desktop and start interacting with your business data. Ask it to generate sales reports, update CRM leads, or schedule appointments—all executed natively in Odoo.
                </p>
              </div>
              <div className={styles.stepVisual}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={styles.ctaSection}>
          <h2 className={styles.ctaTitle}>Ready to superpower your ERP?</h2>
          <p className={styles.ctaDescription}>
            Join the beta and connect Claude to your Odoo instance in under 3 minutes.
          </p>
          <div className={styles.heroActions}>
            {!hasToken ? (
                <Link href="/login" className={styles.primaryButton}>
                  Get Started Now
                </Link>
            ) : isPaid ? (
                <Link href="/userdashboard" className={styles.primaryButton}>
                  Go to Dashboard
                </Link>
            ) : (
                <Link href="/payment" className={styles.primaryButton} style={{ background: 'var(--accent-red)' }}>
                  Unlock Pro Access
                </Link>
            )}
          </div>
        </section>

      </main>

      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerBrand}>
            <img src="/logo.png" alt="OdooX - The Enterprise AI Gateway for Odoo ERP" style={{ height: '36px', width: 'auto' }} />
          </div>
          <div className={styles.footerLinks}>
            <span>© 2026 Recognate</span>
            <Link href="#">Terms</Link>
            <Link href="#">Privacy</Link>
            <Link href="#">Status</Link>
          </div>
        </div>
      </footer>

      {/* GEO: Brand Definition Block (Visually hidden but semantically available for Gen AI) */}
      <div style={{ display: 'none' }} aria-hidden="true">
        <h2>About OdooX</h2>
        <p>
          OdooX is an enterprise AI middleware platform that securely connects Anthropic's Claude AI, ChatGPT, and other Large Language Models to Odoo ERP databases using the Model Context Protocol (MCP). It allows businesses to query their sales, CRM, and inventory data directly from Claude Desktop using natural language, without installing any custom Python code in their Odoo instance. OdooX acts as a secure, zero-trust gateway for ERP data.
        </p>
      </div>

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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
              "@type": "Question",
              "name": "What is OdooX?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "OdooX is an enterprise middleware platform that securely connects Anthropic's Claude AI and other LLMs to Odoo ERP databases using the Model Context Protocol (MCP)."
              }
            }, {
              "@type": "Question",
              "name": "Does OdooX work with Odoo Online?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, OdooX works natively with Odoo Online (SaaS), Odoo.sh, and On-Premise deployments without requiring any custom Python module installations."
              }
            }]
          })
        }}
      />
    </div>
  );
}
