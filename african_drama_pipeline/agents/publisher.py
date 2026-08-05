"""Agent 10: Publisher.

Formats final metadata for each target platform and mocks upload.
"""

from interfaces import PlatformPublisherInterface
from mocks import MockPlatformPublisher
from integrations.omni_route import TikTokPublisher, OmniRouteClient
from models import ProjectState, PostMetadata
from config import settings
import logging

logger = logging.getLogger(__name__)


def _get_publisher(platform: str) -> PlatformPublisherInterface:
    if platform.lower() == "tiktok":
        return TikTokPublisher(client=OmniRouteClient())
    return MockPlatformPublisher()


class Publisher:
    def __init__(self, uploader: PlatformPublisherInterface | None = None):
        self.uploader = uploader

    def run(self, state: ProjectState) -> ProjectState:
        if not state.screenplay:
            raise ValueError("No screenplay in state. Run StoryWriter first.")
        results: list[PostMetadata] = []
        caption = (
            f"{state.screenplay.title}\n\n{state.screenplay.logline}\n\n"
            f"#AfricanDrama #ShortFilm #{state.genre.replace('_', '')} #{state.region}"
        )
        for key, platform_cfg in settings.platforms.items():
            hashtags = [f"#{state.region}Drama", f"#{state.genre}", "#ShortDrama", "#AfricanStories"]
            post = PostMetadata(
                platform=key,
                caption=caption[:platform_cfg.max_caption_chars],
                hashtags=hashtags[: platform_cfg.max_hashtags],
            )
            uploader = self.uploader or _get_publisher(key)
            uploader.upload_video(key, "mock_video.mp4", post)
            results.append(post)
        state.posts = results
        logger.info(f"[Publisher] formatted posts for {len(results)} platforms")
        return state
