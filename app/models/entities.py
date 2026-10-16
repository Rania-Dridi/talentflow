from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Stage(str, enum.Enum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    TECHNICAL = "technical"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"

    @property
    def label(self) -> str:
        return STAGE_LABELS[self]


STAGE_LABELS = {
    Stage.NEW: "Nouveaux",
    Stage.SCREENING: "Présélection",
    Stage.INTERVIEW: "Entretien RH",
    Stage.TECHNICAL: "Test technique",
    Stage.OFFER: "Offre",
    Stage.HIRED: "Embauchés",
    Stage.REJECTED: "Refusés",
}

# Order of the hiring funnel (rejected is an exit, not a step).
PIPELINE = [Stage.NEW, Stage.SCREENING, Stage.INTERVIEW, Stage.TECHNICAL, Stage.OFFER, Stage.HIRED]


class JobStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(140))
    department: Mapped[str] = mapped_column(String(80))
    location: Mapped[str] = mapped_column(String(80))
    contract: Mapped[str] = mapped_column(String(40), default="CDI")
    skills: Mapped[str] = mapped_column(String(300), default="")
    openings: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    candidates: Mapped[list[Candidate]] = relationship(back_populates="job", cascade="all, delete-orphan")

    @property
    def skill_set(self) -> set[str]:
        return {s.strip().lower() for s in self.skills.split(",") if s.strip()}


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(190))
    headline: Mapped[str] = mapped_column(String(160), default="")
    skills: Mapped[str] = mapped_column(String(300), default="")
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(60), default="LinkedIn")
    score: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[Stage] = mapped_column(Enum(Stage), default=Stage.NEW)
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped[Job] = relationship(back_populates="candidates")

    @property
    def skill_list(self) -> list[str]:
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def initials(self) -> str:
        parts = self.full_name.split()
        return "".join(p[0] for p in parts[:2]).upper()
