from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = False

    # real = call Gemini; mock = deterministic local demo mode for testing
    gemini_mode: str = "real"
    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.1-pro-preview"

    image_provider: str = "huggingface"  # huggingface | local | placeholder
    hf_token: str = ""
    hf_provider: str = "auto"
    hf_image_model: str = "runwayml/stable-diffusion-v1-5"

    local_image_model: str = "runwayml/stable-diffusion-v1-5"
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 20
    image_guidance: float = 7.5

    max_panels: int = 5
    output_dir: str = "static"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / self.output_dir

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return settings
