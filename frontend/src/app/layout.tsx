import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";
import { Toaster } from "sonner";

// Viewport configuration
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0A0A0A',
};

// Static metadata with global SEO & GEO optimization
export const metadata: Metadata = {
  metadataBase: new URL('https://odoox.recognate.in'),
  title: {
    default: "OdooX — World's #1 Model Context Protocol (MCP) Server for Odoo ERP",
    template: "%s | OdooX Model Context Protocol"
  },
  description: "Connect Claude Desktop, Cursor, Windsurf, ChatGPT, and AI Agents to your Odoo ERP infrastructure via the Model Context Protocol (MCP). 100+ tools for CRM, Manufacturing, Accounting & Inventory with zero-latency SSE and Fernet envelope encryption.",
  keywords: [
    "Odoo MCP Server",
    "Model Context Protocol Odoo",
    "Odoo Claude Integration",
    "Odoo Cursor AI",
    "Odoo Windsurf MCP",
    "Odoo ERP AI Agent",
    "FastMCP Odoo",
    "Odoo AI Gateway",
    "Model Context Protocol ERP",
    "Anthropic Claude Odoo CRM",
    "Autonomous ERP Agent",
    "Recognate Technologies"
  ],
  authors: [{ name: "Recognate Technologies", url: "https://recognate.in" }],
  creator: "Recognate Technologies",
  publisher: "Recognate Technologies",
  applicationName: "OdooX MCP Server",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    title: "OdooX — World's #1 Model Context Protocol (MCP) Server for Odoo ERP",
    description: "The enterprise AI bridge connecting Claude, Cursor, Windsurf, and LLMs to Odoo ERP. 100+ native MCP tools across CRM, MRP, Accounting, and Inventory.",
    url: "https://odoox.recognate.in",
    siteName: "OdooX",
    images: [
      {
        url: "https://odoox.recognate.in/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "OdooX Model Context Protocol AI Gateway for Odoo ERP",
      },
    ],
    locale: 'en_US',
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OdooX — World's #1 Model Context Protocol (MCP) Server for Odoo ERP",
    description: "Connect Claude, Cursor, and LLMs directly to Odoo ERP via native Model Context Protocol (MCP). 100+ ERP tools, streaming SSE, and enterprise encryption.",
    images: ["https://odoox.recognate.in/og-image.jpg"],
    creator: "@recognate",
  },
  alternates: {
    canonical: 'https://odoox.recognate.in',
    languages: {
      'en-US': 'https://odoox.recognate.in',
      'en-GB': 'https://odoox.recognate.in',
      'en-IN': 'https://odoox.recognate.in',
      'de-DE': 'https://odoox.recognate.in',
      'fr-FR': 'https://odoox.recognate.in',
      'x-default': 'https://odoox.recognate.in',
    },
  },
  category: 'technology',
  classification: 'Software, ERP Integration, Artificial Intelligence, Model Context Protocol',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/android-chrome-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/android-chrome-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  manifest: '/site.webmanifest',
};

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://odoox.recognate.in/#organization",
      "name": "Recognate Technologies",
      "url": "https://recognate.in",
      "logo": "https://odoox.recognate.in/logo.png",
      "sameAs": [
        "https://twitter.com/recognate",
        "https://github.com/recognate-hub",
        "https://linkedin.com/company/recognate"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://odoox.recognate.in/#website",
      "url": "https://odoox.recognate.in",
      "name": "OdooX Model Context Protocol Server",
      "publisher": {
        "@id": "https://odoox.recognate.in/#organization"
      }
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://odoox.recognate.in/#software",
      "name": "OdooX AI Gateway & MCP Server",
      "operatingSystem": "All (Cloud, macOS, Linux, Windows)",
      "applicationCategory": "BusinessApplication, DeveloperApplication",
      "softwareVersion": "2.0.0",
      "url": "https://odoox.recognate.in",
      "offers": {
        "@type": "Offer",
        "price": "49.00",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      },
      "description": "Enterprise-grade Model Context Protocol (MCP) server connecting Claude Desktop, Cursor, and LLMs to Odoo ERP with 100+ tools across CRM, MRP, Accounting, and Inventory.",
      "featureList": [
        "100+ native type-safe MCP tools for Odoo ERP",
        "Dynamic MCP resources (odoo://system/status, odoo://schema/models)",
        "Pre-built MCP prompt workflows (daily executive briefing, bottleneck audit)",
        "Zero-latency Server-Sent Events (SSE) streaming transport",
        "Fernet KMS envelope encryption & stateless permanent API keys",
        "Multi-tenant Role-Based Access Control (RBAC) with FinOps token budgeting",
        "1-click configuration generator for Claude Desktop, Cursor, Windsurf, and Cline"
      ],
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.98",
        "ratingCount": "248"
      }
    },
    {
      "@type": "FAQPage",
      "@id": "https://odoox.recognate.in/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is the OdooX MCP Server?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OdooX is an enterprise Model Context Protocol (MCP) server that enables AI assistants like Claude Desktop, Cursor, Windsurf, and ChatGPT to interact natively with your Odoo ERP database to read, query, analyze, and update CRM leads, manufacturing workorders, inventory levels, invoices, and custom business models in real time."
          }
        },
        {
          "@type": "Question",
          "name": "Which AI clients are supported by OdooX?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OdooX supports all MCP-compliant clients including Claude Desktop, Cursor IDE, Windsurf / Codeium, VS Code with Cline or Roo-Code, Zed Editor, LibreChat, Open WebUI, and custom Python/Node SDK implementations."
          }
        },
        {
          "@type": "Question",
          "name": "How does OdooX protect my ERP credentials and company data?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OdooX employs 32-byte DEK/KEK Fernet envelope encryption for database passwords, stateless token architectures, and strict per-workspace Role-Based Access Control (RBAC) with rate-limiting and circuit-breaker isolation."
          }
        }
      ]
    },
    {
      "@type": "HowTo",
      "@id": "https://odoox.recognate.in/#howto",
      "name": "How to Connect Claude Desktop to Odoo ERP via OdooX",
      "description": "Step-by-step guide to connect Claude Desktop to your Odoo ERP database in under 2 minutes using the Model Context Protocol.",
      "step": [
        {
          "@type": "HowToStep",
          "position": 1,
          "name": "Generate your API Key",
          "text": "Sign in to the OdooX dashboard and copy your secure permanent API key (odx_...)."
        },
        {
          "@type": "HowToStep",
          "position": 2,
          "name": "Update Claude Desktop Config",
          "text": "Open your claude_desktop_config.json file and paste the odoox-mcp-connector command."
        },
        {
          "@type": "HowToStep",
          "position": 3,
          "name": "Start Asking Claude about your ERP",
          "text": "Restart Claude Desktop and begin querying live sales metrics, customer 360 views, and shop floor workorders."
        }
      ]
    }
  ]
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Multi-Region Global GEO Meta Tags */}
        <meta name="geo.region" content="US-CA" />
        <meta name="geo.region" content="US-NY" />
        <meta name="geo.region" content="GB" />
        <meta name="geo.region" content="DE" />
        <meta name="geo.region" content="IN" />
        <meta name="geo.region" content="SG" />
        <meta name="geo.placename" content="San Francisco, London, Berlin, Bengaluru, Singapore" />
        <meta name="geo.position" content="37.7749;-122.4194" />
        <meta name="ICBM" content="37.7749, -122.4194" />

        {/* AI & Search Engine Discovery Link */}
        <link rel="author" href="https://odoox.recognate.in/llms.txt" />

        {/* Schema.org Structured Data */}
        <Script
          id="json-ld"
          type="application/ld+json"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />

        {/* ULTRON SDK */}
        <Script
          src="https://ultron-v6qe.onrender.com/sdk/ultron.js"
          data-api-key="ul_live_6864e09cfb4d.bf7167e42544c20db697fe25670b9ae1"
          strategy="afterInteractive"
        />
      </head>
      <body>
        {children}
        <Toaster theme="dark" position="bottom-right" richColors />
      </body>
    </html>
  );
}
