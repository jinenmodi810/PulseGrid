"""Remove demo zone_1; align with Flutter-only zone ids.

Revision ID: 0005_rm_zone_demo
Revises: 0004_volunteer_pg
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "0005_rm_zone_demo"
down_revision: Union[str, None] = "0004_volunteer_pg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        text("UPDATE responder_profiles SET zone_id = 'zone-riverside' WHERE zone_id = 'zone_1'"),
    )
    bind.execute(
        text("UPDATE victim_profiles SET home_zone_id = 'zone-riverside' WHERE home_zone_id = 'zone_1'"),
    )
    bind.execute(text("DELETE FROM zones WHERE id = 'zone_1'"))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        text("INSERT INTO zones (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING"),
        {"id": "zone_1", "name": "Demo zone 1 (Swagger/tests)"},
    )
