from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ── Model safety ────────────────────────────────────────────────────
# Odoo internal models that should NEVER be accessed through generic
# MCP tools.  Restricting these prevents an LLM from accidentally
# escalating privileges, deleting security rules, or modifying
# access-control lists via create_record / update_record.
_BLOCKED_MODEL_PREFIXES: tuple[str, ...] = (
    "ir.",          # Internal / access rules / crons
    "base.",        # Low-level framework models
    "bus.",         # Real-time bus (websocket internals)
)
_BLOCKED_MODELS: frozenset[str] = frozenset({
    "res.users",              # User accounts — use admin panel instead
    "res.groups",             # Security groups
    "res.config.settings",    # System configuration
})


def _validate_model_name(v: str) -> str:
    """Reject dangerous Odoo model names at the schema level."""
    v = v.strip()
    if not v or "." not in v:
        raise ValueError(
            f"'{v}' is not a valid Odoo model name.  "
            "Model names must use dot notation (e.g. 'sale.order')."
        )
    if v in _BLOCKED_MODELS:
        raise ValueError(f"Access to model '{v}' is blocked for security reasons.")
    for prefix in _BLOCKED_MODEL_PREFIXES:
        if v.startswith(prefix):
            raise ValueError(
                f"Access to internal model '{v}' (prefix '{prefix}') "
                "is blocked for security reasons."
            )
    return v

class CreateLeadInput(BaseModel):
    name: str = Field(..., max_length=100, description="The name or title of the lead.")
    email: EmailStr | None = Field(None, description="A valid email address for the lead.")
    phone: str | None = Field(None, max_length=20, pattern=r'^\+?[\d\s\-\(\)]+$', description="Phone number format.")
    description: str | None = Field(None, max_length=1000, description="Additional notes or description.")

class UpdateLeadInput(BaseModel):
    lead_id: int = Field(..., gt=0, description="The ID of the lead to update.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields to update.")

    # Whitelist of CRM lead fields safe to update via this tool
    _ALLOWED_FIELDS: frozenset[str] = frozenset({
        "name", "email_from", "phone", "mobile", "description",
        "expected_revenue", "probability", "priority", "stage_id",
        "partner_id", "user_id", "team_id", "date_deadline",
        "tag_ids", "source_id", "medium_id", "campaign_id",
        "street", "city", "state_id", "country_id", "zip",
        "website", "contact_name", "function",
    })

    @model_validator(mode="after")
    def validate_data_keys(self) -> "UpdateLeadInput":
        """Reject writes to unknown or dangerous fields."""
        bad_keys = set(self.data.keys()) - self._ALLOWED_FIELDS
        if bad_keys:
            raise ValueError(
                f"Cannot update disallowed CRM fields: {', '.join(sorted(bad_keys))}. "
                f"Allowed fields: {', '.join(sorted(self._ALLOWED_FIELDS))}"
            )
        return self

class ScheduleMeetingInput(BaseModel):
    name: str = Field(..., max_length=100, description="The title of the meeting.")
    start: str = Field(..., description="Start time of the meeting.")
    stop: str = Field(..., description="Stop time of the meeting.")
    partner_ids: list[int] = Field(..., description="List of partner IDs to invite.")
    notes: str | None = Field("", max_length=2000, description="Meeting notes or agenda.")

    @field_validator('start', 'stop')
    def validate_iso_format(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Must be a valid ISO 8601 string.")
        return v

class LogActivityInput(BaseModel):
    res_model: str = Field(..., description="The Odoo model to attach the note to (e.g. 'crm.lead' or 'res.partner').")
    res_id: int = Field(..., description="The ID of the record.")
    summary: str = Field(..., max_length=1000, description="The content of the note or activity summary.")

class CreateInvoiceInput(BaseModel):
    partner_id: int = Field(..., description="The ID of the customer (partner) to invoice.")
    amount: float = Field(..., gt=0, description="The total amount for the invoice line item.")
    description: str = Field("Consulting Services", max_length=500, description="The description for the invoice line item.")

class SendEmailInput(BaseModel):
    email_to: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., max_length=200, description="The subject line of the email.")
    body: str = Field(..., description="The HTML or plain text body of the email.")

class CreateContactInput(BaseModel):
    name: str = Field(..., max_length=150, description="The full name of the contact or company.")
    email: EmailStr | None = Field(None, description="The email address of the contact.")
    phone: str | None = Field(None, max_length=20, pattern=r'^\+?[\d\s\-\(\)]+$', description="Phone number format.")
    is_company: bool = Field(False, description="Set to true if this contact represents a company rather than an individual.")

class CreateProductInput(BaseModel):
    name: str = Field(..., max_length=150, description="The name of the product or service.")
    list_price: float = Field(..., ge=0, description="The sale price of the product.")
    default_code: str | None = Field(None, max_length=50, description="The internal reference or SKU for the product.")
    product_type: str = Field("service", description="Product type. Usually 'consu' (Consumable), 'service' (Service), or 'product' (Storable Product).")

class QuoteLineInput(BaseModel):
    product_id: int = Field(..., description="The ID of the product.")
    quantity: float = Field(1.0, gt=0, description="The quantity to order.")
    price_unit: float | None = Field(None, ge=0, description="The unit price. If omitted, Odoo will use the product's default list price.")

class CreateQuoteInput(BaseModel):
    partner_id: int = Field(..., description="The ID of the customer (partner) to create the quote for.")
    order_lines: list[QuoteLineInput] = Field(..., min_length=1, description="List of products and quantities to include in the quote.")


class SearchReadInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name (e.g. 'hr.employee', 'project.task').")
    domain: list[list[Any]] | None = Field(None, description="The search domain to filter records.")
    fields: list[str] | None = Field(None, description="List of specific fields to return. If omitted, all fields are returned.")
    limit: int = Field(50, ge=1, le=200, description="The maximum number of records to return.")
    offset: int = Field(0, ge=0, description="The number of records to skip for pagination.")

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        return _validate_model_name(v)


class CreateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields and values to create the record.")

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        return _validate_model_name(v)


class UpdateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    record_id: int = Field(..., gt=0, description="The ID of the record to update.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields and values to update.")

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        return _validate_model_name(v)

class BatchCreateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    records: list[dict[str, Any]] = Field(..., description="List of dictionaries of fields and values to create multiple records.")

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        return _validate_model_name(v)

class BatchUpdateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    record_ids: list[int] = Field(..., min_length=1, description="The IDs of the records to update.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields and values to apply to all given record IDs.")

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        return _validate_model_name(v)

class GetModelFieldsInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name to get fields for.")


class ReadGroupInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    domain: list[list[Any]] | None = Field(None, description="The search domain to filter records.")
    fields: list[str] = Field(..., description="List of fields to fetch/aggregate. Must include the groupby fields.")
    groupby: list[str] = Field(..., description="List of fields to group by.")


class ArchiveRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    record_id: int = Field(..., gt=0, description="The ID of the record to archive/unarchive.")
    archive: bool = Field(True, description="True to archive (active=False), False to unarchive (active=True).")


class CreateAttachmentInput(BaseModel):
    res_model: str = Field(..., description="The Odoo model to attach the file to.")
    res_id: int = Field(..., description="The ID of the record.")
    name: str = Field(..., description="The name of the file (e.g., 'document.pdf').")
    base64_data: str = Field(..., description="The base64 encoded content of the file.")


class ReadAttachmentInput(BaseModel):
    attachment_id: int = Field(..., gt=0, description="The ID of the attachment to read.")

class ExecuteMethodInput(BaseModel):
    model: str = Field(..., description="The Odoo model name.")
    method: str = Field(..., description="The method to call on the model (e.g. 'action_confirm').")
    args: list[Any] = Field(default_factory=list, description="Positional arguments.")
    kwargs: dict[str, Any] = Field(default_factory=dict, description="Keyword arguments.")


class PostMessageInput(BaseModel):
    res_model: str = Field(..., description="The Odoo model to post the message to.")
    res_id: int = Field(..., description="The ID of the record.")
    body: str = Field(..., description="The body of the message (HTML or plain text).")
    message_type: str = Field("comment", description="The type of message (e.g., 'comment', 'notification').")


class CreateChannelInput(BaseModel):
    name: str = Field(..., description="The name of the channel.")
    channel_type: str = Field("channel", description="The type of the channel ('channel', 'chat', 'group').")


class PurchaseOrderLineInput(BaseModel):
    product_id: int = Field(..., description="The ID of the product.")
    product_qty: float = Field(1.0, gt=0, description="The quantity to purchase.")
    price_unit: float | None = Field(None, ge=0, description="The unit price.")


class CreatePurchaseOrderInput(BaseModel):
    partner_id: int = Field(..., description="The ID of the vendor (partner).")
    order_lines: list[PurchaseOrderLineInput] = Field(..., min_length=1, description="List of products and quantities to purchase.")


class CreateManufacturingOrderInput(BaseModel):
    product_id: int = Field(..., description="The ID of the product to manufacture.")
    product_qty: float = Field(1.0, gt=0, description="The quantity to manufacture.")


class CreateStockMoveInput(BaseModel):
    name: str = Field(..., description="Description of the move.")
    product_id: int = Field(..., description="The ID of the product.")
    product_uom_qty: float = Field(..., gt=0, description="The quantity to move.")
    location_id: int = Field(..., description="The source location ID.")
    location_dest_id: int = Field(..., description="The destination location ID.")


class CreateQualityAlertInput(BaseModel):
    name: str = Field(..., description="Title or reference for the quality alert.")
    product_id: int = Field(..., description="The ID of the product related to the alert.")
    team_id: int | None = Field(None, description="The ID of the quality team.")
    priority: str | None = Field("0", description="Priority of the alert ('0', '1', '2', '3').")


# ── Calendar Schemas ──────────────────────────────────────────────────
class UpdateMeetingInput(BaseModel):
    meeting_id: int = Field(..., gt=0, description="The ID of the calendar event to update.")
    data: dict[str, Any] = Field(..., description="Fields to update (e.g., name, start, stop, location).")

class DeleteMeetingInput(BaseModel):
    meeting_id: int = Field(..., gt=0, description="The ID of the calendar event to delete.")


# ── Quality Schemas ───────────────────────────────────────────────────
class UpdateQualityAlertInput(BaseModel):
    alert_id: int = Field(..., gt=0, description="The ID of the quality alert to update.")
    data: dict[str, Any] = Field(..., description="Fields to update (e.g., stage_id, priority, description).")


# ── Production Schemas ────────────────────────────────────────────────
class UpdateManufacturingOrderInput(BaseModel):
    mo_id: int = Field(..., gt=0, description="The ID of the manufacturing order to update.")
    data: dict[str, Any] = Field(..., description="Fields to update (e.g., product_qty, date_start).")

class ConfirmManufacturingOrderInput(BaseModel):
    mo_id: int = Field(..., gt=0, description="The ID of the manufacturing order to confirm.")


# ── Purchase Schemas ──────────────────────────────────────────────────
class UpdatePurchaseOrderInput(BaseModel):
    po_id: int = Field(..., gt=0, description="The ID of the purchase order to update.")
    data: dict[str, Any] = Field(..., description="Fields to update.")

class ConfirmPurchaseOrderInput(BaseModel):
    po_id: int = Field(..., gt=0, description="The ID of the purchase order to confirm.")


# ── Invoicing Schemas ─────────────────────────────────────────────────
class PostInvoiceInput(BaseModel):
    invoice_id: int = Field(..., gt=0, description="The ID of the invoice to post/validate.")

class RegisterPaymentInput(BaseModel):
    invoice_id: int = Field(..., gt=0, description="The ID of the invoice to register payment for.")
    amount: float = Field(..., gt=0, description="The payment amount.")
    journal_id: int = Field(..., gt=0, description="The ID of the payment journal (bank/cash).")

