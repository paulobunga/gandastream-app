"""Agent 3: Prompt Engineer.

Generates image-generation prompts for each scene/shot plus a consistent style guide.
"""

from mocks import MockPromptEngineer
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class PromptEngineer:
    def __init__(self, engineer: MockPromptEngineer | None = None):
        self.engineer = engineer or MockPromptEngineer()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.scenes:
            raise ValueError("No scenes in state. Run Director first.")
        logger.info(f"[PromptEngineer] generating shot prompts for {len(state.scenes)} scenes")
        state.shot_prompts = self.engineer.generate_prompts(state.scenes, state.character_refs)
        state.style_guide = self.engineer.style_guide
        return state
