from ..config import get_settings
from ..schemas import ComicOutline, ComicStory, PanelStory, PromptRequest


def _get_client():
    from google import genai

    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    return genai.Client(api_key=settings.gemini_api_key)


def _mock_story(request: PromptRequest, outline: ComicOutline) -> ComicStory:
    panels = []
    for panel in outline.panels:
        number = panel.panel_number
        panels.append(
            PanelStory(
                panel_number=number,
                title=panel.title,
                scene_description=panel.scene_description,
                caption=f"Panel {number}: {panel.title}",
                narration=f"{request.character_name} moves forward, guided by curiosity and courage.",
                dialogue=(
                    "Something is waiting for me here!"
                    if number == 1
                    else "I have to keep going."
                    if number < 5
                    else "I will never forget this adventure!"
                ),
                image_prompt=panel.image_prompt,
            )
        )
    return ComicStory(panels=panels)


def generate_story(request: PromptRequest, outline: ComicOutline) -> ComicStory:
    settings = get_settings()
    if settings.gemini_mode.lower() == "mock":
        return _mock_story(request, outline)

    client = _get_client()
    from google.genai import types

    prompt = f"""
You are ComicCraft's professional comic script writer.
Expand the supplied five-panel outline into a polished comic script.

Original story: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline.model_dump_json(indent=2)}

Requirements:
- Exactly five panels, preserving panel order.
- Maintain character, location, and event continuity.
- For every panel provide title, scene description, caption, narration, dialogue, and image prompt.
- Keep narration concise enough for a comic page.
- Make dialogue natural and suited to the requested tone.
- Image prompts should describe character action, environment, composition, lighting, and art style.
- Do not include readable text, captions, speech bubbles, logos, or watermarks in image prompts.
- Return only JSON matching the supplied schema.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=5000,
            response_mime_type="application/json",
            response_schema=ComicStory,
        ),
    )

    if getattr(response, "parsed", None) is not None:
        story = response.parsed
    elif getattr(response, "text", None):
        story = ComicStory.model_validate_json(response.text)
    else:
        raise RuntimeError("Gemini returned an empty story.")

    if len(story.panels) != settings.max_panels:
        raise RuntimeError(f"Expected {settings.max_panels} panels, got {len(story.panels)}.")
    return story
