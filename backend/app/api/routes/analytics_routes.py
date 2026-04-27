"""Analytics API endpoints over Gold marts (DuckDB)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.analytics_models import (
    AnalyticsOverviewResponse,
    IncidentByZoneItem,
    OrganizationCapacityItem,
    TimeToResponseResponse,
    VolunteerPerformanceItem,
)
from app.observability.metrics import analytics_data_not_ready_total, analytics_query_failure_total
from app.services.analytics_service import AnalyticsDataNotReadyError, AnalyticsFilters
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _filters(
    zone_id: str | None = Query(default=None),
    organization_id: str | None = Query(default=None),
    volunteer_id: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> AnalyticsFilters:
    return AnalyticsFilters(
        zone_id=zone_id,
        organization_id=organization_id,
        volunteer_id=volunteer_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_overview(
    zone_id: str | None = Query(default=None),
    organization_id: str | None = Query(default=None),
    volunteer_id: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> AnalyticsOverviewResponse:
    try:
        out = analytics_service.query_overview(_filters(zone_id, organization_id, volunteer_id, start_date, end_date))
        return AnalyticsOverviewResponse(**out)
    except AnalyticsDataNotReadyError as exc:
        analytics_data_not_ready_total.labels(endpoint="/analytics/overview").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        analytics_query_failure_total.labels(endpoint="/analytics/overview").inc()
        raise HTTPException(status_code=500, detail=f"Analytics overview query failed: {exc}") from exc


@router.get("/incidents-by-zone", response_model=list[IncidentByZoneItem])
def get_incidents_by_zone(
    zone_id: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> list[IncidentByZoneItem]:
    try:
        rows = analytics_service.query_incidents_by_zone(_filters(zone_id, None, None, start_date, end_date))
        return [IncidentByZoneItem(**r) for r in rows]
    except AnalyticsDataNotReadyError as exc:
        analytics_data_not_ready_total.labels(endpoint="/analytics/incidents-by-zone").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        analytics_query_failure_total.labels(endpoint="/analytics/incidents-by-zone").inc()
        raise HTTPException(status_code=500, detail=f"Analytics incidents-by-zone query failed: {exc}") from exc


@router.get("/volunteer-performance", response_model=list[VolunteerPerformanceItem])
def get_volunteer_performance(
    volunteer_id: str | None = Query(default=None),
) -> list[VolunteerPerformanceItem]:
    try:
        rows = analytics_service.query_volunteer_performance(_filters(None, None, volunteer_id, None, None))
        return [VolunteerPerformanceItem(**r) for r in rows]
    except AnalyticsDataNotReadyError as exc:
        analytics_data_not_ready_total.labels(endpoint="/analytics/volunteer-performance").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        analytics_query_failure_total.labels(endpoint="/analytics/volunteer-performance").inc()
        raise HTTPException(status_code=500, detail=f"Analytics volunteer-performance query failed: {exc}") from exc


@router.get("/organization-capacity", response_model=list[OrganizationCapacityItem])
def get_organization_capacity(
    organization_id: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> list[OrganizationCapacityItem]:
    try:
        rows = analytics_service.query_organization_capacity(
            _filters(None, organization_id, None, start_date, end_date)
        )
        return [OrganizationCapacityItem(**r) for r in rows]
    except AnalyticsDataNotReadyError as exc:
        analytics_data_not_ready_total.labels(endpoint="/analytics/organization-capacity").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        analytics_query_failure_total.labels(endpoint="/analytics/organization-capacity").inc()
        raise HTTPException(status_code=500, detail=f"Analytics organization-capacity query failed: {exc}") from exc


@router.get("/time-to-response", response_model=TimeToResponseResponse)
def get_time_to_response(
    zone_id: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> TimeToResponseResponse:
    try:
        out = analytics_service.query_time_to_response(_filters(zone_id, None, None, start_date, end_date))
        return TimeToResponseResponse(**out)
    except AnalyticsDataNotReadyError as exc:
        analytics_data_not_ready_total.labels(endpoint="/analytics/time-to-response").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        analytics_query_failure_total.labels(endpoint="/analytics/time-to-response").inc()
        raise HTTPException(status_code=500, detail=f"Analytics time-to-response query failed: {exc}") from exc
