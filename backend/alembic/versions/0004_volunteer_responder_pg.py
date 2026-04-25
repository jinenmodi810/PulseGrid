"""Volunteer responder_profiles: JSON fields, zone FK, demo zone_1 seed.

Revision ID: 0004_volunteer_pg
Revises: 0003_zones_victim_prof
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision: str = "0004_volunteer_pg"
down_revision: Union[str, None] = "0003_zones_victim_prof"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        text("INSERT INTO zones (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING"),
        {"id": "zone_1", "name": "Demo zone 1 (Swagger/tests)"},
    )

    op.drop_column("responder_profiles", "skills")
    op.add_column(
        "responder_profiles",
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    )
    op.add_column(
        "responder_profiles",
        sa.Column("languages", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    )
    op.add_column(
        "responder_profiles",
        sa.Column("support_types", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    )
    op.add_column("responder_profiles", sa.Column("transport_access", sa.String(length=80), nullable=True))
    op.add_column(
        "responder_profiles",
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("responder_profiles", sa.Column("skill_type", sa.String(length=120), nullable=True))
    op.add_column(
        "responder_profiles",
        sa.Column("credits", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "responder_profiles",
        sa.Column("trust_score", sa.Float(), server_default=sa.text("0.5"), nullable=False),
    )

    op.execute(
        text("""
        UPDATE responder_profiles AS rp
        SET zone_id = 'zone-riverside'
        WHERE zone_id IS NULL
           OR NOT EXISTS (SELECT 1 FROM zones z WHERE z.id = rp.zone_id)
        """)
    )

    op.create_foreign_key(
        "responder_profiles_zone_id_fkey",
        "responder_profiles",
        "zones",
        ["zone_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("responder_profiles_zone_id_fkey", "responder_profiles", type_="foreignkey")
    op.drop_column("responder_profiles", "trust_score")
    op.drop_column("responder_profiles", "credits")
    op.drop_column("responder_profiles", "skill_type")
    op.drop_column("responder_profiles", "verified")
    op.drop_column("responder_profiles", "transport_access")
    op.drop_column("responder_profiles", "support_types")
    op.drop_column("responder_profiles", "languages")
    op.drop_column("responder_profiles", "skills")
    op.add_column(
        "responder_profiles",
        sa.Column("skills", sa.Text(), nullable=True),
    )
    bind = op.get_bind()
    bind.execute(text("DELETE FROM zones WHERE id = :id"), {"id": "zone_1"})
