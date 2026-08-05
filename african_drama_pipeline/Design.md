# AfriDrama Pipeline — Design

## Architecture
Two main components:
1. FastAPI backend — pipeline execution, database, file storage, API clients
2. React mobile PWA — content review and manual publishing UI

Backend pipeline model is linear but each stage is a discrete database record with
input/output snapshots. This enables rerun, audit, and rollback.

## Data Flow
1. User triggers run via API or UI with region/genre/accent
2. Backend creates Run record, executes stages sequentially
3. After Editor stage, status = draft. No auto-publish.
4. User reviews in UI: video preview, subtitles, metadata
5. User clicks "Approve" → status = approved
6. User clicks "Publish to TikTok/YouTube/Instagram" → backend executes upload
7. PublishJob record created with result/error

## Database
SQLite for development, PostgreSQL-compatible schema.
Tables: runs, stages, media_assets, publish_jobs.

## File Storage
Local filesystem under `storage/`:
- storage/videos/ — final rendered videos
- storage/images/ — generated images
- storage/audio/ — synthesized audio
- storage/subtitles/ — SRT files

## Frontend
- React + Vite + Tailwind v4
- Mobile-only CSS (max-width constraints, touch targets)
- PWA: manifest.json, service worker for offline review
- API calls only; no mock data

## External APIs (config-driven, validated at startup)
- LLM: OPENAI_API_KEY or ANTHROPIC_API_KEY
- Image: REPLICATE_API_TOKEN or OPENAI_API_KEY
- Video: REPLICATE_API_TOKEN or STABILITY_API_KEY
- TTS: ELEVENLABS_API_KEY or AZURE_TTS_KEY
- Trends: TREND_API_URL + TREND_API_KEY
- OmniRoute: OMNIROUTE_HOST, OMNIROUTE_PORT, OMNIROUTE_USER, OMNIROUTE_PASS
- TikTok cookies: uploaded via API, stored encrypted

## Error Handling
- Missing config → HTTP 500 on health check with explicit missing keys
- Stage failure → run status = failed, error logged in stage record
- Publish failure → publish_job.error populated, UI shows retry

## GitHub Workflow
- gh CLI used for repo creation, issue management, PR creation
- git flow: main = production, develop = integration, feature branches per epic
- Every deployable state tagged
