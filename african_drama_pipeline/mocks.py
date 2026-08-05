from interfaces import (
    TrendResearchInterface,
    LLMInterface,
    ImageGenerationInterface,
    VideoGenerationInterface,
    TTSInterface,
    PlatformPublisherInterface,
)
from models import (
    TrendSignal,
    Screenplay,
    Character,
    Scene,
    DialogueLine,
    StyleGuide,
    ShotPrompt,
    CharacterRefSheet,
    VideoPrompt,
    VoiceAssignment,
    Clip,
    TimelineClip,
    SubtitleSegment,
    PostMetadata,
)
from config import settings
import logging

logger = logging.getLogger(__name__)


class MockTrendResearcher(TrendResearchInterface):
    def get_trending_premises(self, region: str, genre: str, limit: int = 10) -> list[TrendSignal]:
        sample = [
            TrendSignal(
                rank=1,
                hook="Mother-in-law secretly sells family land while son is abroad",
                target_emotion="outrage",
                source_platform="tiktok",
                source_signal="12.4K views in 48h — #FamilyLandScandal",
                region=region,
                genre=genre,
            ),
            TrendSignal(
                rank=2,
                hook="Woman discovers her husband built a second family in the village",
                target_emotion="betrayal",
                source_platform="instagram",
                source_signal="8.1K views in 24h — #VillageSecondWife",
                region=region,
                genre=genre,
            ),
            TrendSignal(
                rank=3,
                hook="Two sisters fight over one man at a wedding",
                target_emotion="drama",
                source_platform="youtube",
                source_signal="22K views in 72h — #WeddingSistersClash",
                region=region,
                genre=genre,
            ),
            TrendSignal(
                rank=4,
                hook="Son returns from abroad to find his mother living on the streets",
                target_emotion="guilt",
                source_platform="tiktok",
                source_signal="15K views in 36h — #ReturneeGuilt",
                region=region,
                genre=genre,
            ),
            TrendSignal(
                rank=5,
                hook="Choir mistress exposes pastor's secret affair during Sunday service",
                target_emotion="shock",
                source_platform="instagram",
                source_signal="31K views in 48h — #ChoirExpose",
                region=region,
                genre=genre,
            ),
        ]
        logger.info(f"MockTrendResearcher: returning {min(limit, len(sample))} trends for {region}/{genre}")
        return sample[:limit]


class MockLLMStoryWriter(LLMInterface):
    def generate_screenplay(self, premise: TrendSignal, duration_seconds: int = 90) -> Screenplay:
        hook = premise.hook
        title = "The Land That Tore Us Apart"
        logline = (
            "When Adaeze discovers her mother-in-law secretly sold the family land "
            "meant for her children's future, she must choose between justice and family peace."
        )
        characters = [
            Character(
                id="adaeze",
                name="Adaeze",
                description="Strong-willed 32-year-old market trader, fiercely protective of her children",
                appearance={
                    "face": "round, warm dark skin, high cheekbones",
                    "hair": "shoulder-length box braids with burgundy highlights",
                    "eyes": "large, expressive",
                },
                wardrobe={"top": " Ankara print blouse", "bottom": "matching wrapper", "accessories": "gold earrings, headtie"},
                voice_accent=premise.region,
            ),
            Character(
                id="mama_nneka",
                name="Mama Nneka",
                description="Respectable grandmother with a hidden calculating side, 68",
                appearance={
                    "face": "oval, lighter skin tone with traditional tattoos",
                    "hair": "white gele headwrap, natural grey roots",
                    "eyes": "sharp, piercing",
                },
                wardrobe={"top": "iro and buba lace set", "bottom": "shoes", "accessories": "beaded necklace, walking stick"},
                voice_accent=premise.region,
            ),
            Character(
                id="emeka",
                name="Emeka",
                description="Adaeze's husband, mild-mannered, caught between mother and wife",
                appearance={
                    "face": "strong jaw, smooth dark skin",
                    "hair": "low fade, short",
                    "eyes": "kind, tired-looking",
                },
                wardrobe={"top": "white kaftan", "bottom": "sandals", "accessories": "simple wristwatch"},
                voice_accent=premise.region,
            ),
        ]
        scenes = [
            Scene(
                scene_number=1,
                setting="Adaeze's living room — Lagos afternoon, warm sunlight through curtains",
                characters_present=["adaeze", "emeka"],
                action_summary="Adaeze confronts Emeka about missing land documents. Tension rises.",
                dialogue=[
                    DialogueLine(character_id="adaeze", character_name="Adaeze", text="Emeka, where are the land documents?", emotion="anxious", line_number=1),
                    DialogueLine(character_id="emeka", character_name="Emeka", text="I gave them to Mama Nneka last month.", emotion="defensive", line_number=2),
                    DialogueLine(character_id="adaeze", character_name="Adaeze", text="Your mother sold our land. I know it.", emotion="angry", line_number=3),
                ],
                estimated_duration_seconds=15.0,
            ),
            Scene(
                scene_number=2,
                setting="Mama Nneka's bedroom — ornate, old photos on walls",
                characters_present=["mama_nneka"],
                action_summary="Mama Nneka counts cash and hides the deed in a Bible.",
                dialogue=[
                    DialogueLine(character_id="mama_nneka", character_name="Mama Nneka", text="For the family, I did what I had to do.", emotion="resigned", line_number=4),
                ],
                estimated_duration_seconds=12.0,
            ),
            Scene(
                scene_number=3,
                setting="Community chief's palace — formal setting, elders present",
                characters_present=["adaeze", "emeka", "mama_nneka"],
                action_summary="Family dispute brought before elders. Shocking revelation.",
                dialogue=[
                    DialogueLine(character_id="adaeze", character_name="Adaeze", text="Mama sold our children's future for her brother.", emotion="betrayed", line_number=5),
                    DialogueLine(character_id="mama_nneka", character_name="Mama Nneka", text="He needed the money for his hospital bills.", emotion="defensive", line_number=6),
                    DialogueLine(character_id="emeka", character_name="Emeka", text="You both betrayed me — lying for months.", emotion="hurt", line_number=7),
                ],
                estimated_duration_seconds=25.0,
            ),
            Scene(
                scene_number=4,
                setting="Outside the palace — twilight, birds settling in trees",
                characters_present=["adaeze", "emeka"],
                action_summary="Emeka and Adaeze reconcile with a plan to rebuild.",
                dialogue=[
                    DialogueLine(character_id="emeka", character_name="Emeka", text="We will buy it back together.", emotion="hopeful", line_number=8),
                    DialogueLine(character_id="adaeze", character_name="Adaeze", text="Together. And this time, no secrets.", emotion="determined", line_number=9),
                ],
                estimated_duration_seconds=18.0,
            ),
            Scene(
                scene_number=5,
                setting="Market — morning, bustling, hopeful music",
                characters_present=["adaeze"],
                action_summary="Adaeze opens a new business stand — new beginning.",
                dialogue=[
                    DialogueLine(character_id="adaeze", character_name="Adaeze", text="From the ashes of betrayal, we rise.", emotion="resolute", line_number=10),
                ],
                estimated_duration_seconds=10.0,
            ),
        ]
        screenplay = Screenplay(
            title=title,
            logline=logline,
            characters=characters,
            scenes=scenes,
            total_estimated_duration=sum(s.estimated_duration_seconds for s in scenes),
        )
        logger.info(f"MockLLMStoryWriter: generated screenplay '{title}' ({screenplay.total_estimated_duration:.0f}s)")
        return screenplay


class MockDirector:
    def break_into_scenes(self, screenplay: Screenplay) -> list[Scene]:
        return screenplay.scenes


class MockPromptEngineer:
    def __init__(self, style_guide: StyleGuide | None = None):
        self.style_guide = style_guide or StyleGuide(
            lighting="warm golden hour, soft directional",
            color_palette="earth tones — ochre, burnt sienna, deep green, gold",
            aspect_ratio="9:16",
            style_summary="photorealistic African drama, cinematic, emotionally expressive faces, natural locations",
            negative_prompt="deformed, blurry, westernized, cartoon, low quality, extra fingers",
        )

    def generate_prompts(self, scenes: list[Scene], characters: list[CharacterRefSheet]) -> list[ShotPrompt]:
        char_map = {c.character_id: c for c in characters}
        shot_prompts = []
        for scene in scenes:
            for i in range(2):  # 2 shots per scene
                prompt = self._build_shot_prompt(scene, shot_number=i + 1, character_map=char_map)
                shot_prompts.append(ShotPrompt(
                    scene_number=scene.scene_number,
                    shot_number=i + 1,
                    prompt=prompt,
                    style_guide=self.style_guide,
                    character_refs=list(char_map.values()),
                ))
        logger.info(f"MockPromptEngineer: generated {len(shot_prompts)} shot prompts")
        return shot_prompts

    def _build_shot_prompt(self, scene: Scene, shot_number: int, character_map: dict) -> str:
        present = [character_map.get(cid, {"name": cid}) for cid in scene.characters_present]
        names = ", ".join(p.name if isinstance(p, CharacterRefSheet) else str(p) for p in present)
        char_descriptions = " | ".join(
            f"{p.name}: {p.appearance}" for p in present if isinstance(p, CharacterRefSheet)
        ) if present else "empty scene"
        return (
            f"Scene {scene.scene_number} Shot {shot_number}: {scene.setting}. "
            f"Characters: {names}. "
            f"Action: {scene.action_summary}. "
            f"Character details: {char_descriptions}. "
            f"Style: {self.style_guide.style_summary}. "
            f"Lighting: {self.style_guide.lighting}. "
            f"Color palette: {self.style_guide.color_palette}."
        )


class MockCharacterDesigner:
    def generate_ref_sheets(self, characters: list[Character]) -> list[CharacterRefSheet]:
        refs = []
        for char in characters:
            refs.append(CharacterRefSheet(
                character_id=char.id,
                name=char.name,
                appearance=char.appearance or {},
                wardrobe=char.wardrobe or {},
                distinguishing_features=[
                    f"Appearance: {char.appearance}",
                    f"Wardrobe: {char.wardrobe}",
                ],
                reference_prompt_suffix=(
                    f"[{char.name}] consistent appearance: {char.appearance}, "
                    f"wardrobe: {char.wardrobe}, accent: {char.voice_accent}"
                ),
            ))
        logger.info(f"MockCharacterDesigner: generated {len(refs)} ref sheets")
        return refs


class MockVideoDirector:
    def generate_video_prompts(self, scenes: list[Scene]) -> list[VideoPrompt]:
        def _emotion(scene: Scene) -> str:
            if scene.dialogue:
                return scene.dialogue[0].emotion
            return "neutral"
        prompts = []
        for scene in scenes:
            emotion = _emotion(scene)
            shots = max(2, int(scene.estimated_duration_seconds / 10))
            for s in range(shots):
                prompts.append(VideoPrompt(
                    scene_number=scene.scene_number,
                    shot_number=s + 1,
                    camera_movement="slow push-in" if s == 0 else "pan across characters",
                    motion_intensity="low" if emotion in ["guilt", "resigned"] else "medium",
                    transition_in="crossfade" if s > 0 else "none",
                    transition_out="cut",
                    duration_seconds=scene.estimated_duration_seconds / shots,
                ))
        logger.info(f"MockVideoDirector: generated {len(prompts)} video prompts")
        return prompts


class MockVoiceDirector:
    def assign_voices(self, scenes: list[Scene], characters: list[Character], accent: str) -> list[VoiceAssignment]:
        char_map = {c.id: c for c in characters}
        seen = set()
        assignments = []
        for scene in scenes:
            for line in scene.dialogue:
                if line.character_id not in seen:
                    seen.add(line.character_id)
                    assignments.append(VoiceAssignment(
                        character_id=line.character_id,
                        character_name=line.character_name,
                        emotion=line.emotion,
                        pacing="slow and deliberate" if line.emotion in ["angry", "betrayed"] else "natural conversational",
                        tts_provider_hint="mock_tts_default",
                    ))
        logger.info(f"MockVoiceDirector: {len(assignments)} voice assignments with accent={accent}")
        return assignments


class MockImageGenerator(ImageGenerationInterface):
    def __init__(self, output_dir: str = "runs"):
        self.output_dir = output_dir

    def generate_scene_image(self, prompt: str, style_guide: StyleGuide, seed: int | None = None) -> str:
        # In a real impl this would call DALL-E / Stable Diffusion.
        # Here we just log and return a fake path.
        logger.info(f"MockImageGenerator: would generate image for: {prompt[:80]}...")
        return f"{self.output_dir}/mock_renders/image_shot_{seed or 0}.png"


class MockVideoGenerator(VideoGenerationInterface):
    def __init__(self, output_dir: str = "runs"):
        self.output_dir = output_dir

    def generate_shot_video(self, image_path: str, video_prompt: VideoPrompt) -> str:
        logger.info(f"MockVideoGenerator: would animate {image_path} with prompt for scene {video_prompt.scene_number}")
        return f"{self.output_dir}/mock_renders/video_s{video_prompt.scene_number}_sh{video_prompt.shot_number}.mp4"


class MockTTS(TTSInterface):
    def synthesize(self, text: str, character: VoiceAssignment, output_path: str) -> str:
        logger.info(f"MockTTS: [{character.character_name}] '{text[:60]}...' -> {output_path}")
        return f"{output_path}_mock.wav"


class MockPlatformPublisher(PlatformPublisherInterface):
    def upload_video(self, platform: str, video_path: str, metadata: PostMetadata) -> str:
        logger.info(
            f"MockPlatformPublisher: would upload to {platform}\n"
            f"  video={video_path}\n"
            f"  caption={metadata.caption[:80]}...\n"
            f"  hashtags={metadata.hashtags[:5]}..."
        )
        return f"mock://{platform}/{metadata.caption[:20].replace(' ', '_')}"
