import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";

// Viewport configuration
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0A0A0A',
};

// Static metadata
export const metadata: Metadata = {
  metadataBase: new URL('https://odoox.recognate.in'),
  title: "OdooX — AI Gateway for Odoo ERP",
  description: "Securely connect Claude AI, ChatGPT, and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol (MCP).",
  keywords: ["Odoo", "Claude", "AI", "MCP", "Model Context Protocol", "ERP Integration", "Generative AI", "Anthropic"],
  authors: [{ name: "OdooX Team" }],
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
    title: "OdooX — AI Gateway for Odoo ERP",
    description: "Securely connect Claude AI, ChatGPT, and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol (MCP).",
    url: `https://odoox.recognate.in`,
    siteName: "OdooX",
    images: [
      {
        url: "https://odoox.recognate.in/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "OdooX AI Gateway Dashboard",
      },
    ],
    locale: 'en_US',
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OdooX — AI Gateway for Odoo ERP",
    description: "Securely connect Claude AI, ChatGPT, and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol (MCP).",
    images: ["https://odoox.recognate.in/og-image.jpg"],
  },
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'en-GB': '/en-GB',
      'en-IN': '/en-IN',
      'x-default': '/',
    },
  },
  category: 'technology',
  classification: 'Software, ERP Integration, Artificial Intelligence',
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

import { Toaster } from "sonner";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="geo.region" content="US-CA" />
        <meta name="geo.region" content="IN" />
        <meta name="geo.placename" content="San Francisco" />
        <meta name="geo.position" content="37.7749;-122.4194" />
        <meta name="ICBM" content="37.7749, -122.4194" />
        <Script id="json-ld" type="application/ld+json" strategy="afterInteractive">
          {`
            {
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "OdooX AI Gateway",
              "operatingSystem": "Web",
              "applicationCategory": "BusinessApplication",
              "offers": {
                "@type": "Offer",
                "price": "49.00",
                "priceCurrency": "USD"
              },
              "description": "Securely connect Claude AI, ChatGPT, and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol (MCP).",
              "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.9",
                "ratingCount": "124"
              }
            }
          `}
        </Script>
      </head>
      <body>
        {children}
        <Toaster theme="dark" position="bottom-right" richColors />
      </body>
    </html>
  );
}
