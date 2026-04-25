"""Victim / resident profile table (matches Flutter victim registration).

Revision ID: 0002_victim_profiles
Revises: 0001_pg_foundation
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_victim_profiles"
down_revision: Union[str, None] = "0001_pg_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "victim_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("preferred_language", sa.String(length=32), server_default="en", nullable=False),
        sa.Column("home_zone_id", sa.String(length=120), nullable=False),
        sa.Column("household_size", sa.Integer(), nullable=True),
        sa.Column("elderly_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mobility_concern", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("oxygen_dependency", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("emergency_contact_name", sa.String(length=200), nullable=False),
        sa.Column("emergency_contact_phone", sa.String(length=40), nullable=False),
        sa.Column("emergency_contact_relationship", sa.String(length=120), server_default="", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_victim_profiles_home_zone_id"), "victim_profiles", ["home_zone_id"], unique=False)
    op.create_index(op.f("ix_victim_profiles_user_id"), "victim_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_victim_profiles_user_id"), table_name="victim_profiles")
    op.drop_index(op.f("ix_victim_profiles_home_zone_id"), table_name="victim_profiles")
    op.drop_table("victim_profiles")
