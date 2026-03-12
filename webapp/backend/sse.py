"""SSE manager — client registry, broadcast, heartbeat."""

import asyncio
import json
import time

from starlette.responses import StreamingResponse

from .config import HEARTBEAT_INTERVAL_S, SSE_RETRY_MS


class SSEManager:
    def __init__(self):
        self._clients: set[asyncio.Queue] = set()

    async def connect(self) -> StreamingResponse:
        queue: asyncio.Queue = asyncio.Queue()
        self._clients.add(queue)

        async def event_stream():
            try:
                # Send retry directive
                yield f"retry: {SSE_RETRY_MS}\n\n"
                while True:
                    data = await queue.get()
                    yield data
            except asyncio.CancelledError:
                pass
            finally:
                self._clients.discard(queue)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def broadcast(self, event: str, data: dict | list):
        payload = json.dumps(data, default=str)
        message = f"event: {event}\ndata: {payload}\n\n"
        dead = set()
        for queue in self._clients:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                dead.add(queue)
        self._clients -= dead

    async def heartbeat_loop(self):
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL_S)
            await self.broadcast("heartbeat", {"server_time": time.time()})

    @property
    def client_count(self) -> int:
        return len(self._clients)
