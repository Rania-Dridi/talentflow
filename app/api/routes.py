"""JSON API. Handlers stay thin: parse, call a service, return a schema."""
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_analytics, get_candidate_repo, get_job_repo, get_pipeline
from app.models import JobStatus, Stage
from app.repositories import CandidateRepository, JobRepository
from app.schemas.dto import CandidateCreate, CandidateOut, JobCreate, JobOut, StageChange, StatsOut
from app.services import AnalyticsService, PipelineService

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(status_filter: JobStatus | None = Query(None, alias="status"), jobs: JobRepository = Depends(get_job_repo)):
    return jobs.list(status_filter)


@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, service: PipelineService = Depends(get_pipeline)):
    return service.create_job(payload)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, service: PipelineService = Depends(get_pipeline)):
    return service.get_job(job_id)


@router.get("/candidates", response_model=list[CandidateOut])
def list_candidates(
    job_id: int | None = None,
    stage: Stage | None = None,
    q: str | None = None,
    candidates: CandidateRepository = Depends(get_candidate_repo),
):
    return candidates.list(job_id, stage, q)


@router.post("/candidates", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate, service: PipelineService = Depends(get_pipeline)):
    return service.add_candidate(payload)


@router.patch("/candidates/{candidate_id}/stage", response_model=CandidateOut)
def change_stage(candidate_id: int, payload: StageChange, service: PipelineService = Depends(get_pipeline)):
    return service.move(candidate_id, payload.stage)


@router.get("/stats", response_model=StatsOut)
def stats(job_id: int | None = None, analytics: AnalyticsService = Depends(get_analytics)):
    return analytics.stats(job_id)
