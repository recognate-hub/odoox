from datetime import datetime

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
