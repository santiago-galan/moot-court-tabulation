from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from server.config import BASE_DIR, settings
from server.database import Base, engine
from server.net import get_lan_ip
from server.ws.manager import manager

CLIENT_DIST = BASE_DIR / "client" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(StarletteHTTPException)
async def _spa_or_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and not request.url.path.startswith("/api"):
        index = CLIENT_DIST / "index.html"
        if index.is_file():
            return FileResponse(str(index))
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "lan_ip": get_lan_ip(),
        "port": settings.port,
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


from server.api import (  # noqa: E402
    brackets,
    judge_portal,
    network,
    reports,
    rounds,
    rulesets,
    scoring,
    teams,
    tournaments,
)

app.include_router(rulesets.router, prefix="/api")
app.include_router(tournaments.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(rounds.router, prefix="/api")
app.include_router(scoring.router, prefix="/api")
app.include_router(brackets.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(judge_portal.router, prefix="/api")
app.include_router(network.router, prefix="/api")

if CLIENT_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(CLIENT_DIST / "assets")), name="static_assets")
