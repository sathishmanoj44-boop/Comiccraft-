from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=5, max_length=2000)
    character_name: str = Field(..., min_length=1, max_length=80)
    setting: str = Field(..., min_length=1, max_length=120)
    tone: str = Field(..., min_length=1, max_length=60)
    art_style: str = Field(..., min_length=1, max_length=80)

    @field_validator("*")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty.")
        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicStory(BaseModel):
    panels: List[PanelStory]
