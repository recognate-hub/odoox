{
    "name": "Claude CRM Integration (MCP)",
    "version": "1.0.0",
    "category": "Sales/CRM",
    "summary": "AI-powered CRM integration using Anthropic's Claude and MCP",
    "description": """
        Native Odoo Module that bridges Odoo CRM and Anthropic's Claude.
        Allows Claude to analyze leads, summarize customers, forecast sales,
        and draft emails directly using Odoo's internal ORM.
        Provides an endpoint for Claude Desktop to connect via MCP.
    """,
    "author": "AI Middleware",
    "depends": ["base", "crm", "sale", "mail", "calendar"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
