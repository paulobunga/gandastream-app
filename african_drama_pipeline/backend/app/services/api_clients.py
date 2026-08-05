import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def validate_required_keys(provider: str, keys: list[str]) -> None:
    missing = [k for k in keys if not getattr(config.settings.providers, k, "")]
    if missing:
        raise ValidationError(
            f"Missing required config for {provider}: {', '.join(missing)}. "
            f"Set them in .env or environment variables."
        )


class LLMClient:
    def __init__(self):
        validate_required_keys("LLM", ["llm_api_key", "llm_model"])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate_screenplay(self, premise: str, duration: int = 90) -> dict:
        provider = config.settings.providers.llm_provider
        api_key = config.settings.providers.llm_api_key
        model = config.settings.providers.llm_model
        logger.info(f"LLMClient: generating screenplay via {provider} with model {model}")

        if provider == "openai":
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a screenplay writer for African drama short films."},
                            {"role": "user", "content": f"Write a {duration}s screenplay JSON for: {premise}"},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        elif provider == "anthropic":
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": 2048,
                        "messages": [
                            {"role": "user", "content": f"Write a {duration}s screenplay JSON for: {premise}. Output JSON only."}
                        ],
                    },
                )
                resp.raise_for_status()
                return resp.json()["content"][0]["text"]
        else:
            raise NotImplementedError(f"LLM provider {provider} not implemented")


class ImageGenClient:
    def __init__(self):
        validate_required_keys("ImageGen", ["image_api_key"])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate_image(self, prompt: str, output_path: str) -> str:
        provider = config.settings.providers.image_provider
        api_key = config.settings.providers.image_api_key
        logger.info(f"ImageGenClient: generating image via {provider}")

        if provider == "openai":
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1792"},
                )
                resp.raise_for_status()
                url = resp.json()["data"][0]["url"]
                # download image
                img_resp = await client.get(url)
                img_resp.raise_for_status()
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                return output_path
        elif provider == "replicate":
            # initiate prediction
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={"Authorization": f"Token {api_key}"},
                    json={"version": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b", "input": {"prompt": prompt, "width": 1080, "height": 1920}},
                )
                resp.raise_for_status()
                pred = resp.json()
                pred_id = pred["id"]
                # poll
                import asyncio
                for _ in range(30):
                    await asyncio.sleep(2)
                    poll = await client.get(f"https://api.replicate.com/v1/predictions/{pred_id}", headers={"Authorization": f"Token {api_key}"})
                    poll.raise_for_status()
                    data = poll.json()
                    if data.get("status") == "succeeded" and data.get("output"):
                        url = data["output"][0] if isinstance(data["output"], list) else data["output"]
                        img_resp = await client.get(url)
                        img_resp.raise_for_status()
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        return output_path
                raise RuntimeError("Replicate image generation timed out")
        else:
            raise NotImplementedError(f"Image provider {provider} not implemented")


class VideoGenClient:
    def __init__(self):
        validate_required_keys("VideoGen", ["video_api_key"])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate_video(self, image_path: str, prompt: str, output_path: str) -> str:
        provider = config.settings.providers.video_provider
        api_key = config.settings.providers.video_api_key
        logger.info(f"VideoGenClient: generating video via {provider}")

        if provider == "replicate":
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={"Authorization": f"Token {api_key}"},
                    json={
                        "version": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                        "input": {"image": open(image_path, "rb"), "prompt": prompt, "num_frames": 90},
                    },
                )
                resp.raise_for_status()
                pred = resp.json()
                pred_id = pred["id"]
                import asyncio
                for _ in range(60):
                    await asyncio.sleep(3)
                    poll = await client.get(f"https://api.replicate.com/v1/predictions/{pred_id}", headers={"Authorization": f"Token {api_key}"})
                    poll.raise_for_status()
                    data = poll.json()
                    if data.get("status") == "succeeded" and data.get("output"):
                        url = data["output"]
                        vid_resp = await client.get(url)
                        vid_resp.raise_for_status()
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(vid_resp.content)
                        return output_path
                raise RuntimeError("Replicate video generation timed out")
        elif provider == "stability":
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://api.stability.ai/v2beta/video/generate",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "multipart/form-data"},
                    files={"image": open(image_path, "rb")},
                    data={"prompt": prompt},
                )
                resp.raise_for_status()
                url = resp.json()["video_url"]
                vid_resp = await client.get(url)
                vid_resp.raise_for_status()
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(vid_resp.content)
                return output_path
        else:
            raise NotImplementedError(f"Video provider {provider} not implemented")


class TTSClient:
    def __init__(self):
        validate_required_keys("TTS", ["tts_api_key"])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def synthesize(self, text: str, output_path: str, voice_id: str = "default") -> str:
        provider = config.settings.providers.tts_provider
        api_key = config.settings.providers.tts_api_key
        logger.info(f"TTSClient: synthesizing via {provider}")

        if provider == "elevenlabs":
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": api_key},
                    json={"text": text, "model_id": "eleven_multilingual_v2"},
                )
                resp.raise_for_status()
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return output_path
        elif provider == "azure":
            # azure tts requires region + endpoint configured; for now fail fast with guidance
            raise NotImplementedError("Azure TTS requires endpoint + region in config")
        else:
            raise NotImplementedError(f"TTS provider {provider} not implemented")


class TrendClient:
    def __init__(self):
        if not config.settings.providers.trend_api_url:
            raise ValidationError("TREND_API_URL is required for TrendClient")

    async def get_trending(self, region: str, genre: str, limit: int = 10) -> list[dict]:
        api_key = config.settings.providers.trend_api_key
        url = config.settings.providers.trend_api_url
        logger.info(f"TrendClient: fetching trends from {url}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params={"region": region, "genre": genre, "limit": limit}, headers={"Authorization": f"Bearer {api_key}"})
            resp.raise_for_status()
            return resp.json().get("trends", [])
