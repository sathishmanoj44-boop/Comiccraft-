from ..config import get_settings
from ..schemas import ComicOutline, PanelOutline, PromptRequest


def _get_client():
    from google import genai

    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    return genai.Client(api_key=settings.gemini_api_key)


def _mock_outline(request: PromptRequest) -> ComicOutline:
    character = request.character_name
    setting = request.setting
    tone = request.tone
    style = request.art_style

    panels = [
        ("The Idea", f"{character} arrives in {setting} and notices something unusual.", f"{character} in {setting}, discovering a mysterious clue, {style} comic illustration"),
        ("The Discovery", f"{character} follows the clue deeper into {setting} and finds a surprising secret.", f"{character} investigating a hidden secret in {setting}, expressive pose, detailed environment, {style} art"),
        ("The Challenge", f"A problem appears and {character} must make a brave decision.", f"{character} facing a dramatic challenge in {setting}, cinematic composition, action pose, {style} comic art"),
        ("The Turning Point", f"{character} uses creativity and courage to overcome the main obstacle.", f"{character} overcoming the obstacle in {setting}, dynamic action scene, dramatic lighting, {style} illustration"),
        ("The Ending", f"The adventure ends with {character} changed by what happened and a hopeful final moment.", f"{character} celebrating a hopeful ending in {setting}, warm atmosphere, cinematic final panel, {style} comic illustration"),
    ]
    return ComicOutline(
        panels=[
            PanelOutline(
                panel_number=i,
                title=title,
                scene_description=scene,
                image_prompt=prompt,
            )
            for i, (title, scene, prompt) in enumerate(panels, start=1)
        ]
    )


def generate_outline(request: PromptRequest) -> ComicOutline:
    settings = get_settings()
    if settings.gemini_mode.lower() == "mock":
        return _mock_outline(request)

    client = _get_client()
    from google.genai import types

    prompt = f"""
You are ComicCraft's outline writer.
Create exactly five coherent comic panels from the user's idea.

Story prompt: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Requirements:
- Exactly 5 panels with panel numbers 1 through 5.
- Create a clear beginning, development, challenge, turning point, and ending.
- Keep character and environment continuity.
- Each panel needs a short scene description.
- Each image prompt must be visual and concrete.
- Do not put dialogue, words, captions, speech bubbles, logos, or watermarks in image prompts.
- Return only JSON matching the provided schema.
"""

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=2500,
            response_mime_type="application/json",
            response_schema=ComicOutline,
        ),
    )

    if getattr(response, "parsed", None) is not None:
        outline = response.parsed
    elif getattr(response, "text", None):
        outline = ComicOutline.model_validate_json(response.text)
    else:
        raise RuntimeError("Gemini returned an empty outline.")

    if len(outline.panels) != settings.max_panels:
        raise RuntimeError(f"Expected {settings.max_panels} panels, got {len(outline.panels)}.")
    return outline
