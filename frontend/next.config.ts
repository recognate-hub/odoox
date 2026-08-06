import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Proxy SSE calls to the FastAPI backend
      {
        source: "/sse",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/sse`,
      },
    ];
  },
};

export default nextConfig;
