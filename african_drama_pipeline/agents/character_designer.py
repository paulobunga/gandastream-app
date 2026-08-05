"""Agent 3b: Character Designer.

Builds persistent character reference sheets from screenplay characters.
"""

from mocks import MockCharacterDesigner
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class CharacterDesigner:
    def __init__(self, designer: MockCharacterDesigner | None = None):
        self.designer = designer or MockCharacterDesigner()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.screenplay:
            raise ValueError("No screenplay in state. Run StoryWriter first.")
        logger.info(f"[CharacterDesigner] ref sheets for {len(state.screenplay.characters)} characters")
        state.character_refs = self.designer.generate_ref_sheets(state.screenplay.characters)
        return state
