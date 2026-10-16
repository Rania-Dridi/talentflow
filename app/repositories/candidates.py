from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Candidate, Stage


class CandidateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, job_id: int | None = None, stage: Stage | None = None, query: str | None = None) -> list[Candidate]:
        stmt = select(Candidate).order_by(Candidate.score.desc(), Candidate.id)
        if job_id:
            stmt = stmt.where(Candidate.job_id == job_id)
        if stage:
            stmt = stmt.where(Candidate.stage == stage)
        if query:
            like = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(func.lower(Candidate.full_name).like(like), func.lower(Candidate.skills).like(like), func.lower(Candidate.headline).like(like))
            )
        return list(self.session.scalars(stmt))

    def get(self, candidate_id: int) -> Candidate | None:
        return self.session.get(Candidate, candidate_id)

    def add(self, candidate: Candidate) -> Candidate:
        self.session.add(candidate)
        self.session.commit()
        return candidate

    def count_by_stage(self, job_id: int | None = None) -> dict[Stage, int]:
        stmt = select(Candidate.stage, func.count()).group_by(Candidate.stage)
        if job_id:
            stmt = stmt.where(Candidate.job_id == job_id)
        return {stage: count for stage, count in self.session.execute(stmt)}

    def average_score(self) -> float:
        value = self.session.scalar(select(func.avg(Candidate.score)))
        return round(float(value or 0), 1)

    def save(self) -> None:
        self.session.commit()
