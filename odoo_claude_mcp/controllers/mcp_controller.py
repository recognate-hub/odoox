from odoo import http
from odoo.http import request
import json

class MCPController(http.Controller):

    @http.route('/mcp/tools', type='json', auth='user', methods=['POST'])
    def list_tools(self, **kwargs):
        """Returns the list of available MCP tools."""
        return {
            "tools": [
                {
                    "name": "analyze_lead",
                    "description": "Analyze a CRM lead and identify strengths, risks, and next steps.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "integer"}
                        },
                        "required": ["lead_id"]
                    }
                },
                {
                    "name": "generate_draft_email",
                    "description": "Draft an email to a lead based on specific instructions.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "integer"},
                            "instructions": {"type": "string"}
                        },
                        "required": ["lead_id", "instructions"]
                    }
                }
            ]
        }

    @http.route('/mcp/call_tool', type='json', auth='user', methods=['POST'])
    def call_tool(self, name, arguments, **kwargs):
        """Executes a specific MCP tool and returns the result."""
        claude_service = request.env['claude.service']
        
        try:
            if name == "analyze_lead":
                result = claude_service.analyze_lead(arguments.get('lead_id'))
                return {"status": "success", "result": result}
                
            elif name == "generate_draft_email":
                result = claude_service.generate_draft_email(
                    arguments.get('lead_id'), 
                    arguments.get('instructions')
                )
                return {"status": "success", "result": result}
                
            else:
                return {"status": "error", "message": f"Tool '{name}' not found."}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
