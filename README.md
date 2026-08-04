# Odoo-Claude CRM Middleware

A robust middleware application that bridges Odoo ERP (specifically the CRM module) and Anthropic's Claude using the Model Context Protocol (MCP). It exposes a set of AI-ready tools that allow Claude to natively interact with Odoo data—analyzing leads, forecasting sales, summarizing customer profiles, and drafting targeted emails.

## Features

- **MCP Server**: Provides native tools for Claude to read and mutate Odoo CRM data securely.
- **REST API & Admin Dashboard**: FastAPI-based administration UI for configuring Odoo and Claude credentials.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions securing each MCP tool.
- **Automated AI Workflows**: AI pipelines for generating emails, summarizing meetings, and profiling customers.
- **Robust Odoo Integration**: XML-RPC connector with caching, error handling, and domain filtering.

## Setup & Installation

### Prerequisites
- Python 3.12+
- Poetry
- Docker & Docker Compose (optional, for deployment)

### Local Development

1. **Clone and Install dependencies:**
   ```bash
   poetry install
   ```
2. **Initialize Configuration:**
   Run the setup command to generate the `.env` file:
   ```bash
   poetry run app install
   ```
   *Edit `.env` with your Odoo and Claude credentials.*
3. **Run the API & Admin Server:**
   ```bash
   poetry run app api
   ```
   Access the dashboard at `http://localhost:8000/admin`.
4. **Run the MCP Server (for Claude Desktop):**
   ```bash
   poetry run app mcp
   ```

## Production Deployment (Docker)

The application is containerized and ready for production deployment using Docker Compose.

1. **Create the environment file:**
   Copy the example environment file and fill in your credentials.
   ```bash
   cp .env.example .env
   ```
2. **Start the containers:**
   ```bash
   docker-compose up -d
   ```
3. **Verify Health:**
   The application will be available on port 8000. You can verify its status at:
   ```bash
   curl http://localhost:8000/health
   ```

## Enterprise Client Distribution

To allow your enterprise clients to connect their local Claude Desktop apps to your remote production Odoo MCP server, distribute the provided `odoox-mcp-connector` bridge tool. 

Clients should add this configuration to their `claude_desktop_config.json`:

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

*(Note: You will need to publish the `clients/odoox-mcp-connector` package to NPM, or instruct clients to install it via a git URL or local path).* 

## CI/CD

This project uses GitHub Actions for Continuous Integration.
- **Test Enforcement:** Every push and PR to `main` runs the full test suite.
- **Coverage Target:** The pipeline mandates a >90% code coverage threshold.
- **Build Checks:** The pipeline verifies that the Docker image builds successfully.

## Architecture

- **`cli/`**: Typer-based command-line interface.
- **`config/`**: Pydantic settings management.
- **`core/`**: Custom exceptions and structured logging.
- **`odoo/`**: Low-level XML-RPC connector to Odoo.
- **`repositories/`**: Domain-specific data access layer (e.g., Leads, Contacts, Products).
- **`claude/`**: Anthropic API service for executing AI tasks.
- **`services/`**: High-level business logic orchestrating Odoo and Claude.
- **`mcp_app/`**: FastMCP server with RBAC security and rate limiting.
- **`routers/`**: FastAPI REST endpoints and HTML dashboards.
