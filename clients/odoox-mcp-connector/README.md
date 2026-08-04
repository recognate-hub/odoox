# OdooX MCP Connector

This is a lightweight CLI bridge designed for enterprise clients to connect their local **Claude Desktop** application to a remote **Odoo MCP Server**.

Claude Desktop natively communicates with local tools over standard input/output (STDIO), but enterprise servers often expose their endpoints over HTTP using Server-Sent Events (SSE). This connector transparently proxies the communication between Claude Desktop and your production SSE server.

## Usage in Claude Desktop

Add the following configuration to your Claude Desktop configuration file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "odoox-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "odoox-mcp-connector",
        "--url",
        "https://your-production-domain.com/sse?token=YOUR_JWT_TOKEN"
      ]
    }
  }
}
```

After updating the configuration, **fully restart** Claude Desktop.

## How It Works
This tool uses the official `@modelcontextprotocol/sdk` to run an `StdioServerTransport` connected to an `SSEClientTransport`, routing JSON-RPC messages seamlessly.
