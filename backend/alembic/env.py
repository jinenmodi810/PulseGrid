"""Alembic migration environment (loads DATABASE_URL from the process environment)."""

from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure `app` package is importable when running `alembic` from backend/
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment,misc]


def _load_env_files() -> None:
    """Load env vars from repo-root `.env` then `backend/.env` (backend wins on duplicate keys)."""
    if load_dotenv is None:
        return
    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(backend_dir / ".env", override=True)


_load_env_files()

from app.db.sql.base import Base  # noqa: E402
from app.db.sql.models import (  # noqa: E402,F401  # pylint: disable=unused-import
    EventOutbox,
    Incident,
    IncidentAssignment,
    IncidentEvent,
    Organization,
    ResponderProfile,
    User,
    VictimProfile,
    Zone,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    url = (os.environ.get("DATABASE_URL") or "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to backend/.env (recommended) or the repo-root .env, "
            "for example:\n"
            "  DATABASE_URL=postgresql+psycopg2://jinenmodi@localhost:5432/pulsegrid_db\n"
            "Or: export DATABASE_URL='...' in this shell, then run alembic again.\n"
            "Note: run alembic from the backend directory (no extra `cd backend` if you are already there)."
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
