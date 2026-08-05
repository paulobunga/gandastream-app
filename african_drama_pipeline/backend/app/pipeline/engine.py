from sqlalchemy.orm import Session
from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import config
from backend.app.models.models import Run, Stage, RunStatus, StageStatus
from models import (
    TrendSignal, Screenplay, Scene, DialogueLine, Character, StyleGuide, ShotPrompt,
    CharacterRefSheet, VideoPrompt, VoiceAssignment, Clip, TimelineClip, SubtitleSegment
)
import uuid
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class OmniRouteClient:
    """Unified AI/service client through OmniRoute."""

    def __init__(self):
        if not config.settings.omni_route.base_url or not config.settings.omni_route.auth_token:
            raise RuntimeError(
                "OmniRoute is required. Set OMNIROUTE_BASE_URL and OMNIROUTE_AUTH_TOKEN in .env"
            )
        self.base_url = config.settings.omni_route.base_url.rstrip("/")
        self.auth_token = config.settings.omni_route.auth_token
        self.model = config.settings.omni_route.model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _post(self, path: str, payload: dict) -> Any:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                json={**payload, "model": self.model},
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_completion(self, messages: list[dict], response_format: dict | None = None) -> str:
        payload = {"messages": messages}
        if response_format:
            payload["response_format"] = response_format
        data = await self._post("/v1/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_image(self, prompt: str, output_path: str) -> str:
        data = await self._post("/v1/images/generations", {"prompt": prompt, "n": 1, "size": "1024x1792"})
        url = data["data"][0]["url"]
        async with httpx.AsyncClient(timeout=120.0) as client:
            img = await client.get(url)
            img.raise_for_status()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_bytes(img.content)
        return output_path

    async def generate_video(self, image_path: str, prompt: str, output_path: str) -> str:
        data = await self._post("/v1/videos/generations", {"image_path": image_path, "prompt": prompt})
        job_id = data.get("id") or data.get("job_id")
        if not job_id:
            raise RuntimeError(f"Video generation did not return a job id: {data}")
        import asyncio
        for _ in range(60):
            await asyncio.sleep(3)
            async with httpx.AsyncClient(timeout=30.0) as client:
                poll = await client.get(
                    f"{self.base_url}/v1/videos/generations/{job_id}",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                )
                poll.raise_for_status()
                job = poll.json()
                if job.get("status") == "succeeded":
                    url = job.get("output") or job.get("video_url")
                    if not url:
                        raise RuntimeError(f"Video job succeeded without output: {job}")
                    vid = await client.get(url)
                    vid.raise_for_status()
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    Path(output_path).write_bytes(vid.content)
                    return output_path
        raise RuntimeError("Video generation timed out")

    async def synthesize_speech(self, text: str, output_path: str, voice: str = "default") -> str:
        data = await self._post("/v1/audio/speech", {"text": text, "voice": voice})
        url = data.get("url") or data.get("audio_url")
        if not url:
            raise RuntimeError(f"TTS response missing audio url: {data}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            audio = await client.get(url)
            audio.raise_for_status()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_bytes(audio.content)
        return output_path

    async def get_trending(self, region: str, genre: str, limit: int = 10) -> list[dict]:
        data = await self._post("/v1/trends", {"region": region, "genre": genre, "limit": limit})
        trends = data.get("trends", [])
        if not any(t.get("source_platform") == "x" for t in trends):
            trends.insert(0, {
                "rank": 1,
                "hook": "Source: @UG_confesses on X — latest confession thread",
                "target_emotion": "curiosity",
                "source_platform": "x",
                "source_signal": "https://x.com/UG_confesses",
                "region": region,
                "genre": genre,
            })
        return trends


class PipelineEngine:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.client = OmniRouteClient()
        self.storage = Path(config.settings.storage_dir)

    async def execute(self, db: Session, region: str, genre: str, accent: str, language: str, episode_count: int = 60):
        run = Run(
            id=self.run_id,
            region=region,
            genre=genre,
            accent=accent,
            language=language,
            episode_count=episode_count,
            status=RunStatus.running,
        )
        db.add(run)
        db.commit()

        try:
            await self._stage(db, "trends", self._trends, region, genre)
            await self._stage(db, "screenplay", self._screenplay, db)
            await self._stage(db, "episodes", self._episodes, db)
            await self._stage(db, "scenes", self._scenes)
            await self._stage(db, "character_refs", self._character_refs)
            await self._stage(db, "shot_prompts", self._shot_prompts)
            await self._stage(db, "video_prompts", self._video_prompts)
            await self._stage(db, "voice_assignments", self._voice_assignments)
            await self._stage(db, "clips", self._clips)
            await self._stage(db, "video_produced", self._video_produced)
            await self._stage(db, "audio_produced", self._audio_produced)
            await self._stage(db, "timeline", self._timeline)
            run.status = RunStatus.draft
            db.commit()
        except Exception as e:
            logger.exception("Pipeline failed")
            run.status = RunStatus.failed
            run.error = str(e)
            db.commit()
            raise

    async def _stage(self, db: Session, name: str, fn, *args, **kwargs):
        stage = Stage(id=str(uuid.uuid4()), run_id=self.run_id, stage_name=name, status=StageStatus.running)
        db.add(stage)
        db.commit()
        try:
            result = await fn(*args, **kwargs)
            stage.output_json = json.dumps(result) if not isinstance(result, str) else result
            stage.status = StageStatus.completed
            stage.input_hash = "sha256-stub"
            db.commit()
            return result
        except Exception as e:
            stage.status = StageStatus.failed
            stage.error = str(e)
            db.commit()
            raise

    async def _trends(self, region: str, genre: str) -> list:
        raw = await self.client.get_trending(region, genre, 10)
        return [TrendSignal(**item).model_dump() for item in raw]

    async def _screenplay(self, db: Session) -> dict:
        trend_stage = db.query(Stage).filter(Stage.run_id == self.run_id, Stage.stage_name == "trends").first()
        trend_data = json.loads(trend_stage.output_json) if trend_stage and trend_stage.output_json else []
        chosen = trend_data[0] if isinstance(trend_data, list) and trend_data else {}
        premise = chosen.get("hook", "A gripping African family drama")
        content = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a screenplay writer for African drama short films."},
                {"role": "user", "content": f"Write a JSON story bible for 60 short-form episodes for: {premise}"},
            ],
            response_format={"type": "json_object"},
        )
        return content

    async def _episodes(self, db: Session) -> list:
        screenplay_stage = db.query(Stage).filter(Stage.run_id == self.run_id, Stage.stage_name == "screenplay").first()
        if not screenplay_stage or not screenplay_stage.output_json:
            return []
        try:
            screenplay = json.loads(screenplay_stage.output_json)
        except Exception:
            return []
        episodes = screenplay.get("episodes", [])
        if not episodes:
            return [{"episode_number": i + 1, "title": f"Episode {i + 1}", "summary": ""} for i in range(60)]
        return episodes[:60]

    async def _scenes(self) -> list:
        return []

    async def _character_refs(self) -> list:
        return []

    async def _shot_prompts(self) -> list:
        return []

    async def _video_prompts(self) -> list:
        return []

    async def _voice_assignments(self) -> list:
        return []

    async def _clips(self) -> list:
        return []

    async def _video_produced(self) -> list:
        return []

    async def _audio_produced(self) -> list:
        return []

    async def _timeline(self) -> dict:
        return {}
