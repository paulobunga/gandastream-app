from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import config
from backend.app.core.database import Base


class RunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    draft = "draft"
    approved = "approved"
    published = "published"
    failed = "failed"


class StageStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class PublishStatus(str, enum.Enum):
    pending = "pending"
    publishing = "publishing"
    published = "published"
    failed = "failed"


class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True)
    region = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    accent = Column(String, nullable=False)
    language = Column(String, nullable=False)
    episode_count = Column(Integer, default=60)
    status = Column(SQLEnum(RunStatus), default=RunStatus.pending)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stages = relationship("Stage", back_populates="run", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="run", cascade="all, delete-orphan")
    publish_jobs = relationship("PublishJob", back_populates="run", cascade="all, delete-orphan")


class Stage(Base):
    __tablename__ = "stages"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    stage_name = Column(String, nullable=False)
    input_hash = Column(String, nullable=True)
    output_json = Column(Text, nullable=True)
    status = Column(SQLEnum(StageStatus), default=StageStatus.pending)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    run = relationship("Run", back_populates="stages")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    stage = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="media_assets")


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    platform = Column(String, nullable=False)
    status = Column(SQLEnum(PublishStatus), default=PublishStatus.pending)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    post_url = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="publish_jobs")
