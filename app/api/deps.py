from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.repositories import CandidateRepository, JobRepository
from app.services import AnalyticsService, PipelineService


def get_pipeline(session: Session = Depends(get_session)) -> PipelineService:
    return PipelineService(JobRepository(session), CandidateRepository(session))


def get_analytics(session: Session = Depends(get_session)) -> AnalyticsService:
    return AnalyticsService(JobRepository(session), CandidateRepository(session))


def get_job_repo(session: Session = Depends(get_session)) -> JobRepository:
    return JobRepository(session)


def get_candidate_repo(session: Session = Depends(get_session)) -> CandidateRepository:
    return CandidateRepository(session)
