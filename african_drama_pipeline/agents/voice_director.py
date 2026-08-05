"""Agent 5: Voice Director.

Assigns voices, emotions, and pacing to each character's dialogue lines.
"""

from mocks import MockVoiceDirector
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class VoiceDirector:
    def __init__(self, director: MockVoiceDirector | None = None):
        self.director = director or MockVoiceDirector()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.screenplay:
            raise ValueError("No screenplay in state. Run StoryWriter first.")
        logger.info(f"[VoiceDirector] assigning voices, accent={state.accent}")
        state.voice_assignments = self.director.assign_voices(
            state.screenplay.scenes, state.screenplay.characters, state.accent
        )
        return state
