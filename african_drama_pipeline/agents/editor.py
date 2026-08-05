"""Agent 9: Editor.

Builds a timeline/EDL and SRT subtitles from produced clips.
"""

from models import ProjectState, TimelineClip, SubtitleSegment
from config import settings
import logging

logger = logging.getLogger(__name__)


class Editor:
    def run(self, state: ProjectState) -> ProjectState:
        if not state.video_prompts or not state.clips:
            raise ValueError("No clips/video_prompts in state. Run VideoProducer first.")
        timeline = []
        order = 0
        current_time = 0.0
        subtitles: list[SubtitleSegment] = []
        vp_map = {(v.scene_number, v.shot_number): v for v in state.video_prompts}
        for clip in state.clips:
            key = (clip.scene_number, clip.shot_number)
            vp = vp_map.get(key)
            duration = vp.duration_seconds if vp else 5.0
            order += 1
            timeline.append(TimelineClip(
                clip_id=f"clip_{order:03d}",
                order=order,
                scene_number=clip.scene_number,
                shot_number=clip.shot_number,
                clip_path=clip.generated_video_path,
                duration_seconds=duration,
                transition_in=vp.transition_in if vp else "cut",
                transition_out=vp.transition_out if vp else "cut",
            ))
            # Simple subtitle from screenplay dialogue
            if state.screenplay:
                scene = next((s for s in state.screenplay.scenes if s.scene_number == clip.scene_number), None)
                if scene and scene.dialogue:
                    line = scene.dialogue[0]
                    subtitles.append(SubtitleSegment(
                        start_time=current_time,
                        end_time=current_time + duration,
                        text=f"{line.character_name}: {line.text}",
                        language=state.language,
                    ))
            current_time += duration
        state.timeline = timeline
        state.subtitles = subtitles
        logger.info(f"[Editor] timeline={len(timeline)} clips, subtitles={len(subtitles)}")
        return state
