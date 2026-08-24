from typing import Any

from core.domain_builder import Domain
from odoo.interface import OdooConnectorInterface
from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)


class OdooRepository:
    """
    Repository pattern over the Odoo Connector.
    Provides domain-specific query building and abstracts away raw Odoo domains.
    """

    def __init__(self, connector: OdooConnectorInterface):
        self.connector = connector

    def get_active_leads(
        self,
        name_query: str | None = None,
        stage_id: int | None = None,
        limit: int = 100,
    ) -> list[OdooLead]:
        d = Domain().eq("type", "opportunity")
        if name_query:
            d.ilike("name", name_query)
        if stage_id:
            d.eq("stage_id", stage_id)
        return self.connector.get_leads(domain=d.build(), limit=limit)

    def get_lead_by_id(self, lead_id: int) -> OdooLead | None:
        domain = Domain().eq("id", lead_id).build()
        leads = self.connector.get_leads(domain=domain, limit=1)
        return leads[0] if leads else None

    def search_contacts_by_name(
        self, name_query: str, limit: int = 20
    ) -> list[OdooContact]:
        domain = Domain().ilike("name", name_query).build()
        return self.connector.search_contacts(domain=domain, limit=limit)

    def create_contact(
        self,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        is_company: bool = False,
    ) -> int:
        data = {"name": name, "is_company": is_company}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        return self.connector.create_contact(data)

    def search_products(self, query: str, limit: int = 20) -> list[OdooProduct]:
        if query:
            domain = Domain.or_(
                Domain().ilike("name", query),
                Domain().ilike("default_code", query),
            ).build()
        else:
            domain = Domain().build()
        return self.connector.get_products(domain=domain, limit=limit)

    def create_product(
        self,
        name: str,
        list_price: float,
        default_code: str | None = None,
        type_code: str = "service",
    ) -> int:
        data = {"name": name, "list_price": list_price, "detailed_type": type_code}
        if default_code:
            data["default_code"] = default_code
        return self.connector.create_product(data)

    def get_recent_quotes(
        self, partner_id: int | None = None, limit: int = 10
    ) -> list[OdooQuote]:
        d = Domain()
        if partner_id:
            d.eq("partner_id", partner_id)
        return self.connector.get_quotes(domain=d.build(), limit=limit)

    def create_quote(self, partner_id: int, order_lines: list[dict]) -> int:
        formatted_lines = []
        for line in order_lines:
            line_dict = {
                "product_id": line["product_id"],
                "product_uom_qty": line["quantity"],
            }
            if line.get("price_unit") is not None:
                line_dict["price_unit"] = line["price_unit"]
            # Odoo uses [0, 0, dict] for creating new related records
            formatted_lines.append([0, 0, line_dict])

        data = {"partner_id": partner_id, "order_line": formatted_lines}
        return self.connector.create_quote(data)

    def create_lead(
        self,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        description: str | None = None,
    ) -> int:
        data = {"name": name, "type": "opportunity"}
        if email:
            data["email_from"] = email
        if phone:
            data["phone"] = phone
        if description:
            data["description"] = description
        return self.connector.create_lead(data)

    def update_lead(self, lead_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_lead(lead_id, data)

    def log_activity(
        self, res_model: str, res_id: int, summary: str, activity_type_id: int = 4
    ) -> int:
        data = {
            "model": res_model,
            "res_id": res_id,
            "body": summary,
            "message_type": "comment",
            "subtype_id": 2,
        }
        return self.connector.create_activity(data)

    def schedule_meeting(
        self, name: str, start: str, stop: str, partner_ids: list[int]
    ) -> int:
        data = {
            "name": name,
            "start": start,
            "stop": stop,
            "partner_ids": [[6, 0, partner_ids]],  # Odoo Many2many syntax
        }
        return self.connector.schedule_meeting(data)

    def get_dashboard(self) -> OdooSalesDashboard:
        return self.connector.get_sales_dashboard()

    def create_invoice(self, partner_id: int, amount: float, description: str) -> int:
        data = {
            "partner_id": partner_id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                [
                    0,
                    0,
                    {
                        "name": description,
                        "quantity": 1,
                        "price_unit": amount,
                    },
                ]
            ],
        }
        return self.connector.create_invoice(data)

    def get_product_stock(self, product_id: int) -> list[dict[str, Any]]:
        """
        Retrieves the stock quantities for a specific product.
        Returns a list of locations and their available quantities.
        """
        domain = Domain().eq("product_id", product_id).build()
        fields = ["location_id", "quantity", "reserved_quantity"]
        return self.connector.search_read_records(
            "stock.quant", domain, fields, limit=50
        )

    def send_email(self, email_to: str, subject: str, body: str) -> int:
        data = {
            "email_to": email_to,
            "subject": subject,
            "body_html": body,
            "state": "outgoing",
        }
        return self.connector.send_email(data)

    def search_read_records(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return self.connector.search_read_records(
            model, domain=domain, fields=fields, limit=limit, offset=offset
        )

    def read_group(
        self, model: str, domain: list[Any], fields: list[str], groupby: list[str]
    ) -> list[dict[str, Any]]:
        return self.connector.read_group(model, domain, fields, groupby, lazy=False)

    def create_record(self, model: str, data: dict[str, Any]) -> int:
        return self.connector.create_record(model, data)

    def create_records(self, model: str, data_list: list[dict[str, Any]]) -> list[int]:
        return self.connector.create_records(model, data_list)

    def update_record(self, model: str, record_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_record(model, record_id, data)

    def get_installed_apps(self) -> list[dict[str, Any]]:
        return self.connector.get_installed_apps()

    def get_model_fields(self, model: str) -> dict[str, Any]:
        return self.connector.get_model_fields(model)


    def archive_record(self, model: str, record_id: int, archive: bool = True) -> bool:
        return self.connector.archive_record(model, record_id, archive)

    def get_attachment(self, attachment_id: int) -> dict[str, Any]:
        return self.connector.get_attachment(attachment_id)

    def create_attachment(self, data: dict[str, Any]) -> int:
        return self.connector.create_attachment(data)

    def execute_method(
        self,
        model: str,
        method: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        return self.connector.execute_method(model, method, args, kwargs)

    def batch_create_records(
        self, model: str, records: list[dict[str, Any]]
    ) -> list[int]:
        """Create multiple records in a single XML-RPC call."""

        def _exec():
            return self.connector.execute_method(model, "create", [records])

        # Using execute_method to bypass the single-dict wrapper in connector.create_record
        return _exec()

    def batch_update_records(
        self, model: str, record_ids: list[int], data: dict[str, Any]
    ) -> bool:
        """Update multiple records with the same data in a single XML-RPC call."""
        return self.connector.execute_method(model, "write", [record_ids, data])

    def post_message(
        self, res_model: str, res_id: int, body: str, message_type: str = "comment"
    ) -> int:
        data = {
            "model": res_model,
            "res_id": res_id,
            "body": body,
            "message_type": message_type,
        }
        return self.connector.create_record("mail.message", data)

    def create_channel(self, name: str, channel_type: str = "channel") -> int:
        data = {
            "name": name,
            "channel_type": channel_type,
        }
        return self.connector.create_record("discuss.channel", data)

    def create_purchase_order(self, partner_id: int, order_lines: list[dict]) -> int:
        formatted_lines = []
        for line in order_lines:
            line_dict = {
                "product_id": line["product_id"],
                "product_qty": line["product_qty"],
            }
            if line.get("price_unit") is not None:
                line_dict["price_unit"] = line["price_unit"]
            formatted_lines.append([0, 0, line_dict])

        data = {"partner_id": partner_id, "order_line": formatted_lines}
        return self.connector.create_record("purchase.order", data)

    def get_purchase_orders(
        self, partner_id: int | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        d = Domain()
        if partner_id:
            d.eq("partner_id", partner_id)
        fields = [
            "name",
            "partner_id",
            "state",
            "amount_total",
            "date_order",
            "date_approve",
        ]
        return self.connector.search_read_records(
            "purchase.order", domain=d.build(), fields=fields, limit=limit
        )

    def create_manufacturing_order(self, product_id: int, product_qty: float) -> int:
        data = {
            "product_id": product_id,
            "product_qty": product_qty,
        }
        return self.connector.create_record("mrp.production", data)

    def get_manufacturing_orders(self, limit: int = 20, offset: int = 0, date_from: str | None = None, date_to: str | None = None) -> list[dict[str, Any]]:
        fields = [
            "name",
            "product_id",
            "product_qty",
            "state",
            "date_planned_start",
            "date_planned_finished",
            "bom_id",
        ]
        d = Domain()
        if date_from:
            d.gte("create_date", date_from)
        if date_to:
            d.lte("create_date", date_to)
            
        return self.connector.search_read_records(
            "mrp.production", domain=d.build(), fields=fields, limit=limit, offset=offset
        )

    def create_stock_move(
        self,
        name: str,
        product_id: int,
        product_uom_qty: float,
        location_id: int,
        location_dest_id: int,
    ) -> int:
        data = {
            "name": name,
            "product_id": product_id,
            "product_uom_qty": product_uom_qty,
            "location_id": location_id,
            "location_dest_id": location_dest_id,
        }
        return self.connector.create_record("stock.move", data)

    def get_inventory_valuation(
        self, product_id: int | None = None, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        d = Domain()
        if product_id:
            d.eq("product_id", product_id)
        fields = [
            "product_id",
            "quantity",
            "unit_cost",
            "value",
            "description",
        ]
        return self.connector.search_read_records(
            "stock.valuation.layer", domain=d.build(), fields=fields, limit=limit, offset=offset
        )

    def create_quality_alert(
        self,
        name: str,
        product_id: int,
        team_id: int | None = None,
        priority: str = "0",
    ) -> int:
        data = {
            "name": name,
            "product_id": product_id,
            "priority": priority,
        }
        if team_id:
            data["team_id"] = team_id
        return self.connector.create_record("quality.alert", data)

    def get_quality_checks(
        self, product_id: int | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        d = Domain()
        if product_id:
            d.eq("product_id", product_id)
        if date_from:
            d.gte("create_date", date_from)
        if date_to:
            d.lte("create_date", date_to)
        fields = [
            "name",
            "product_id",
            "test_type",
            "quality_state",
            "control_date",
            "measure",
            "norm",
            "tolerance_min",
            "tolerance_max",
            "workorder_id",
            "point_id",
            "note",
        ]
        return self.connector.search_read_records(
            "quality.check", domain=d.build(), fields=fields, limit=limit, offset=offset
        )

    def update_quality_check_result(
        self, check_id: int, measure: float | None = None, quality_state: str | None = None
    ) -> bool:
        data = {}
        if measure is not None:
            data["measure"] = measure
        if quality_state is not None:
            data["quality_state"] = quality_state
        if not data:
            return False
        return self.connector.update_record("quality.check", check_id, data)

    # ── Discuss (mail) ─────────────────────────────────────────────────
    def get_messages(
        self, res_model: str | None = None, res_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain()
        if res_model:
            d.eq("model", res_model)
        if res_id:
            d.eq("res_id", res_id)
        fields = [
            "body",
            "message_type",
            "author_id",
            "date",
            "model",
            "res_id",
            "subject",
        ]
        return self.connector.search_read_records(
            "mail.message", domain=d.build(), fields=fields, limit=limit
        )

    def get_channels(self, limit: int = 50) -> list[dict[str, Any]]:
        fields = ["name", "channel_type", "channel_member_ids", "description"]
        return self.connector.search_read_records(
            "discuss.channel", domain=[], fields=fields, limit=limit
        )

    def get_channel_messages(
        self, channel_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain().eq("res_id", channel_id).eq("model", "discuss.channel")
        fields = ["body", "author_id", "date", "message_type"]
        return self.connector.search_read_records(
            "mail.message", domain=d.build(), fields=fields, limit=limit
        )

    # ── Calendar ───────────────────────────────────────────────────────
    def get_meetings(
        self,
        partner_id: int | None = None,
        start_date: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        d = Domain()
        if partner_id:
            d.eq("partner_ids", partner_id)
        if start_date:
            d.gte("start", start_date)
        fields = [
            "name",
            "start",
            "stop",
            "partner_ids",
            "description",
            "location",
            "allday",
        ]
        return self.connector.search_read_records(
            "calendar.event", domain=d.build(), fields=fields, limit=limit
        )

    def update_meeting(self, meeting_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_record("calendar.event", meeting_id, data)

    def delete_meeting(self, meeting_id: int) -> bool:
        return self.connector.execute_method("calendar.event", "unlink", [[meeting_id]])

    # ── Quality ────────────────────────────────────────────────────────
    def get_quality_alerts(
        self, product_id: int | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        d = Domain()
        if product_id:
            d.eq("product_id", product_id)
        if date_from:
            d.gte("create_date", date_from)
        if date_to:
            d.lte("create_date", date_to)
        fields = [
            "name",
            "product_id",
            "team_id",
            "stage_id",
            "priority",
            "description",
            "create_date",
        ]
        return self.connector.search_read_records(
            "quality.alert", domain=d.build(), fields=fields, limit=limit, offset=offset
        )

    def update_quality_alert(self, alert_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_record("quality.alert", alert_id, data)

    def get_quality_points(self, limit: int = 50) -> list[dict[str, Any]]:
        fields = [
            "name",
            "product_ids",
            "picking_type_ids",
            "measure_on",
            "test_type_id",
            "team_id",
        ]
        return self.connector.search_read_records(
            "quality.point", domain=[], fields=fields, limit=limit
        )

    # ── Production / Manufacturing ─────────────────────────────────────
    def update_manufacturing_order(self, mo_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_record("mrp.production", mo_id, data)

    def confirm_manufacturing_order(self, mo_id: int) -> Any:
        return self.connector.execute_method(
            "mrp.production", "action_confirm", [[mo_id]]
        )

    def get_bill_of_materials(
        self, product_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain()
        if product_id:
            d.eq("product_tmpl_id", product_id)
        fields = ["product_tmpl_id", "product_qty", "code", "type", "bom_line_ids"]
        return self.connector.search_read_records(
            "mrp.bom", domain=d.build(), fields=fields, limit=limit
        )

    def get_work_orders(
        self, mo_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain()
        if mo_id:
            d.eq("production_id", mo_id)
        fields = [
            "name",
            "production_id",
            "workcenter_id",
            "state",
            "date_start",
            "date_finished",
            "duration",
        ]
        return self.connector.search_read_records(
            "mrp.workorder", domain=d.build(), fields=fields, limit=limit
        )

    def get_wip_stock_by_stage(self, product_id: int) -> list[dict[str, Any]]:
        d = Domain().eq("product_id", product_id).in_("state", ["pending", "waiting", "ready", "progress"])
        fields = [
            "name",
            "production_id",
            "workcenter_id",
            "state",
            "qty_producing",
            "qty_production",
            "qty_remaining",
        ]
        return self.connector.search_read_records(
            "mrp.workorder", domain=d.build(), fields=fields, limit=500
        )

    # ── Pre-Production (Planning) ──────────────────────────────────────
    def get_workcenters(self, limit: int = 50) -> list[dict[str, Any]]:
        fields = [
            "name",
            "code",
            "active",
            "capacity",
            "time_efficiency",
            "working_state",
        ]
        return self.connector.search_read_records(
            "mrp.workcenter", domain=[], fields=fields, limit=limit
        )

    def get_routings(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get BOM operations (routings) — Odoo 17+ stores these on mrp.routing.workcenter."""
        fields = ["name", "workcenter_id", "bom_id", "time_cycle_manual", "sequence"]
        return self.connector.search_read_records(
            "mrp.routing.workcenter", domain=[], fields=fields, limit=limit
        )

    # ── Purchase ───────────────────────────────────────────────────────
    def update_purchase_order(self, po_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_record("purchase.order", po_id, data)

    def confirm_purchase_order(self, po_id: int) -> Any:
        return self.connector.execute_method(
            "purchase.order", "button_confirm", [[po_id]]
        )

    def get_purchase_order_lines(self, po_id: int) -> list[dict[str, Any]]:
        d = Domain().eq("order_id", po_id)
        fields = [
            "product_id",
            "product_qty",
            "price_unit",
            "price_subtotal",
            "date_planned",
            "qty_received",
        ]
        return self.connector.search_read_records(
            "purchase.order.line", domain=d.build(), fields=fields, limit=200
        )

    def get_vendor_bills(
        self, partner_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain().eq("move_type", "in_invoice")
        if partner_id:
            d.eq("partner_id", partner_id)
        fields = [
            "name",
            "partner_id",
            "amount_total",
            "state",
            "invoice_date",
            "payment_state",
        ]
        return self.connector.search_read_records(
            "account.move", domain=d.build(), fields=fields, limit=limit
        )

    # ── Invoicing ──────────────────────────────────────────────────────
    def get_invoices(
        self, partner_id: int | None = None, state: str | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        d = Domain().eq("move_type", "out_invoice")
        if partner_id:
            d.eq("partner_id", partner_id)
        if state:
            d.eq("state", state)
        if date_from:
            d.gte("invoice_date", date_from)
        if date_to:
            d.lte("invoice_date", date_to)
        fields = [
            "name",
            "partner_id",
            "amount_total",
            "amount_residual",
            "state",
            "invoice_date",
            "payment_state",
        ]
        return self.connector.search_read_records(
            "account.move", domain=d.build(), fields=fields, limit=limit, offset=offset
        )

    def post_invoice(self, invoice_id: int) -> Any:
        return self.connector.execute_method(
            "account.move", "action_post", [[invoice_id]]
        )

    def register_payment(
        self, invoice_id: int, amount: float, journal_id: int
    ) -> dict[str, Any]:
        """Register a payment against an invoice using the payment wizard."""
        wizard_data = {
            "payment_type": "inbound",
            "partner_type": "customer",
            "amount": amount,
            "journal_id": journal_id,
        }
        wizard_id = self.connector.create_record(
            "account.payment.register", wizard_data
        )
        return self.connector.execute_method(
            "account.payment.register", "action_create_payments", [[wizard_id]]
        )

    def get_payment_journals(self) -> list[dict[str, Any]]:
        d = Domain().eq("type", "bank")
        fields = ["name", "type", "currency_id"]
        return self.connector.search_read_records(
            "account.journal", domain=d.build(), fields=fields, limit=20
        )

    # ── Advanced Manufacturing & PLM ───────────────────────────────────
    def get_mo_raw_materials(self, limit: int = 500) -> list[dict[str, Any]]:
        # Fetch raw material moves for active MOs
        return self.connector.search_read_records(
            "stock.move",
            domain=[("raw_material_production_id", "!=", False), ("state", "not in", ["done", "cancel"])],
            fields=["product_id", "product_uom_qty", "quantity", "raw_material_production_id", "state"],
            limit=limit,
        )

    def get_active_work_orders_duration(self, limit: int = 200) -> list[dict[str, Any]]:
        return self.connector.search_read_records(
            "mrp.workorder",
            domain=[("state", "in", ["ready", "progress"])],
            fields=["name", "workcenter_id", "production_id", "duration", "duration_expected", "state"],
            limit=limit,
        )

    def get_bom_lines(
        self, bom_id: int | None = None, limit: int = 200
    ) -> list[dict[str, Any]]:
        d = Domain()
        if bom_id:
            d.eq("bom_id", bom_id)
        fields = ["bom_id", "product_id", "product_qty", "product_uom_id"]
        return self.connector.search_read_records(
            "mrp.bom.line", domain=d.build(), fields=fields, limit=limit
        )

    def create_eco(self, product_tmpl_id: int, type_id: int, name: str) -> int:
        data = {
            "product_tmpl_id": product_tmpl_id,
            "type_id": type_id,
            "name": name,
        }
        return self.connector.create_record("mrp.eco", data)

    def get_equipment_oee(
        self, workcenter_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        d = Domain()
        if workcenter_id:
            d.eq("workcenter_id", workcenter_id)
        fields = ["workcenter_id", "loss_id", "duration", "date_start", "date_end"]
        return self.connector.search_read_records(
            "mrp.workcenter.productivity", domain=d.build(), fields=fields, limit=limit
        )

    def get_mps_forecast(self, limit: int = 50) -> list[dict[str, Any]]:
        """Requires mrp_mps module."""
        fields = [
            "product_id",
            "forecast_qty",
            "replenish_qty",
            "starting_inventory_qty",
        ]
        return self.connector.search_read_records(
            "mrp.production.schedule", domain=[], fields=fields, limit=limit
        )

    def run_mrp_scheduler(self) -> Any:
        return self.connector.execute_method("procurement.group", "run_scheduler", [])

    def trace_lot_number(
        self, lot_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        d = Domain()
        if lot_id:
            d.eq("lot_id", lot_id)
        fields = [
            "product_id",
            "lot_id",
            "reference",
            "location_id",
            "location_dest_id",
            "qty_done",
            "state",
        ]
        return self.connector.search_read_records(
            "stock.move.line", domain=d.build(), fields=fields, limit=limit
        )

    def log_work_order_time(
        self, workorder_id: int, duration_minutes: float, loss_id: int | None = None
    ) -> int:
        data = {
            "workorder_id": workorder_id,
            "duration": duration_minutes,
        }
        if loss_id:
            data["loss_id"] = loss_id
        return self.connector.create_record("mrp.workcenter.productivity", data)

    # ── Maintenance ────────────────────────────────────────────────────
    def create_maintenance_request(
        self,
        name: str,
        equipment_id: int,
        description: str | None = None,
        priority: str = "0",
    ) -> int:
        data = {
            "name": name,
            "equipment_id": equipment_id,
            "priority": priority,
        }
        if description:
            data["description"] = description
        return self.connector.create_record("maintenance.request", data)

    def get_equipment_status(
        self, equipment_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain()
        if equipment_id:
            d.eq("id", equipment_id)
        fields = [
            "name",
            "category_id",
            "active",
            "next_action_date",
            "cost",
            "location",
        ]
        return self.connector.search_read_records(
            "maintenance.equipment", domain=d.build(), fields=fields, limit=limit
        )

    def get_maintenance_requests(
        self, equipment_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        d = Domain()
        if equipment_id:
            d.eq("equipment_id", equipment_id)
        fields = [
            "name",
            "equipment_id",
            "request_date",
            "schedule_date",
            "stage_id",
            "priority",
        ]
        return self.connector.search_read_records(
            "maintenance.request", domain=d.build(), fields=fields, limit=limit
        )
