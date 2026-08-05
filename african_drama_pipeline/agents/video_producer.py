"""Agent 7: Video Producer.

Animates generated images using the video generation interface.
"""

from interfaces import VideoGenerationInterface
from mocks import MockVideoGenerator
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class VideoProducer:
    def __init__(self, video_gen: VideoGenerationInterface | None = None):
        self.video_gen = video_gen or MockVideoGenerator()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.video_prompts or not state.clips:
            raise ValueError("No video_prompts/clips in state. Run VideoDirector + VisualProducer first.")
        vp_map = {(v.scene_number, v.shot_number): v for v in state.video_prompts}
        produced = 0
        for clip in state.clips:
            key = (clip.scene_number, clip.shot_number)
            vp = vp_map.get(key)
            if vp is None:
                continue
            path = self.video_gen.generate_shot_video(clip.source_image_path or "", vp)
            clip.generated_video_path = path
            produced += 1
        logger.info(f"[VideoProducer] produced {produced} video clips")
        return state
