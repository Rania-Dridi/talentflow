from app.models import PIPELINE, STAGE_LABELS, JobStatus, Stage
from app.repositories import CandidateRepository, JobRepository
from app.schemas.dto import FunnelStep, StatsOut


class AnalyticsService:
    def __init__(self, jobs: JobRepository, candidates: CandidateRepository) -> None:
        self.jobs = jobs
        self.candidates = candidates

    def stats(self, job_id: int | None = None) -> StatsOut:
        counts = self.candidates.count_by_stage(job_id)
        total = sum(counts.values())
        hired = counts.get(Stage.HIRED, 0)
        # The funnel is cumulative: a candidate in "offer" also went through earlier steps.
        funnel = []
        for index, stage in enumerate(PIPELINE):
            reached = sum(counts.get(s, 0) for s in PIPELINE[index:])
            funnel.append(FunnelStep(stage=stage, label=STAGE_LABELS[stage], count=reached))
        return StatsOut(
            open_jobs=len(self.jobs.list(JobStatus.OPEN)),
            candidates=total,
            hired=hired,
            average_score=self.candidates.average_score(),
            conversion_rate=round(100 * hired / total, 1) if total else 0.0,
            funnel=funnel,
        )
