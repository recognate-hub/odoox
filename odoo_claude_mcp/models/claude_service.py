import logging

from odoo.exceptions import UserError

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeService(models.AbstractModel):
    _name = "claude.service"
    _description = "Claude AI Integration Service"

    @api.model
    def _get_client(self):
        if not anthropic:
            raise UserError(
                "The 'anthropic' python package is not installed. Please run 'pip install anthropic'."
            )

        api_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("odoo_claude_mcp.claude_api_key")
        )
        if not api_key:
            raise UserError(
                "Anthropic API key is not configured. Please set it in Settings -> General Settings."
            )

        return anthropic.Anthropic(api_key=api_key)

    @api.model
    def _get_model_name(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "odoo_claude_mcp.claude_model_name", "claude-3-5-sonnet-20240620"
            )
        )

    @api.model
    def _get_temperature(self):
        temp = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("odoo_claude_mcp.claude_temperature", 0.0)
        )
        return float(temp)

    @api.model
    def _generate(self, instructions: str, context: str, max_tokens: int = 1000) -> str:
        client = self._get_client()
        model = self._get_model_name()
        temperature = self._get_temperature()

        prompt = f"""
You are an expert AI assistant integrated natively into an Odoo CRM system.
Follow the instructions carefully and use the provided context to generate your response.

<context>
{context}
</context>

<instructions>
{instructions}
</instructions>
"""
        _logger.info("Calling Claude API (Model: %s)", model)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            _logger.error("Claude API Error: %s", str(e))
            raise UserError(f"Failed to communicate with Claude: {e!s}")

    @api.model
    def analyze_lead(self, lead_id: int) -> str:
        lead = self.env["crm.lead"].browse(lead_id)
        if not lead.exists():
            return "Lead not found."

        context = f"Lead Name: {lead.name}\nExpected Revenue: {lead.expected_revenue}\nProbability: {lead.probability}%\nDescription: {lead.description or 'None'}"
        return self._generate(
            instructions="Analyze this lead and identify key strengths, risks, and next steps.",
            context=context,
        )

    @api.model
    def generate_draft_email(self, lead_id: int, instructions: str) -> str:
        lead = self.env["crm.lead"].browse(lead_id)
        if not lead.exists():
            return "Lead not found."

        context = f"Lead Name: {lead.name}\nPartner: {lead.partner_id.name if lead.partner_id else 'None'}\nEmail: {lead.email_from}"
        return self._generate(
            instructions=f"Draft an email based on these instructions: {instructions}",
            context=context,
            max_tokens=800,
        )
