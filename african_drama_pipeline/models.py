from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
from pathlib import Path
from config import settings


class Character(BaseModel):
    id: str
    name: str
    description: str
    appearance: Optional[dict] = None
    wardrobe: Optional[dict] = None
    voice_accent: str = "Nigerian"


class DialogueLine(BaseModel):
    character_id: str
    character_name: str
    text: str
    emotion: str
    line_number: int


class Scene(BaseModel):
    scene_number: int
    setting: str
    characters_present: list[str]
    action_summary: str
    dialogue: list[DialogueLine]
    estimated_duration_seconds: float
    image_prompts: Optional[list[str]] = None
    video_prompts: Optional[list[dict]] = None
    voice_assignments: Optional[dict] = None


class TrendSignal(BaseModel):
    rank: int
    hook: str
    target_emotion: str
    source_platform: str
    source_signal: str
    region: str
    genre: str


class Screenplay(BaseModel):
    title: str
    logline: str
    characters: list[Character]
    episodes: list[dict] = Field(default_factory=list)
    episode_count: int = 60
    total_estimated_duration: float


class CharacterRefSheet(BaseModel):
    character_id: str
    name: str
    appearance: dict
    wardrobe: dict
    distinguishing_features: list[str]
    reference_prompt_suffix: str


class StyleGuide(BaseModel):
    lighting: str
    color_palette: str
    aspect_ratio: str
    style_summary: str
    negative_prompt: str


class ShotPrompt(BaseModel):
    scene_number: int
    shot_number: int
    prompt: str
    style_guide: StyleGuide
    character_refs: list[CharacterRefSheet]


class VideoPrompt(BaseModel):
    scene_number: int
    shot_number: int
    camera_movement: str
    motion_intensity: str
    transition_in: str
    transition_out: str
    duration_seconds: float


class VoiceAssignment(BaseModel):
    character_id: str
    character_name: str
    emotion: str
    pacing: str
    tts_provider_hint: str


class Clip(BaseModel):
    scene_number: int
    shot_number: int
    source_image_path: Optional[str] = None
    generated_video_path: Optional[str] = None
    duration_seconds: Optional[float] = None


class TimelineClip(BaseModel):
    clip_id: str
    order: int
    scene_number: int
    shot_number: int
    clip_path: Optional[str] = None
    duration_seconds: float
    transition_in: str
    transition_out: str


class SubtitleSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    language: str


class PostMetadata(BaseModel):
    platform: str
    caption: str
    hashtags: list[str]
    thumbnail_path: Optional[str] = None


class ProjectState(BaseModel):
    run_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4())[:8])
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    region: str = "Nigeria"
    genre: str = "family_drama"
    accent: str = "Nigerian"
    language: str = "en"

    trends: list[TrendSignal] = Field(default_factory=list)
    chosen_trend: Optional[TrendSignal] = None
    screenplay: Optional[Screenplay] = None
    scenes: list[Scene] = Field(default_factory=list)
    style_guide: Optional[StyleGuide] = None
    shot_prompts: list[ShotPrompt] = Field(default_factory=list)
    character_refs: list[CharacterRefSheet] = Field(default_factory=list)
    video_prompts: list[VideoPrompt] = Field(default_factory=list)
    voice_assignments: list[VoiceAssignment] = Field(default_factory=list)
    clips: list[Clip] = Field(default_factory=list)
    timeline: list[TimelineClip] = Field(default_factory=list)
    subtitles: list[SubtitleSegment] = Field(default_factory=list)
    posts: list[PostMetadata] = Field(default_factory=list)

    def get_output_dir(self) -> Path:
        return Path(settings.run_output_dir) / self.run_id

    def save_stage(self, stage_name: str, data: Any) -> Path:
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{stage_name}.json"
        if isinstance(data, BaseModel):
            path.write_text(data.model_dump_json(indent=2))
        elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
            path.write_text(json.dumps([item.model_dump() for item in data], indent=2))
        else:
            path.write_text(json.dumps(data, indent=2) if not isinstance(data, str) else data)
        return path

    def load_stage(self, stage_name: str) -> Any:
        path = self.get_output_dir() / f"{stage_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Stage file not found: {path}")
        return json.loads(path.read_text())

    def get_serializable(self) -> dict:
        return self.model_dump(mode="json")
