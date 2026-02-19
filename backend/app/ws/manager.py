import asyncio
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages all active WebSocket client connections.
    Thread-safe for asyncio — all operations run in the same event loop.
    """

    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info(f"WS client connected. Total: {len(self._connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)
        logger.info(f"WS client disconnected. Total: {len(self._connections)}")

    async def broadcast(self, data: dict) -> None:
        """Send JSON data to all connected clients. Remove stale connections."""
        if not self._connections:
            return

        message = json.dumps(data, default=str)
        stale: set[WebSocket] = set()

        async with self._lock:
            connections_snapshot = set(self._connections)

        for ws in connections_snapshot:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to WS client: {e}")
                stale.add(ws)

        if stale:
            async with self._lock:
                self._connections -= stale

    async def send_to(self, websocket: WebSocket, data: dict) -> None:
        """Send data to a specific client."""
        try:
            await websocket.send_text(json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"Failed to send to specific WS client: {e}")
            await self.disconnect(websocket)

    def connection_count(self) -> int:
        return len(self._connections)
