from typing import Any

from pydantic import BaseModel, Field, model_validator, ConfigDict


class OdooBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='before')
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

    @model_validator(mode='after')
    def sanitize_strings(self) -> 'OdooBaseModel':
        for field_name, field_info in type(self).model_fields.items():
            val = getattr(self, field_name)
            if isinstance(val, str):
                # Escape existing XML/HTML tags
                sanitized = val.replace('<', '&lt;').replace('>', '&gt;')
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
    company_id: list | None = None  # Odoo returns [id, name] for Many2one


class OdooLead(OdooBaseModel):
    id: int
    name: str
    email_from: str | None = None
    phone: str | None = None
    partner_id: list | None = None
    stage_id: list | None = None
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
    partner_id: list | None = None
    state: str
    amount_total: float = 0.0
    date_order: str | None = None


class OdooActivity(OdooBaseModel):
    id: int
    res_model: str
    res_id: int
    activity_type_id: list | None = None
    summary: str | None = None
    date_deadline: str | None = None
    user_id: list | None = None


class OdooMeeting(OdooBaseModel):
    id: int
    name: str
    start: str | None = None
    stop: str | None = None
    partner_ids: list[int] = Field(default_factory=list)


class OdooSalesDashboard(OdooBaseModel):
    total_revenue: float = 0.0
    active_leads_count: int = 0
    quotes_count: int = 0
    win_rate_percentage: float = 0.0


class OdooMessage(OdooBaseModel):
    id: int
    body: str | None = None
    date: str | None = None
    author_id: list | None = None
    res_id: int | None = None
    model: str | None = None


class OdooChannel(OdooBaseModel):
    id: int
    name: str | None = None
    channel_type: str | None = None


class OdooPurchaseOrder(OdooBaseModel):
    id: int
    name: str
    partner_id: list | None = None
    state: str
    amount_total: float = 0.0
    date_order: str | None = None


class OdooManufacturingOrder(OdooBaseModel):
    id: int
    name: str
    product_id: list | None = None
    product_qty: float = 0.0
    state: str
    date_planned_start: str | None = None


class OdooStockMove(OdooBaseModel):
    id: int
    name: str
    product_id: list | None = None
    product_uom_qty: float = 0.0
    location_id: list | None = None
    location_dest_id: list | None = None
    state: str


class OdooQualityAlert(OdooBaseModel):
    id: int
    name: str
    product_id: list | None = None
    team_id: list | None = None
    priority: str | None = None


class OdooQualityCheck(OdooBaseModel):
    id: int
    name: str
    product_id: list | None = None
    quality_state: str | None = None
