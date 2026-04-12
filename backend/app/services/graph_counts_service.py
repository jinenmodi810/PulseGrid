"""Read-only Neo4j counts for development verification."""

from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session

_SUMMARY_QUERY = """
OPTIONAL MATCH (u:User)
WITH count(u) AS total_users
OPTIONAL MATCH (v:Volunteer)
WITH total_users, count(v) AS total_volunteers
OPTIONAL MATCH (o:Organization)
WITH total_users, total_volunteers, count(o) AS total_organizations
OPTIONAL MATCH (i:Incident)
WITH total_users, total_volunteers, total_organizations, count(i) AS total_incidents
OPTIONAL MATCH (:Volunteer)-[av:ASSIGNED_TO]->(:Incident)
WITH total_users, total_volunteers, total_organizations, total_incidents, count(av) AS total_assigned_volunteers
OPTIONAL MATCH (io:Incident)
WHERE coalesce(io.assigned_organization_id, '') <> ''
WITH total_users,
     total_volunteers,
     total_organizations,
     total_incidents,
     total_assigned_volunteers,
     count(io) AS total_assigned_organizations
RETURN total_users,
       total_volunteers,
       total_organizations,
       total_incidents,
       total_assigned_volunteers,
       total_assigned_organizations
"""


def persistence_summary() -> dict[str, int]:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> dict[str, Any]:
        rec = tx.run(_SUMMARY_QUERY).single()
        return dict(rec) if rec else {}

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_read(work)
    out: dict[str, int] = {}
    for k in (
        "total_users",
        "total_volunteers",
        "total_organizations",
        "total_incidents",
        "total_assigned_volunteers",
        "total_assigned_organizations",
    ):
        v = row.get(k)
        out[k] = int(v) if v is not None else 0
    return out
