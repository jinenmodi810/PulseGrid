"""Singleton Neo4j driver for AuraDB and on-prem instances."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional

from neo4j import Driver, GraphDatabase

from app.core.config import Settings, get_settings

_driver: Optional[Driver] = None


@contextmanager
def managed_neo4j_session(driver: Driver, settings: Settings) -> Iterator[Any]:
    """Open a read/write session; omit `database` when settings request server default."""
    name = settings.resolved_neo4j_database()
    if name is not None:
        with driver.session(database=name) as session:
            yield session
    else:
        with driver.session() as session:
            yield session


def get_driver() -> Driver:
    """Return shared Neo4j driver (creates on first use)."""
    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            connection_timeout=float(settings.NEO4J_CONNECTION_TIMEOUT),
            connection_acquisition_timeout=float(settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT),
        )
    return _driver


def close_driver() -> None:
    """Close driver if open (call on app shutdown)."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
