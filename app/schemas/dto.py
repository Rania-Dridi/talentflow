from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import JobStatus, Stage


class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    department: str = Field(min_length=2, max_length=80)
    location: str = Field(min_length=2, max_length=80)
    contract: str = "CDI"
    skills: str = ""
    openings: int = Field(default=1, ge=1, le=50)


class JobOut(JobCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: JobStatus
    created_at: datetime


class CandidateCreate(BaseModel):
    job_id: int
    full_name: str = Field(min_length=2, max_length=120)
    email: str
    headline: str = ""
    skills: str = ""
    years_experience: int = Field(default=0, ge=0, le=45)
    source: str = "LinkedIn"

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("invalid e-mail address")
        return value.lower()


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    full_name: str
    email: str
    headline: str
    skills: str
    years_experience: int
    source: str
    score: int
    stage: Stage
    applied_at: datetime


class StageChange(BaseModel):
    stage: Stage


class FunnelStep(BaseModel):
    stage: Stage
    label: str
    count: int


class StatsOut(BaseModel):
    open_jobs: int
    candidates: int
    hired: int
    average_score: float
    conversion_rate: float
    funnel: list[FunnelStep]
