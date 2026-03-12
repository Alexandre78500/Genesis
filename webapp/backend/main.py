"""FastAPI app — Autoresearch Lab Monitor."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse, JSONResponse

from .routes import api, git, stream
from .sse import SSEManager
from .watcher import FileWatcher

sse_manager = SSEManager()
file_watcher = FileWatcher(sse_manager)

# Wire SSE manager to stream route
stream.sse_manager = sse_manager

FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "build"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await file_watcher.prime()
    watcher_task = asyncio.create_task(file_watcher.watch_loop())
    heartbeat_task = asyncio.create_task(sse_manager.heartbeat_loop())
    yield
    watcher_task.cancel()
    heartbeat_task.cancel()


app = FastAPI(title="Autoresearch Lab Monitor", lifespan=lifespan)

# No CORS needed — same origin when serving from single server.
# Vite dev proxy handles cross-origin during development.

app.include_router(api.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(git.router, prefix="/api/git")


@app.get("/api/health")
async def health():
    return {"status": "ok", "clients": sse_manager.client_count}


# --- SPA fallback for non-API 404s ---
@app.exception_handler(404)
async def spa_fallback(request: Request, exc: StarletteHTTPException):
    if not request.url.path.startswith("/api") and FRONTEND_BUILD.exists():
        index = FRONTEND_BUILD / "index.html"
        if index.exists():
            return FileResponse(str(index))
    return JSONResponse({"detail": "Not found"}, status_code=404)


# --- Serve built frontend (must be registered last) ---
if FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD), html=True), name="static")
