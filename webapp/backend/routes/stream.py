"""SSE streaming endpoint."""

from fastapi import APIRouter

from ..data import get_snapshot
from ..sse import SSEManager

router = APIRouter()

# Will be set by main.py
sse_manager: SSEManager | None = None


@router.get("/stream")
async def stream():
    import json

    response, queue = await sse_manager.connect()

    # Queue initial snapshot directly to this client's queue
    snapshot = get_snapshot()
    snapshot_payload = json.dumps(snapshot, default=str)
    queue.put_nowait(f"event: snapshot\ndata: {snapshot_payload}\n\n")

    return response
