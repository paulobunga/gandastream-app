"""Pipeline: wires agents together into a linear runnable pipeline."""

from models import ProjectState
from config import settings
import logging

logger = logging.getLogger(__name__)


STAGE_ORDER = [
    "trends",
    "screenplay",
    "scenes",
    "character_refs",
    "shot_prompts",
    "video_prompts",
    "voice_assignments",
    "clips",
    "video_produced",
    "audio_produced",
    "timeline",
    "posts",
]


class Pipeline:
    def __init__(self):
        from agents.trend_researcher import TrendResearcher
        from agents.story_writer import StoryWriter
        from agents.director import Director
        from agents.character_designer import CharacterDesigner
        from agents.prompt_engineer import PromptEngineer
        from agents.video_director import VideoDirector
        from agents.voice_director import VoiceDirector
        from agents.visual_producer import VisualProducer
        from agents.video_producer import VideoProducer
        from agents.audio_producer import AudioProducer
        from agents.editor import Editor
        from agents.publisher import Publisher

        self.stages = {
            "trends": TrendResearcher(),
            "screenplay": StoryWriter(),
            "scenes": Director(),
            "character_refs": CharacterDesigner(),
            "shot_prompts": PromptEngineer(),
            "video_prompts": VideoDirector(),
            "voice_assignments": VoiceDirector(),
            "clips": VisualProducer(),
            "video_produced": VideoProducer(),
            "audio_produced": AudioProducer(),
            "timeline": Editor(),
            "posts": Publisher(),
        }

    def run_all(self, state: ProjectState) -> ProjectState:
        state.save_stage("_project_state_before", state.get_serializable())
        for name in STAGE_ORDER:
            logger.info(f"=== Running stage: {name} ===")
            state = self.stages[name].run(state)
            state.save_stage(name, state.get_serializable())
        state.save_stage("_project_state_final", state.get_serializable())
        return state

    def run_from(self, state: ProjectState, stage_name: str) -> ProjectState:
        if stage_name not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage_name}. Choose from {STAGE_ORDER}")
        # Load a previous run's final state so upstream outputs are available.
        if state.run_id and (state.get_output_dir() / "_project_state_final.json").exists():
            try:
                loaded = state.load_stage("_project_state_final")
                state = ProjectState(**loaded)
            except Exception:
                state = ProjectState(run_id=state.run_id)
        # Run requested stage and all downstream stages.
        idx = STAGE_ORDER.index(stage_name)
        for name in STAGE_ORDER[idx:]:
            logger.info(f"=== Running stage: {name} ===")
            state = self.stages[name].run(state)
            state.save_stage(name, state.get_serializable())
        state.save_stage("_project_state_final", state.get_serializable())
        return state
