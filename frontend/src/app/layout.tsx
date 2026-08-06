import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OdooX — AI Gateway for Odoo ERP",
  description: "Securely connect Claude AI and other LLMs to your Odoo ERP infrastructure via the Model Context Protocol.",
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
