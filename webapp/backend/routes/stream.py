"""SSE streaming endpoint."""

from fastapi import APIRouter

from ..data import get_snapshot
from ..sse import SSEManager

router = APIRouter()

# Will be set by main.py
sse_manager: SSEManager | None = None


@router.get("/stream")
async def stream():
    response = await sse_manager.connect()

    # Queue initial snapshot for this client
    snapshot = get_snapshot()
    # The snapshot is sent as the first event via the SSE manager
    # We broadcast it only to the newest client by sending directly
    import json
    snapshot_payload = json.dumps(snapshot, default=str)
    # Get the last queue added (the one we just created)
    if sse_manager._clients:
        newest = max(sse_manager._clients, key=id)
        newest.put_nowait(f"event: snapshot\ndata: {snapshot_payload}\n\n")

    return response
