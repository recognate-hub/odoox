from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OdooBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def convert_odoo_false_to_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for k, v in data.items():
                if v is False:
                    field = cls.model_fields.get(k)
                    if field and field.annotation is bool:
                        continue
                    data[k] = None
        return data

    @model_validator(mode="after")
    def sanitize_strings(self) -> "OdooBaseModel":
        for field_name in type(self).model_fields:
            val = getattr(self, field_name)
            if isinstance(val, str):
                # Escape existing XML/HTML tags
                sanitized = val.replace("<", "&lt;").replace(">", "&gt;")
                # Wrap in delimiting tags to prevent prompt injection
                wrapped = f"<untrusted_crm_data>{sanitized}</untrusted_crm_data>"
                setattr(self, field_name, wrapped)
        return self


class OdooContact(OdooBaseModel):
    id: int
    name: str
    email: str | None = None
    phone: str | None = None
    is_company: bool = False
    company_id: Any = None  # Odoo returns [id, name] for Many2one, or expanded dict


class OdooLead(OdooBaseModel):
    id: int
    name: str
    email_from: str | None = None
    phone: str | None = None
    partner_id: Any = None
    stage_id: Any = None
    expected_revenue: float = 0.0
    probability: float = 0.0
    description: str | None = None


class OdooProduct(OdooBaseModel):
    id: int
    name: str
    list_price: float = 0.0
    default_code: str | None = None
    qty_available: float = 0.0


class OdooQuote(OdooBaseModel):
    id: int
    name: str
    partner_id: Any = None
    state: str
    amount_total: float = 0.0
    date_order: str | None = None
    order_line: Any = None


class OdooActivity(OdooBaseModel):
    id: int
    res_model: str
    res_id: int
    activity_type_id: Any = None
    summary: str | None = None
    date_deadline: str | None = None
    user_id: Any = None


class OdooMeeting(OdooBaseModel):
    id: int
    name: str
    start: str | None = None
    stop: str | None = None
    partner_ids: Any = Field(default_factory=list)


class OdooSalesDashboard(OdooBaseModel):
    total_revenue: float = 0.0
    active_leads_count: int = 0
    quotes_count: int = 0
    win_rate_percentage: float = 0.0


class OdooMessage(OdooBaseModel):
    id: int
    body: str | None = None
    date: str | None = None
    author_id: Any = None
    res_id: int | None = None
    model: str | None = None


class OdooChannel(OdooBaseModel):
    id: int
    name: str | None = None
    channel_type: str | None = None


class OdooPurchaseOrder(OdooBaseModel):
    id: int
    name: str
    partner_id: Any = None
    state: str
    amount_total: float = 0.0
    date_order: str | None = None
    order_line: Any = None


class OdooManufacturingOrder(OdooBaseModel):
    id: int
    name: str
    product_id: Any = None
    product_qty: float = 0.0
    state: str
    date_planned_start: str | None = None
    bom_id: Any = None
    workorder_ids: Any = None
    move_raw_ids: Any = None


class OdooStockMove(OdooBaseModel):
    id: int
    name: str
    product_id: Any = None
    product_uom_qty: float = 0.0
    location_id: Any = None
    location_dest_id: Any = None
    state: str


class OdooQualityAlert(OdooBaseModel):
    id: int
    name: str
    product_id: Any = None
    team_id: Any = None
    priority: str | None = None


class OdooQualityCheck(OdooBaseModel):
    id: int
    name: str
    product_id: list | None = None
    quality_state: str | None = None
