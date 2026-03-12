"""FastAPI app — Autoresearch Lab Monitor."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import api, git, stream
from .sse import SSEManager
from .watcher import FileWatcher

sse_manager = SSEManager()
file_watcher = FileWatcher(sse_manager)

# Wire SSE manager to stream route
stream.sse_manager = sse_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    watcher_task = asyncio.create_task(file_watcher.watch_loop())
    heartbeat_task = asyncio.create_task(sse_manager.heartbeat_loop())
    yield
    watcher_task.cancel()
    heartbeat_task.cancel()


app = FastAPI(title="Autoresearch Lab Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(git.router, prefix="/api/git")


@app.get("/api/health")
async def health():
    return {"status": "ok", "clients": sse_manager.client_count}
