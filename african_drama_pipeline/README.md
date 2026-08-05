# AfriDrama Pipeline

A Python-based multi-agent system that automates production of short-form drama videos
(TikTok / YouTube Shorts / Instagram Reels) aimed at African audiences, from trend discovery
to publishing-ready metadata.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Run full pipeline end-to-end
python main.py run --region Nigeria --genre family_drama --accent Nigerian

# List previous runs
python main.py list-runs

# Inspect a stage output
python main.py inspect --run-id <run_id> --stage screenplay

# Resume from a specific stage (skips upstream)
python main.py resume --run-id <run_id> --from-stage video_prompts
```

All stage outputs are written under `runs/<run_id>/` as JSON for manual review.

## Configuration

Copy `.env.example` to `.env` and set OmniRoute + TikTok cookie values:
- `OMNIROUTE_HOST`
- `OMNIROUTE_PORT`
- `OMNIROUTE_USER`
- `OMNIROUTE_PASS`
- `TIKTOK_COOKIES_PATH`

TikTok publishing uses browser automation through OmniRoute, not a direct HTTP upload.
Provide a valid TikTok cookies JSON at `TIKTOK_COOKIES_PATH`.

## Architecture

Linear pipeline passing a shared `ProjectState` through 12 stages:

1. Trend Researcher — discovers trending drama hooks
2. Story Writer — generates screenplay (structured JSON)
3. Director — scene breakdown
4. Character Designer — persistent ref sheets
5. Prompt Engineer — image-gen prompts + style guide
6. Video Director — camera/motion prompts per shot
7. Voice Director — voice assignments + pacing
8. Visual Producer — generates images
9. Video Producer — generates animated clips
10. Audio Producer — synthesizes dialogue (TTS)
11. Editor — builds timeline/EDL + SRT subtitles
12. Publisher — formats platform-specific metadata, uploads to TikTok via browser automation

## Swapping in real APIs

Every external dependency is an abstract interface:

- `interfaces.py` — `TrendResearchInterface`, `LLMInterface`, `ImageGenerationInterface`,
  `VideoGenerationInterface`, `TTSInterface`, `PlatformPublisherInterface`
- `mocks.py` — `Mock*` implementations that log instead of calling real services
- `integrations/omni_route.py` — TikTok publisher through OmniRoute/CDP with cookies

To go live: implement each interface with a real client, then inject it into the agent's
constructor. No changes to `agents/` or `pipeline.py` are needed.
