from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routes import router

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate a personalized five-panel comic from a story prompt.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)

app.include_router(router)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "ComicCraft",
        "gemini_mode": settings.gemini_mode,
        "image_provider": settings.image_provider,
    }
