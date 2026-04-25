"""Coordinator dashboard API (tablet / ops friendly)."""

from fastapi import APIRouter, Depends

from app.api.deps.auth_deps import auth_principal, require_role
from app.services.destination_service import assign_destination
from app.services.graph_matching_service import get_best_match
from app.services.route_service import compute_route

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


@router.get("/snapshot")
def coordinator_snapshot(principal: dict[str, str] = Depends(auth_principal)) -> dict:
    require_role(principal, "organization")
    # TODO(Phase1): aggregate Neo4j metrics (open incidents, hospital load, etc.).
    return {
        "open_incidents": 3,
        "route_preview": compute_route(from_id="inc-001", to_id="hosp-001"),
        "assignment": assign_destination(incident_id="inc-001", destination_id="hosp-001").model_dump(),
        "matching": get_best_match(incident_id="inc-001", candidate_ids=["vol-001", "vol-002", "vol-003"]),
    }
