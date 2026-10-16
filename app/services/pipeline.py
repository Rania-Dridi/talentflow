"""Hiring pipeline business rules."""
from app.models import Candidate, Job, JobStatus, Stage
from app.repositories import CandidateRepository, JobRepository
from app.schemas.dto import CandidateCreate, JobCreate
from app.services.errors import Conflict, NotFound
from app.services.scoring import compute_score

TERMINAL = {Stage.HIRED, Stage.REJECTED}


class PipelineService:
    def __init__(self, jobs: JobRepository, candidates: CandidateRepository) -> None:
        self.jobs = jobs
        self.candidates = candidates

    # ----- jobs -------------------------------------------------------------------------------
    def create_job(self, data: JobCreate) -> Job:
        return self.jobs.add(Job(**data.model_dump()))

    def get_job(self, job_id: int) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise NotFound(f"Job {job_id} not found")
        return job

    # ----- candidates ---------------------------------------------------------------------------
    def add_candidate(self, data: CandidateCreate) -> Candidate:
        job = self.get_job(data.job_id)
        if job.status is JobStatus.CLOSED:
            raise Conflict("This job is closed to new applications")
        if any(c.email == data.email for c in self.candidates.list(job_id=job.id)):
            raise Conflict("This candidate already applied to this job")
        candidate = Candidate(**data.model_dump())
        candidate.score = compute_score(job.skills, data.skills, data.years_experience)
        return self.candidates.add(candidate)

    def move(self, candidate_id: int, target: Stage) -> Candidate:
        candidate = self.candidates.get(candidate_id)
        if not candidate:
            raise NotFound(f"Candidate {candidate_id} not found")
        current = candidate.stage

        if current == target:
            return candidate
        if current in TERMINAL and not (current is Stage.REJECTED and target is Stage.NEW):
            raise Conflict(f"A candidate who is {current.label.lower()} cannot be moved")
        if target is Stage.HIRED:
            self._hire(candidate)
        candidate.stage = target
        self.candidates.save()
        return candidate

    def _hire(self, candidate: Candidate) -> None:
        if candidate.stage is not Stage.OFFER:
            raise Conflict("A candidate can only be hired after an offer")
        job = candidate.job
        hired = sum(1 for c in job.candidates if c.stage is Stage.HIRED)
        if hired >= job.openings:
            raise Conflict("All openings for this job are already filled")
        if hired + 1 >= job.openings:
            job.status = JobStatus.CLOSED
