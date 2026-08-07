import type { NextConfig } from "next";

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const apiUrl = rawApiUrl.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Proxy SSE calls to the FastAPI backend
      {
        source: "/sse",
        destination: `${apiUrl}/sse`,
      },
      // Proxy MCP messages endpoint
      {
        source: "/messages",
        destination: `${apiUrl}/messages`,
      },
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

export default nextConfig;
