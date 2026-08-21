"""initial_schema

Revision ID: 3b1e2c6009d2
Revises:
Create Date: 2026-08-12 13:35:26.137200

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b1e2c6009d2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_workspaces",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("odoo_url", sa.String(), nullable=False),
        sa.Column("odoo_db", sa.String(), nullable=False),
        sa.Column("odoo_username", sa.String(), nullable=False),
        sa.Column("odoo_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="Admin"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_type", sa.String(), nullable=False, server_default="single"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_table(
        "revoked_api_keys",
        sa.Column("api_key", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("revoked_api_keys")
    op.drop_table("payments")
    op.drop_table("user_workspaces")
