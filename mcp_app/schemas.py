from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateLeadInput(BaseModel):
    name: str = Field(..., max_length=100, description="The name or title of the lead.")
    email: EmailStr | None = Field(None, description="A valid email address for the lead.")
    phone: str | None = Field(None, max_length=20, pattern=r'^\+?[\d\s\-\(\)]+$', description="Phone number format.")
    description: str | None = Field(None, max_length=1000, description="Additional notes or description.")

class UpdateLeadInput(BaseModel):
    lead_id: int = Field(..., gt=0, description="The ID of the lead to update.")
    data: dict = Field(..., description="Dictionary of fields to update.")
    
    # We can add a custom validator to ensure 'data' fields are safe if needed
    # For now, rely on Odoo's internal protections for dynamic kwargs, 
    # but we can enforce some known keys here if desired.

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


class CreateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields and values to create the record.")


class UpdateRecordInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    model: str = Field(..., description="The Odoo model name.")
    record_id: int = Field(..., gt=0, description="The ID of the record to update.")
    data: dict[str, Any] = Field(..., description="Dictionary of fields and values to update.")

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
