"""Organization row: auth + org type + contact + coverage + capacity (Flutter parity).

Revision ID: 0006_org_pg
Revises: 0005_rm_zone_demo
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision: str = "0006_org_pg"
down_revision: Union[str, None] = "0005_rm_zone_demo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("hashed_password", sa.String(length=255), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("org_type", sa.String(length=80), server_default="ngo", nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("contact_name", sa.String(length=200), server_default="", nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "coverage_zone_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("beds_available", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("oxygen_units", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("ambulances_available", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("shelter_units", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("food_capacity_units", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("rescue_units", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )

    op.execute(
        text("""
        UPDATE organizations AS o
        SET zone_id = 'zone-riverside'
        WHERE zone_id IS NULL
           OR NOT EXISTS (SELECT 1 FROM zones z WHERE z.id = o.zone_id)
        """)
    )

    op.create_foreign_key(
        "organizations_zone_id_fkey",
        "organizations",
        "zones",
        ["zone_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("organizations_zone_id_fkey", "organizations", type_="foreignkey")
    op.drop_column("organizations", "rescue_units")
    op.drop_column("organizations", "food_capacity_units")
    op.drop_column("organizations", "shelter_units")
    op.drop_column("organizations", "ambulances_available")
    op.drop_column("organizations", "oxygen_units")
    op.drop_column("organizations", "beds_available")
    op.drop_column("organizations", "coverage_zone_ids")
    op.drop_column("organizations", "contact_name")
    op.drop_column("organizations", "org_type")
    op.drop_column("organizations", "hashed_password")
