from __future__ import annotations

import re
import uuid
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from ..config import get_settings


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return cleaned[:50] or "comic"


def _local_static_path(web_path: str) -> Path:
    settings = get_settings()
    prefix = "/static/"
    if not web_path.startswith(prefix):
        raise ValueError("Unsupported image path.")

    relative = Path(web_path[len(prefix):])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Invalid image path.")

    target = (settings.static_dir / relative).resolve()
    static_root = settings.static_dir.resolve()
    target.relative_to(static_root)
    return target


def _pdf_text(value: str) -> str:
    return (
        str(value)
        .replace("—", "-")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def save_pdf(layout: list[dict], title: str = "ComicCraft Comic") -> str:
    settings = get_settings()
    filename = f"{_safe_name(title)}_{uuid.uuid4().hex[:8]}.pdf"
    output = settings.exports_dir / filename

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=False)

    page_width = 210
    page_height = 297
    margin = 12
    content_width = page_width - (2 * margin)

    for panel in layout:
        pdf.add_page()
        pdf.set_xy(margin, 10)
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(
            content_width,
            8,
            _pdf_text(f"Panel {panel['panel_number']}: {panel['title']}"),
        )

        image_path = _local_static_path(panel["image_path"])
        if not image_path.exists():
            raise FileNotFoundError(f"Panel image not found: {image_path}")

        with Image.open(image_path) as img:
            image_width, image_height = img.size

        max_width = content_width
        max_height = 110
        scale = min(max_width / image_width, max_height / image_height)
        display_width = image_width * scale
        display_height = image_height * scale
        image_x = (page_width - display_width) / 2

        pdf.image(
            str(image_path),
            x=image_x,
            y=30,
            w=display_width,
            h=display_height,
        )

        y = 30 + display_height + 7
        pdf.set_xy(margin, y)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(content_width, 5, _pdf_text(panel["scene_description"]))

        pdf.set_xy(margin, pdf.get_y() + 2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(content_width, 5, _pdf_text(f"Caption: {panel['caption']}"))

        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(content_width, 5, _pdf_text(f"Narration: {panel['narration']}"))

        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(content_width, 5, _pdf_text(f"Dialogue: {panel['dialogue']}"))

        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(margin, page_height - 10)
        pdf.cell(content_width, 5, "Created with ComicCraft", align="C")

    pdf.output(str(output))
    return f"/static/exports/{filename}"
