"""Dashboard metrics from Neo4j."""

from fastapi import APIRouter, HTTPException

from app.models.auth_requests import DashboardSummaryResponse
from app.services import auth_neo4j_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary() -> DashboardSummaryResponse:
    try:
        data = auth_neo4j_service.dashboard_summary()
        return DashboardSummaryResponse(**data)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
