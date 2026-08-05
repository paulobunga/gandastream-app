from abc import ABC, abstractmethod
from typing import Any
from models import (
    TrendSignal,
    Screenplay,
    Scene,
    StyleGuide,
    ShotPrompt,
    CharacterRefSheet,
    VideoPrompt,
    VoiceAssignment,
    Clip,
    TimelineClip,
    SubtitleSegment,
    PostMetadata,
)


class TrendResearchInterface(ABC):
    @abstractmethod
    def get_trending_premises(self, region: str, genre: str, limit: int = 10) -> list[TrendSignal]:
        ...


class LLMInterface(ABC):
    @abstractmethod
    def generate_screenplay(self, premise: TrendSignal, duration_seconds: int = 90) -> Screenplay:
        ...


class ImageGenerationInterface(ABC):
    @abstractmethod
    def generate_scene_image(self, prompt: str, style_guide: StyleGuide, seed: int | None = None) -> str:
        """Returns path to generated image."""
        ...


class VideoGenerationInterface(ABC):
    @abstractmethod
    def generate_shot_video(self, image_path: str, video_prompt: VideoPrompt) -> str:
        """Returns path to generated video clip."""
        ...


class TTSInterface(ABC):
    @abstractmethod
    def synthesize(self, text: str, character: VoiceAssignment, output_path: str) -> str:
        """Returns path to generated audio file."""
        ...


class PlatformPublisherInterface(ABC):
    @abstractmethod
    def upload_video(self, platform: str, video_path: str, metadata: PostMetadata) -> str:
        """Returns the published URL or post ID."""
        ...
