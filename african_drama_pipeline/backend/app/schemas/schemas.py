from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from backend.app.models.models import RunStatus, StageStatus, PublishStatus


class RunCreate(BaseModel):
    region: str
    genre: str
    accent: str
    language: str = "en"


class RunResponse(BaseModel):
    id: str
    region: str
    genre: str
    accent: str
    language: str
    status: RunStatus
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StageResponse(BaseModel):
    id: str
    run_id: str
    stage_name: str
    status: StageStatus
    error: Optional[str] = None
    output: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MediaAssetResponse(BaseModel):
    id: str
    run_id: str
    stage: str
    asset_type: str
    storage_path: str
    url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PublishJobResponse(BaseModel):
    id: str
    run_id: str
    platform: str
    status: PublishStatus
    post_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TikTokCookiesUpload(BaseModel):
    cookies: dict = Field(..., description="TikTok cookies JSON object")
