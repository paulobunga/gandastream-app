# gandastream

Real product: automated short-form drama video production pipeline with manual review/publish.
No mock data. OmniRoute-backed AI. React mobile PWA frontend. Packaged for VPS deployment with Docker.

## Quickstart

```bash
cp .env.example .env
# fill in OMNIROUTE_BASE_URL and OMNIROUTE_AUTH_TOKEN

python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# run backend only
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# frontend dev
cd frontend && npm install && npm run dev
```

## VPS Deployment

```bash
# on VPS
git clone <repo-url> /opt/gandastream
cd /opt/gandastream
cp .env.example .env
# edit .env with production values

docker compose up -d --build
```

## Architecture

- Backend: FastAPI + SQLAlchemy + OmniRoute AI client
- Frontend: React + Vite + Tailwind v4 mobile PWA
- Pipeline: 60-episode short drama generation, manual review, manual publish
- Storage: local filesystem under storage/
- Database: SQLite (development) / PostgreSQL (production)

## Manual Publishing

Content is never auto-uploaded. The pipeline ends at draft status.
User reviews in the mobile UI, then manually triggers publish to TikTok/YouTube/Instagram.
