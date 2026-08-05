# gandastream — Tasks

## Phase 1: Backend Foundation
- [x] Create project structure
- [x] Update config.py with OmniRoute settings + startup validation
- [x] Implement database models (SQLAlchemy)
- [x] Implement storage service
- [x] Implement health check endpoint
- [x] Implement error handling middleware

## Phase 2: Real API Clients
- [x] Implement unified OmniRoute client
- [x] Add startup config validation (fail fast on missing keys)

## Phase 3: Pipeline Backend
- [x] Implement pipeline execution engine
- [x] Implement stage persistence
- [x] Implement rerun/resume from stage
- [x] Implement approve/publish endpoints
- [x] Implement file export (video, audio, subtitles)

## Phase 4: Frontend (React Mobile PWA)
- [ ] Scaffold React + Vite + Tailwind v4 PWA
- [ ] Implement mobile-only layout
- [ ] Implement runs list view
- [ ] Implement run detail view
- [ ] Implement review/draft view
- [ ] Implement manual publish form
- [ ] Implement PWA manifest + service worker

## Phase 5: GitHub + Deployment
- [ ] Create GitHub repo via gh CLI
- [ ] Push code with proper .gitignore
- [ ] Create README with setup instructions
- [ ] Tag v0.1.0

## Phase 6: End-to-End Testing
- [ ] Run full pipeline with real APIs
- [ ] Verify manual review flow
- [ ] Verify manual publish flow
- [ ] Document API key requirements
