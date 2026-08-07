import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Proxy SSE calls to the FastAPI backend
      {
        source: "/sse",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/sse`,
      },
      // Proxy MCP messages endpoint
      {
        source: "/messages",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/messages`,
      },
      // Proxy OAuth Metadata
      {
        source: "/.well-known/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/.well-known/:path*`,
      },
      // Proxy OAuth endpoints
      {
        source: "/oauth/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/oauth/:path*`,
      },
    ];
  },
};

export default nextConfig;
