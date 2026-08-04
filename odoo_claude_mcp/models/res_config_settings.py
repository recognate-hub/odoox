from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    claude_api_key = fields.Char(
        string="Anthropic API Key",
        config_parameter="odoo_claude_mcp.claude_api_key",
        help="API key for Anthropic Claude (e.g., sk-ant-...)"
    )
    
    claude_model_name = fields.Selection(
        [
            ('claude-3-5-sonnet-20240620', 'Claude 3.5 Sonnet'),
            ('claude-3-opus-20240229', 'Claude 3 Opus'),
            ('claude-3-haiku-20240307', 'Claude 3 Haiku')
        ],
        string="Claude Model",
        default="claude-3-5-sonnet-20240620",
        config_parameter="odoo_claude_mcp.claude_model_name"
    )

    claude_temperature = fields.Float(
        string="Temperature",
        default=0.0,
        config_parameter="odoo_claude_mcp.claude_temperature"
    )
