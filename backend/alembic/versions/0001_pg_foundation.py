"""Initial PostgreSQL schema: users, orgs, incidents, responders, assignments, events.

Revision ID: 0001_pg_foundation
Revises:
Create Date: 2026-04-16

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_pg_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("contact_email", sa.String(length=320), nullable=False),
        sa.Column("contact_phone", sa.String(length=64), nullable=True),
        sa.Column("zone_id", sa.String(length=128), nullable=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organizations_contact_email"), "organizations", ["contact_email"], unique=True)
    op.create_index(op.f("ix_organizations_owner_user_id"), "organizations", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_organizations_zone_id"), "organizations", ["zone_id"], unique=False)

    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reporter_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("incident_type", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="open", nullable=False),
        sa.Column("severity", sa.String(length=32), server_default="medium", nullable=False),
        sa.Column("priority_score", sa.Float(), nullable=True),
        sa.Column("priority_label", sa.String(length=64), nullable=True),
        sa.Column("zone_id", sa.String(length=128), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_incidents_incident_type"), "incidents", ["incident_type"], unique=False)
    op.create_index(op.f("ix_incidents_organization_id"), "incidents", ["organization_id"], unique=False)
    op.create_index(op.f("ix_incidents_priority_score"), "incidents", ["priority_score"], unique=False)
    op.create_index(op.f("ix_incidents_reporter_user_id"), "incidents", ["reporter_user_id"], unique=False)
    op.create_index(op.f("ix_incidents_status"), "incidents", ["status"], unique=False)
    op.create_index(op.f("ix_incidents_severity"), "incidents", ["severity"], unique=False)
    op.create_index(op.f("ix_incidents_zone_id"), "incidents", ["zone_id"], unique=False)

    op.create_table(
        "responder_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("zone_id", sa.String(length=128), nullable=True),
        sa.Column("availability", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_responder_profiles_user_id"), "responder_profiles", ["user_id"], unique=True)
    op.create_index(op.f("ix_responder_profiles_zone_id"), "responder_profiles", ["zone_id"], unique=False)

    op.create_table(
        "incident_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("responder_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["responder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("incident_id", "responder_user_id", name="uq_assignment_incident_responder"),
    )
    op.create_index(op.f("ix_incident_assignments_incident_id"), "incident_assignments", ["incident_id"], unique=False)
    op.create_index(
        op.f("ix_incident_assignments_responder_user_id"),
        "incident_assignments",
        ["responder_user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_incident_assignments_status"), "incident_assignments", ["status"], unique=False)

    op.create_table(
        "incident_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_incident_events_actor_user_id"), "incident_events", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_incident_events_created_at"), "incident_events", ["created_at"], unique=False)
    op.create_index(op.f("ix_incident_events_event_type"), "incident_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_incident_events_incident_id"), "incident_events", ["incident_id"], unique=False)
    op.create_index(
        "ix_incident_events_incident_created",
        "incident_events",
        ["incident_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_incident_events_incident_created", table_name="incident_events")
    op.drop_index(op.f("ix_incident_events_incident_id"), table_name="incident_events")
    op.drop_index(op.f("ix_incident_events_event_type"), table_name="incident_events")
    op.drop_index(op.f("ix_incident_events_created_at"), table_name="incident_events")
    op.drop_index(op.f("ix_incident_events_actor_user_id"), table_name="incident_events")
    op.drop_table("incident_events")

    op.drop_index(op.f("ix_incident_assignments_status"), table_name="incident_assignments")
    op.drop_index(op.f("ix_incident_assignments_responder_user_id"), table_name="incident_assignments")
    op.drop_index(op.f("ix_incident_assignments_incident_id"), table_name="incident_assignments")
    op.drop_table("incident_assignments")

    op.drop_index(op.f("ix_responder_profiles_zone_id"), table_name="responder_profiles")
    op.drop_index(op.f("ix_responder_profiles_user_id"), table_name="responder_profiles")
    op.drop_table("responder_profiles")

    op.drop_index(op.f("ix_incidents_zone_id"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_severity"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_status"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_reporter_user_id"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_priority_score"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_organization_id"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_incident_type"), table_name="incidents")
    op.drop_table("incidents")

    op.drop_index(op.f("ix_organizations_zone_id"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_owner_user_id"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_contact_email"), table_name="organizations")
    op.drop_table("organizations")

    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
