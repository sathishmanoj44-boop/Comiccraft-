from __future__ import annotations

import re
import textwrap
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from ..config import get_settings

_pipeline = None


def _safe_name(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
    return cleaned[:50] or "panel"


def _placeholder_image(prompt: str, path: Path, panel_number: int) -> None:
    width, height = 768, 768
    image = Image.new("RGB", (width, height), "#f4f0e6")
    draw = ImageDraw.Draw(image)

    draw.rectangle((20, 20, width - 20, height - 20), outline="#202b55", width=8)
    draw.rectangle((45, 45, width - 45, 125), fill="#202b55")
    draw.text((70, 72), f"COMICCRAFT - PANEL {panel_number}", fill="white")

    wrapped = "\n".join(textwrap.wrap(prompt, width=55)[:18])
    draw.text((60, 165), wrapped, fill="#172033", spacing=8)
    draw.rectangle((60, 590, 708, 690), outline="#5b46d6", width=4)
    draw.text((85, 625), "PLACEHOLDER IMAGE - AI ART ENABLED LATER", fill="#5b46d6")
    image.save(path, format="PNG")


def _generate_huggingface(prompt: str, path: Path) -> None:
    from huggingface_hub import InferenceClient

    settings = get_settings()
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is required when IMAGE_PROVIDER=huggingface.")

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
    )

    image = client.text_to_image(
        prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    image.save(path)


def _generate_local(prompt: str, path: Path) -> None:
    global _pipeline

    import torch
    from diffusers import DiffusionPipeline

    settings = get_settings()

    if _pipeline is None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        kwargs = {"torch_dtype": dtype}
        if torch.cuda.is_available():
            kwargs["variant"] = "fp16"
        _pipeline = DiffusionPipeline.from_pretrained(settings.local_image_model, **kwargs)
        if torch.cuda.is_available():
            _pipeline = _pipeline.to("cuda")

    result = _pipeline(
        prompt=prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    result.images[0].save(path)


def generate_image(prompt: str, panel_number: int, filename_hint: Optional[str] = None) -> str:
    settings = get_settings()
    filename = f"{panel_number:02d}_{_safe_name(filename_hint or 'panel')}_{uuid.uuid4().hex[:8]}.png"
    path = settings.panels_dir / filename

    enhanced_prompt = (
        f"{prompt}. Clean comic illustration, consistent character appearance, expressive pose, "
        "clear storytelling composition, detailed environment, cinematic lighting, no words, "
        "no captions, no speech bubbles, no logos, no watermark."
    )

    provider = settings.image_provider.lower().strip()
    if provider == "placeholder":
        _placeholder_image(enhanced_prompt, path, panel_number)
    elif provider == "huggingface":
        _generate_huggingface(enhanced_prompt, path)
    elif provider == "local":
        _generate_local(enhanced_prompt, path)
    else:
        raise ValueError("IMAGE_PROVIDER must be huggingface, local, or placeholder.")

    return f"/static/panels/{filename}"
