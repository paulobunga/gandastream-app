"""Agent 2: Story Writer.

Generates a full screenplay from the chosen trend premise.
"""

from interfaces import LLMInterface
from mocks import MockLLMStoryWriter
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class StoryWriter:
    def __init__(self, llm: LLMInterface | None = None):
        self.llm = llm or MockLLMStoryWriter()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.chosen_trend:
            raise ValueError("No chosen_trend in state. Run TrendResearcher first.")
        logger.info(f"[StoryWriter] writing screenplay from: {state.chosen_trend.hook}")
        screenplay = self.llm.generate_screenplay(state.chosen_trend)
        state.screenplay = screenplay
        logger.info(f"[StoryWriter] created '{screenplay.title}' with {len(screenplay.scenes)} scenes")
        return state
