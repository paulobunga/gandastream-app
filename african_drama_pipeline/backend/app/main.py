from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import config
from backend.app.core.database import engine, get_db
from backend.app.models.models import Base, Run, Stage, MediaAsset, PublishJob, RunStatus, StageStatus, PublishStatus
from backend.app.schemas.schemas import RunCreate, RunResponse, StageResponse, PublishJobResponse, TikTokCookiesUpload
from backend.app.pipeline.engine import PipelineEngine, OmniRouteClient
import uuid
import json
import logging

logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="gandastream API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health():
    try:
        OmniRouteClient()
        omni_status = "configured"
    except RuntimeError as e:
        omni_status = f"misconfigured: {e}"
    return {
        "status": "ok",
        "omni_route": omni_status,
        "environment": config.settings.environment,
    }


@app.post("/api/v1/pipeline/run", response_model=RunResponse)
async def run_pipeline(payload: RunCreate, db: Session = Depends(get_db)):
    run_id = str(uuid.uuid4())
    engine = PipelineEngine(run_id)
    await engine.execute(db, payload.region, payload.genre, payload.accent, payload.language)
    run = db.query(Run).filter(Run.id == run_id).first()
    return RunResponse.model_validate(run)


@app.get("/api/v1/pipeline/runs", response_model=list[RunResponse])
def list_runs(db: Session = Depends(get_db)):
    return [RunResponse.model_validate(r) for r in db.query(Run).order_by(Run.created_at.desc()).all()]


@app.get("/api/v1/pipeline/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(404, "Run not found")
    return RunResponse.model_validate(run)


@app.get("/api/v1/pipeline/runs/{run_id}/stages/{stage}", response_model=StageResponse)
def get_stage(run_id: str, stage: str, db: Session = Depends(get_db)):
    s = db.query(Stage).filter(Stage.run_id == run_id, Stage.stage_name == stage).first()
    if not s:
        raise HTTPException(404, "Stage not found")
    return StageResponse(
        id=s.id,
        run_id=s.run_id,
        stage_name=s.stage_name,
        status=s.status,
        error=s.error,
        output=json.loads(s.output_json) if s.output_json else None,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@app.post("/api/v1/pipeline/runs/{run_id}/approve", response_model=RunResponse)
def approve_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(404, "Run not found")
    if run.status != RunStatus.draft:
        raise HTTPException(400, f"Run is in status {run.status}, cannot approve")
    run.status = RunStatus.approved
    db.commit()
    return RunResponse.model_validate(run)


@app.post("/api/v1/pipeline/runs/{run_id}/publish", response_model=PublishJobResponse)
def publish_run(run_id: str, platform: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(404, "Run not found")
    if run.status not in {RunStatus.approved, RunStatus.draft}:
        raise HTTPException(400, f"Run is in status {run.status}, cannot publish")
    job = PublishJob(id=str(uuid.uuid4()), run_id=run_id, platform=platform, status=PublishStatus.publishing)
    db.add(job)
    # Real upload will be implemented here with TikTok browser automation via OmniRoute
    job.status = PublishStatus.published
    job.post_url = f"https://www.{platform}.com/@user/video/{run_id}"
    run.status = RunStatus.published
    db.commit()
    return PublishJobResponse.model_validate(job)


@app.post("/api/v1/auth/tiktok/cookies")
def upload_tiktok_cookies(payload: TikTokCookiesUpload, db: Session = Depends(get_db)):
    path = Path(config.settings.tiktok_cookies_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload.cookies))
    return {"status": "saved", "path": str(path)}


@app.get("/api/v1/pipeline/runs/{run_id}/media", response_model=list[MediaAssetResponse])
def list_media(run_id: str, db: Session = Depends(get_db)):
    return [MediaAssetResponse.model_validate(m) for m in db.query(MediaAsset).filter(MediaAsset.run_id == run_id).all()]
