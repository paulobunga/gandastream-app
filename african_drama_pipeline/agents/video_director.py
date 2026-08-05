"""Agent 4: Video Director.

Generates camera motion / animation prompts per shot.
"""

from mocks import MockVideoDirector
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class VideoDirector:
    def __init__(self, director: MockVideoDirector | None = None):
        self.director = director or MockVideoDirector()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.scenes:
            raise ValueError("No scenes in state. Run Director first.")
        logger.info(f"[VideoDirector] video prompts for {len(state.scenes)} scenes")
        state.video_prompts = self.director.generate_video_prompts(state.scenes)
        return state
