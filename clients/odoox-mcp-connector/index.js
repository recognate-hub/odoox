#!/usr/bin/env node

import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

// Catch unhandled promise rejections to prevent crashes
process.on("unhandledRejection", (error) => {
  console.error("[Connector] Unhandled rejection:", error?.message || error);
});

async function main() {
  // Parse command line arguments to find --url
  const args = process.argv.slice(2);
  const urlIndex = args.indexOf("--url");

  if (urlIndex === -1 || urlIndex === args.length - 1) {
    console.error("Usage: npx odoox-mcp-connector --url <SSE_ENDPOINT_URL>");
    process.exit(1);
  }

  const sseUrl = args[urlIndex + 1];
  console.error(`[Connector] Connecting to ${new URL(sseUrl).origin}...`);

  // Initialize transports
  const clientTransport = new SSEClientTransport(new URL(sseUrl));
  const serverTransport = new StdioServerTransport();

  let isClosing = false;

  function shutdown() {
    if (isClosing) return;
    isClosing = true;
    try { clientTransport.close(); } catch {}
    try { serverTransport.close(); } catch {}
    process.exit(0);
  }

  // When we receive a message from Claude (via stdio), send it to the remote server
  serverTransport.onmessage = async (message) => {
    try {
      await clientTransport.send(message);
    } catch (error) {
      console.error("[Connector] Failed to forward message to server:", error?.message || error);
      shutdown();
    }
  };

  // When we receive a message from the remote server (via SSE), send it to Claude
  clientTransport.onmessage = async (message) => {
    try {
      await serverTransport.send(message);
    } catch (error) {
      console.error("[Connector] Failed to forward message to Claude:", error?.message || error);
      shutdown();
    }
  };

  // Handle close events
  serverTransport.onclose = () => {
    console.error("[Connector] Claude disconnected.");
    shutdown();
  };

  clientTransport.onclose = () => {
    console.error("[Connector] Server SSE connection closed.");
    shutdown();
  };

  // Handle errors
  clientTransport.onerror = (error) => {
    console.error("[Connector] SSE error:", error?.message || error);
  };

  serverTransport.onerror = (error) => {
    console.error("[Connector] Stdio error:", error?.message || error);
  };

  // Start both transports
  try {
    await clientTransport.start();
    console.error("[Connector] SSE connection established.");
  } catch (error) {
    console.error("[Connector] Failed to connect to SSE server:", error?.message || error);
    process.exit(1);
  }

  await serverTransport.start();
  console.error("[Connector] Ready. Proxying messages between Claude and server.");
}

main().catch((error) => {
  console.error("[Connector] Fatal error:", error?.message || error);
  process.exit(1);
});
