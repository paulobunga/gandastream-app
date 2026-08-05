from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(".env", override=False)
    load_dotenv(".env.example", override=False)
except Exception:
    pass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


class VideoSpec(BaseModel):
    width: int = int(_env("VIDEO_WIDTH", "1080"))
    height: int = int(_env("VIDEO_HEIGHT", "1920"))
    fps: int = int(_env("VIDEO_FPS", "30"))
    aspect_ratio: str = _env("VIDEO_ASPECT_RATIO", "9:16")
    target_duration_seconds: tuple[int, int] = (60, 120)
    preferred_duration: int = 90
    episode_count: int = int(_env("EPISODE_COUNT", "60"))


class PlatformConfig(BaseModel):
    name: str
    max_caption_chars: int
    max_hashtags: int
    supported_accent: str
    aspect_ratio: str


class OmniRouteSettings(BaseModel):
    base_url: str = _env("OMNIROUTE_BASE_URL", "")
    auth_token: str = _env("OMNIROUTE_AUTH_TOKEN", "")
    model: str = _env("OMNIROUTE_MODEL", "auto")


class Settings(BaseSettings):
    project_name: str = "gandastream"
    environment: Literal["development", "production"] = _env("ENVIRONMENT", "development")
    database_url: str = _env("DATABASE_URL", "sqlite:///./afridrama.db")
    storage_dir: str = _env("STORAGE_DIR", "storage")
    default_region: str = _env("DEFAULT_REGION", "Uganda")
    default_genre: str = _env("DEFAULT_GENRE", "family_drama")
    language: str = _env("LANGUAGE", "en")
    accent: str = _env("ACCENT", "Ugandan")
    video_spec: VideoSpec = VideoSpec()
    platforms: dict[str, PlatformConfig] = {
        "tiktok": PlatformConfig(
            name="TikTok",
            max_caption_chars=2200,
            max_hashtags=10,
            supported_accent="Ugandan",
            aspect_ratio="9:16",
        ),
        "youtube": PlatformConfig(
            name="YouTube Shorts",
            max_caption_chars=5000,
            max_hashtags=15,
            supported_accent="Ugandan",
            aspect_ratio="9:16",
        ),
        "instagram": PlatformConfig(
            name="Instagram Reels",
            max_caption_chars=2200,
            max_hashtags=30,
            supported_accent="Ugandan",
            aspect_ratio="9:16",
        ),
    }
    omni_route: OmniRouteSettings = OmniRouteSettings()
    tiktok_cookies_path: str = _env("TIKTOK_COOKIES_PATH", "storage/cookies/tiktok_cookies.json")
    run_output_dir: str = _env("RUN_OUTPUT_DIR", "runs")
    log_level: str = _env("LOG_LEVEL", "INFO")
    secret_key: str = _env("SECRET_KEY", "change-me-in-production")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
