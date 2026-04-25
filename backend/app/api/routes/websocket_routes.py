"""WebSocket channels for live UI updates with JWT session validation."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from starlette.websockets import WebSocketState

from app.core.security import decode_access_token
from app.realtime.connection_manager import connection_manager

router = APIRouter(tags=["realtime"])


def _principal_from_websocket(websocket: WebSocket) -> dict[str, str] | None:
    token = (websocket.query_params.get("token") or "").strip()
    if not token:
        auth_header = (websocket.headers.get("authorization") or "").strip()
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except Exception:
        return None
    sub = str(payload.get("sub") or "").strip()
    role = str(payload.get("role") or "").strip()
    if not sub or not role:
        return None
    return {"sub": sub, "role": role}


async def _reject(websocket: WebSocket, reason: str) -> None:
    if websocket.client_state is WebSocketState.CONNECTING:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=reason)
    else:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket) -> None:
    principal = _principal_from_websocket(websocket)
    if principal is None:
        await _reject(websocket, "Auth token required.")
        return
    await websocket.accept()
    await connection_manager.connect("dashboard", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect("dashboard", websocket)


@router.websocket("/ws/incidents/{incident_id}")
async def websocket_incident(websocket: WebSocket, incident_id: str) -> None:
    principal = _principal_from_websocket(websocket)
    if principal is None:
        await _reject(websocket, "Auth token required.")
        return
    await websocket.accept()
    channel = f"incident:{incident_id}"
    await connection_manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(channel, websocket)


@router.websocket("/ws/organizations/{organization_id}")
async def websocket_organization(websocket: WebSocket, organization_id: str) -> None:
    principal = _principal_from_websocket(websocket)
    if principal is None:
        await _reject(websocket, "Auth token required.")
        return
    if principal["role"] != "organization" or principal["sub"] != str(organization_id):
        await _reject(websocket, "Organization channel denied.")
        return
    await websocket.accept()
    channel = f"organization:{organization_id}"
    await connection_manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(channel, websocket)


@router.websocket("/ws/volunteers/{volunteer_id}")
async def websocket_volunteer(websocket: WebSocket, volunteer_id: str) -> None:
    principal = _principal_from_websocket(websocket)
    if principal is None:
        await _reject(websocket, "Auth token required.")
        return
    if principal["role"] != "volunteer" or principal["sub"] != str(volunteer_id):
        await _reject(websocket, "Volunteer channel denied.")
        return
    await websocket.accept()
    channel = f"volunteer:{volunteer_id}"
    await connection_manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(channel, websocket)
