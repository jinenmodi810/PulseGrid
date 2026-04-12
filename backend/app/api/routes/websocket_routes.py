"""WebSocket channels for live UI updates. TODO(Phase1D+): validate session / role per channel."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.connection_manager import connection_manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket) -> None:
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
