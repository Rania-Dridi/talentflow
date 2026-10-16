from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, JobStatus


class JobRepository:
    """Data access for jobs. Services never build queries themselves."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, status: JobStatus | None = None) -> list[Job]:
        stmt = select(Job).order_by(Job.created_at.desc(), Job.id.desc())
        if status:
            stmt = stmt.where(Job.status == status)
        return list(self.session.scalars(stmt))

    def get(self, job_id: int) -> Job | None:
        return self.session.get(Job, job_id)

    def add(self, job: Job) -> Job:
        self.session.add(job)
        self.session.commit()
        return job

    def save(self) -> None:
        self.session.commit()
