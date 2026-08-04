#!/usr/bin/env node

import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

async function main() {
  // Parse command line arguments to find --url
  const args = process.argv.slice(2);
  const urlIndex = args.indexOf("--url");
  
  if (urlIndex === -1 || urlIndex === args.length - 1) {
    console.error("Usage: npx odoox-mcp-connector --url <SSE_ENDPOINT_URL>");
    process.exit(1);
  }
  
  const sseUrl = args[urlIndex + 1];

  // Initialize transports
  const clientTransport = new SSEClientTransport(new URL(sseUrl));
  const serverTransport = new StdioServerTransport();

  // When we receive a message from Claude (via stdio), send it to the remote server
  serverTransport.onmessage = (message) => {
    clientTransport.send(message);
  };

  // When we receive a message from the remote server (via SSE), send it to Claude
  clientTransport.onmessage = (message) => {
    serverTransport.send(message);
  };

  // Handle close events
  serverTransport.onclose = () => {
    clientTransport.close();
    process.exit(0);
  };
  
  clientTransport.onclose = () => {
    serverTransport.close();
    process.exit(0);
  };

  // Handle errors
  clientTransport.onerror = (error) => {
    console.error("[SSE Error]", error);
  };

  serverTransport.onerror = (error) => {
    console.error("[Stdio Error]", error);
  };

  // Start both transports
  await clientTransport.start();
  await serverTransport.start();
}

main().catch((error) => {
  console.error("Failed to start MCP connector:", error);
  process.exit(1);
});
