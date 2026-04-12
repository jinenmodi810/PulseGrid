"""Track WebSocket clients per logical channel (dashboard, incident, volunteer, organization)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.websockets import WebSocket


class ConnectionManager:
    """In-memory fan-out. TODO(Phase1D+): auth per channel, Redis adapter for multi-worker."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._channels: dict[str, set[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._channels.setdefault(channel, set()).add(websocket)

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(websocket)

    async def broadcast_json(self, channel: str, payload: dict[str, Any]) -> None:
        text = json.dumps(payload, default=str)
        async with self._lock:
            clients = list(self._channels.get(channel, set()))
        dead: list[tuple[str, WebSocket]] = []
        for ws in clients:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append((channel, ws))
        if dead:
            async with self._lock:
                for ch, ws in dead:
                    self._channels.get(ch, set()).discard(ws)


connection_manager = ConnectionManager()
