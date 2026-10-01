from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import BASE_DIR, get_settings
from .schemas import PromptRequest
from .services.exporters import save_pdf
from .services.gemini_flash import generate_outline
from .services.gemini_pro import generate_story
from .services.image_generator import generate_image
from .services.layout_builder import build_comic_layout

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"settings": settings},
    )


def _run_pipeline(payload: PromptRequest) -> tuple[list[dict], str]:
    outline = generate_outline(payload)
    story = generate_story(payload, outline)

    image_paths = [
        generate_image(
            panel.image_prompt,
            panel.panel_number,
            panel.title,
        )
        for panel in story.panels
    ]

    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout, title=payload.character_name)
    return layout, pdf_path


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout, pdf_path = _run_pipeline(payload)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": pdf_path,
                "input": payload.model_dump(),
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_comic_json(payload: PromptRequest):
    try:
        layout, pdf_path = _run_pipeline(payload)
        return {
            "success": True,
            "message": "Comic generated successfully.",
            "layout": layout,
            "pdf_path": pdf_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/download/{filename}")
def download_pdf(filename: str):
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid PDF filename.")

    path = settings.exports_dir / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="PDF file not found.")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=path.name,
    )


@router.get("/test-image")
def test_image(
    prompt: str = "A heroic fox exploring an enchanted forest, comic illustration",
):
    try:
        image_path = generate_image(prompt, 0, "test")
        return {"success": True, "image_path": image_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
