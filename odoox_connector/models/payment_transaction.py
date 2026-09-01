# -*- coding: utf-8 -*-
import logging
import requests
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _set_error(self, state_message):
        """Override to notify ULTRON when a transaction moves to error state."""
        res = super()._set_error(state_message)
        for tx in self:
            tx._notify_ultron_recovery(error_code=state_message or "PAYMENT_FAILED")
        return res

    def _set_canceled(self, state_message):
        """Override to notify ULTRON when a transaction is canceled."""
        res = super()._set_canceled(state_message)
        for tx in self:
            tx._notify_ultron_recovery(error_code=state_message or "TRANSACTION_CANCELED")
        return res

    def _notify_ultron_recovery(self, error_code="PAYMENT_FAILED"):
        """
        Sends the failed payment event to ULTRON for autonomous recovery analysis.
        """
        self.ensure_one()

        ICP = self.env['ir.config_parameter'].sudo()
        ultron_url = ICP.get_param('ultron.api_url', 'http://localhost:3001/v1/events')
        ultron_key = ICP.get_param('ultron.api_key', 'ul_live_ee52e1727853.97301d13f5dfe358b652104e44940347')

        if not ultron_key or not ultron_url:
            _logger.debug("ULTRON integration is not configured in ir.config_parameter.")
            return

        order = self.sale_order_ids[:1]
        partner = self.partner_id

        # Convert to paise (e.g. INR 499.00 -> 49900)
        amount_paise = int(round(self.amount * 100))

        create_ts = int(self.create_date.timestamp()) if self.create_date else 0
        payload = {
            "event_id": f"evt_odoo_{self.id}_{create_ts}",
            "event_type": "payment.failed",
            "payment_id": self.provider_reference or f"tx_{self.id}",
            "order_id": order.name if order else (self.reference or f"TX-{self.id}"),
            "amount_paise": amount_paise,
            "currency": self.currency_id.name or "INR",
            "reason_code": str(error_code),
            "customer_id": f"partner_{partner.id}" if partner else "guest",
            "customer_email": partner.email if partner else None,
            "customer_phone": (partner.phone or partner.mobile) if partner else None,
        }

        headers = {
            "Authorization": f"Bearer {ultron_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(ultron_url, json=payload, headers=headers, timeout=5)
            if response.status_code in (200, 201):
                _logger.info("Successfully pushed failed payment tx %s to ULTRON: %s", self.id, response.text)
            else:
                _logger.warning("ULTRON ingestion returned [%s]: %s", response.status_code, response.text)
        except Exception as exc:
            _logger.error("Failed to connect to ULTRON engine for tx %s: %s", self.id, str(exc))
