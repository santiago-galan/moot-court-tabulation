import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._active.append(ws)

    def disconnect(self, ws: WebSocket):
        self._active.remove(ws)

    async def broadcast(self, event: str, data: dict):
        payload = json.dumps({"event": event, "data": data})
        for ws in list(self._active):
            try:
                await ws.send_text(payload)
            except Exception:
                self._active.remove(ws)


manager = ConnectionManager()
