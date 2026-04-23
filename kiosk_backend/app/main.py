from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

import app.api.routes.state as state
import app.api.routes.session as session
import app.api.routes.greeting as greeting
import app.api.routes.listening as listening
import app.api.routes.chat as chat

from app.services.camera_detection_service import camera_detection_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] FastAPI startup")
    camera_detection_service.start()
    yield
    print("[INFO] FastAPI shutdown")
    camera_detection_service.stop()


app = FastAPI(title="AI Kiosk Backend", lifespan=lifespan)

app.include_router(state.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(greeting.router, prefix="/api")
app.include_router(listening.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/ui")
def ui():
    return FileResponse(Path("app/test_ui/index.html"))
