"""Zones table, victim profile full_name + account_id, users.display_name (drop users.full_name).

Revision ID: 0003_zones_victim_prof  (<=32 chars for alembic_version.version_num)
Revises: 0002_victim_profiles
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "0003_zones_victim_prof"
down_revision: Union[str, None] = "0002_victim_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical zone ids (see Flutter ``lib/features/auth/presentation/constants/zone_options.dart``).
_SEED_ZONES: list[tuple[str, str]] = [
    ("zone-riverside", "Riverside"),
    ("zone-central", "Central"),
    ("zone-north", "North"),
    ("zone-east", "East"),
]


def upgrade() -> None:
    op.create_table(
        "zones",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    bind = op.get_bind()
    for zid, label in _SEED_ZONES:
        bind.execute(
            text("INSERT INTO zones (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING"),
            {"id": zid, "name": label},
        )

    op.add_column("victim_profiles", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.execute(
        """
        UPDATE victim_profiles AS vp
        SET full_name = u.full_name
        FROM users AS u
        WHERE vp.user_id = u.id
        """
    )
    op.execute("UPDATE victim_profiles SET full_name = 'Unknown' WHERE full_name IS NULL")
    op.alter_column("victim_profiles", "full_name", existing_type=sa.String(length=255), nullable=False)

    op.add_column("users", sa.Column("display_name", sa.String(length=255), nullable=True))
    op.execute("UPDATE users SET display_name = full_name")

    op.drop_constraint("victim_profiles_user_id_fkey", "victim_profiles", type_="foreignkey")
    op.alter_column("victim_profiles", "user_id", new_column_name="account_id")

    op.create_foreign_key(
        "victim_profiles_account_id_fkey",
        "victim_profiles",
        "users",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "victim_profiles_home_zone_id_fkey",
        "victim_profiles",
        "zones",
        ["home_zone_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.drop_column("users", "full_name")


def downgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.execute(
        """
        UPDATE users AS u
        SET full_name = vp.full_name
        FROM victim_profiles AS vp
        WHERE vp.account_id = u.id
        """
    )
    op.execute("UPDATE users SET full_name = coalesce(display_name, 'Unknown') WHERE full_name IS NULL")
    op.alter_column("users", "full_name", existing_type=sa.String(length=255), nullable=False)

    op.drop_constraint("victim_profiles_home_zone_id_fkey", "victim_profiles", type_="foreignkey")
    op.drop_constraint("victim_profiles_account_id_fkey", "victim_profiles", type_="foreignkey")

    op.alter_column("victim_profiles", "account_id", new_column_name="user_id")
    op.create_foreign_key(
        "victim_profiles_user_id_fkey",
        "victim_profiles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_column("victim_profiles", "full_name")
    op.drop_column("users", "display_name")

    op.drop_table("zones")
