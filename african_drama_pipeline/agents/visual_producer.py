"""Agent 6: Visual Producer (image gen).

Converts shot prompts into generated image paths using the image generation interface.
"""

from interfaces import ImageGenerationInterface
from mocks import MockImageGenerator
from models import ProjectState, Clip
import logging

logger = logging.getLogger(__name__)


class VisualProducer:
    def __init__(self, image_gen: ImageGenerationInterface | None = None):
        self.image_gen = image_gen or MockImageGenerator()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.shot_prompts:
            raise ValueError("No shot_prompts in state. Run PromptEngineer first.")
        clips = []
        for sp in state.shot_prompts:
            path = self.image_gen.generate_scene_image(sp.prompt, sp.style_guide, seed=sp.shot_number)
            clips.append(Clip(
                scene_number=sp.scene_number,
                shot_number=sp.shot_number,
                source_image_path=path,
            ))
        state.clips = clips
        logger.info(f"[VisualProducer] generated {len(clips)} images")
        return state
