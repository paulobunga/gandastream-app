"""Agent 8: Audio Producer (TTS).

Synthesizes all dialogue lines into audio clips.
"""

from interfaces import TTSInterface
from mocks import MockTTS
from models import ProjectState
import logging

logger = logging.getLogger(__name__)


class AudioProducer:
    def __init__(self, tts: TTSInterface | None = None):
        self.tts = tts or MockTTS()

    def run(self, state: ProjectState) -> ProjectState:
        if not state.screenplay or not state.voice_assignments:
            raise ValueError("Missing screenplay/voice_assignments. Run StoryWriter + VoiceDirector first.")
        outputs = []
        for scene in state.screenplay.scenes:
            for line in scene.dialogue:
                assignment = next((a for a in state.voice_assignments if a.character_id == line.character_id), None)
                if assignment is None:
                    continue
                path = self.tts.synthesize(line.text, assignment, f"runs/{state.run_id}/audio")
                outputs.append({
                    "scene_number": scene.scene_number,
                    "character_id": line.character_id,
                    "line_number": line.line_number,
                    "audio_path": path,
                })
        logger.info(f"[AudioProducer] synthesized {len(outputs)} audio lines")
        return state
