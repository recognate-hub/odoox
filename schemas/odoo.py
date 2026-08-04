from typing import Optional, List, Any
from pydantic import BaseModel, Field, model_validator

class OdooBaseModel(BaseModel):
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
    email: Optional[str] = None
    phone: Optional[str] = None
    is_company: bool = False
    company_id: Optional[list] = None  # Odoo returns [id, name] for Many2one


class OdooLead(OdooBaseModel):
    id: int
    name: str
    email_from: Optional[str] = None
    phone: Optional[str] = None
    partner_id: Optional[list] = None
    stage_id: Optional[list] = None
    expected_revenue: float = 0.0
    probability: float = 0.0
    description: Optional[str] = None


class OdooProduct(OdooBaseModel):
    id: int
    name: str
    list_price: float = 0.0
    default_code: Optional[str] = None
    qty_available: float = 0.0


class OdooQuote(OdooBaseModel):
    id: int
    name: str
    partner_id: Optional[list] = None
    state: str
    amount_total: float = 0.0
    date_order: Optional[str] = None


class OdooActivity(OdooBaseModel):
    id: int
    res_model: str
    res_id: int
    activity_type_id: Optional[list] = None
    summary: Optional[str] = None
    date_deadline: Optional[str] = None
    user_id: Optional[list] = None


class OdooMeeting(OdooBaseModel):
    id: int
    name: str
    start: Optional[str] = None
    stop: Optional[str] = None
    partner_ids: List[int] = Field(default_factory=list)


class OdooSalesDashboard(OdooBaseModel):
    total_revenue: float = 0.0
    active_leads_count: int = 0
    quotes_count: int = 0
    win_rate_percentage: float = 0.0
