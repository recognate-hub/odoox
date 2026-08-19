import type { Metadata } from "next";
import "./globals.css";

// Static metadata
export const metadata: Metadata = {
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
    canonical: `https://odoox.recognate.in`,
  },
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
