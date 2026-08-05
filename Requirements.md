# gandastream — Requirements

## 1. Product Goal
Build a fully functional production system that automates creation of short-form drama videos
for African audiences. No mock data or fake services. If an external API key is missing,
the system must clearly fail at startup/config validation, not silently fall back to mocks.

## 2. Non-Negotiable Constraints
- Python 3.11+ backend, React mobile PWA frontend
- Strictly linear pipeline execution model
- Pydantic for all API contracts
- Content is NOT auto-uploaded. Pipeline ends at reviewable draft.
- Manual publishing workflow: user reviews draft, then manually triggers upload.
- Every external dependency is config-driven and validated at startup.
- Stage outputs persisted to database and filesystem for review.
- Full audit trail and rollback capability.

## 3. Functional Requirements

### 3.1 Backend API (FastAPI)
- POST /api/v1/pipeline/run — start a new pipeline run
- GET /api/v1/pipeline/runs — list runs with status
- GET /api/v1/pipeline/runs/{run_id} — get run detail
- POST /api/v1/pipeline/runs/{run_id}/approve — approve draft for publishing
- POST /api/v1/pipeline/runs/{run_id}/publish — manually publish approved content
- GET /api/v1/pipeline/runs/{run_id}/stages/{stage} — get specific stage output
- POST /api/v1/auth/tiktok/cookies — upload TikTok cookies for browser automation
- GET /api/v1/health — health check with config validation status

### 3.2 Database Models
- runs: id, region, genre, accent, status (draft/approved/published/failed), created_at, updated_at
- stages: run_id, stage_name, input_hash, output_json, status, created_at
- media_assets: run_id, stage, asset_type, storage_path, url, created_at
- publish_jobs: run_id, platform, status, scheduled_at, published_at, post_url, error

### 3.3 Pipeline Agents (Real Implementations)
- TrendResearcher: real trend API client via OmniRoute
- StoryWriter: real LLM client via OmniRoute
- Director: deterministic scene breakdown from screenplay
- CharacterDesigner: deterministic ref sheet generator
- PromptEngineer: deterministic prompt builder with style guide
- VideoDirector: deterministic camera/motion prompts
- VoiceDirector: deterministic voice assignment
- VisualProducer: real image generation via OmniRoute
- VideoProducer: real video generation via OmniRoute
- AudioProducer: real TTS via OmniRoute
- Editor: deterministic EDL + subtitle generation
- Publisher: metadata formatter + manual trigger only

### 3.4 Frontend (React Mobile PWA)
- React + Vite + Tailwind v4, mobile-only viewport
- PWA manifest + service worker for offline review
- Routes:
  - /runs — list pipeline runs
  - /runs/{run_id} — run detail with stage timeline
  - /runs/{run_id}/review — draft review page (video preview, subtitles, metadata)
  - /runs/{run_id}/publish — manual publish form per platform
- No auto-upload anywhere in UI. All publish actions are explicit button clicks.
- Offline-capable metadata editing and note-taking.

### 3.5 TikTok Browser Automation
- TikTok upload via OmniRoute with user-provided cookies
- Cookies stored server-side, not in frontend
- Upload only triggered by explicit user action from frontend
- Upload status streamed back to UI

## 4. Configuration
- `.env` required; startup fails fast if required keys are missing
- OmniRoute: OMNIROUTE_BASE_URL, OMNIROUTE_AUTH_TOKEN, OMNIROUTE_MODEL
- Platforms: TikTok, YouTube, Instagram
- Video specs: 1080×1920, 9:16, 30fps, 60–120s

## 5. Out of Scope
- Multi-user auth/roles
- Scheduled auto-publishing
