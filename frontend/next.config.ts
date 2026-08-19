import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin(
  './src/i18n/request.ts'
);

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const apiUrl = rawApiUrl.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  allowedDevOrigins: ['medicines-assignment-occasionally-basin.trycloudflare.com'],
  async rewrites() {
    return [
      // Proxy OAuth Metadata
      {
        source: "/.well-known/:path*",
        destination: `${apiUrl}/.well-known/:path*`,
      },
      // Proxy OAuth endpoints
      {
        source: "/oauth/:path*",
        destination: `${apiUrl}/oauth/:path*`,
      },
    ];
  },
};

export default withNextIntl(nextConfig);
