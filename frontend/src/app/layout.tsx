import type { Metadata } from "next";
import "./globals.css";

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
    title: "OdooX — Enterprise AI Gateway for Odoo",
    description: "Securely connect Anthropic's Claude AI to your Odoo ERP database using the Model Context Protocol.",
    url: "https://odoox.com",
    siteName: "OdooX",
    images: [
      {
        url: "https://odoox.com/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "OdooX AI Gateway Dashboard",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OdooX — AI Gateway for Odoo ERP",
    description: "Securely connect Claude AI to Odoo via MCP.",
    images: ["https://odoox.com/og-image.jpg"],
  },
  alternates: {
    canonical: "https://odoox.com",
  },
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
