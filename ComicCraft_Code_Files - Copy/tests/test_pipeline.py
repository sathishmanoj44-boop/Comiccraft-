from pathlib import Path

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def test_complete_mock_pipeline(monkeypatch):
    monkeypatch.setenv("GEMINI_MODE", "mock")
    monkeypatch.setenv("IMAGE_PROVIDER", "placeholder")
    get_settings.cache_clear()

    request = PromptRequest(
        story_prompt="A young fox discovers a glowing portal in an enchanted forest.",
        character_name="Rin",
        setting="Enchanted Forest",
        tone="Adventurous",
        art_style="Comic Book",
    )

    outline = generate_outline(request)
    assert len(outline.panels) == 5

    story = generate_story(request, outline)
    assert len(story.panels) == 5

    image_paths = [
        generate_image(p.image_prompt, p.panel_number, p.title)
        for p in story.panels
    ]
    assert len(image_paths) == 5

    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout, "Rin")

    settings = get_settings()
    pdf_file = settings.static_dir / pdf_path.removeprefix("/static/")
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1000

    for path in image_paths:
        image_file = settings.static_dir / path.removeprefix("/static/")
        assert Path(image_file).exists()
