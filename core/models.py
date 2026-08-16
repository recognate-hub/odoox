import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserWorkspace(Base):
    __tablename__ = 'user_workspaces'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Refers to Supabase auth.users but we don't define that table here
    user_id = Column(UUID(as_uuid=True), nullable=False)
    odoo_url = Column(String, nullable=False)
    odoo_db = Column(String, nullable=False)
    odoo_username = Column(String, nullable=False)
    odoo_password = Column(String, nullable=False)
    role = Column(String, default="Admin", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    plan_type = Column(String, nullable=False, default="single")
    created_at = Column(DateTime, default=datetime.utcnow)

class RevokedApiKey(Base):
    __tablename__ = 'revoked_api_keys'

    api_key = Column(String, primary_key=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
