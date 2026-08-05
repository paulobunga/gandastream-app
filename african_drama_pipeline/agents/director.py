"""Agent 2b: Director.

Converts screenplay scenes into an ordered scene breakdown (no LLM needed, it's structural).
"""

from mocks import MockDirector
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class Director:
    def __init__(self, director: MockDirector | None = None):
        self.director = director or MockDirector()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.screenplay:
            raise ValueError("No screenplay in state. Run StoryWriter first.")
        logger.info(f"[Director] breaking screenplay into {len(state.screenplay.scenes)} scenes")
        state.scenes = self.director.break_into_scenes(state.screenplay)
        return state
