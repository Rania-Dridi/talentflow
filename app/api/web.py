"""Server-rendered pages (Jinja2). They use the same services as the JSON API."""
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.deps import get_analytics, get_candidate_repo, get_job_repo
from app.models import PIPELINE, STAGE_LABELS, JobStatus, Stage
from app.repositories import CandidateRepository, JobRepository
from app.services import AnalyticsService

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
router = APIRouter(include_in_schema=False)

BOARD_STAGES = [*PIPELINE[:-1], Stage.HIRED, Stage.REJECTED]


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    analytics: AnalyticsService = Depends(get_analytics),
    jobs: JobRepository = Depends(get_job_repo),
    candidates: CandidateRepository = Depends(get_candidate_repo),
):
    stats = analytics.stats()
    top = [c for c in candidates.list() if c.stage not in (Stage.REJECTED, Stage.HIRED)][:5]
    return templates.TemplateResponse(
        request, "dashboard.html", {"stats": stats, "top": top, "jobs": jobs.list(JobStatus.OPEN)[:4], "page": "dashboard"}
    )


@router.get("/board", response_class=HTMLResponse)
def board(
    request: Request,
    job_id: int | None = None,
    jobs: JobRepository = Depends(get_job_repo),
    candidates: CandidateRepository = Depends(get_candidate_repo),
):
    selected = job_id or (jobs.list(JobStatus.OPEN)[0].id if jobs.list(JobStatus.OPEN) else None)
    columns = [
        {"stage": stage, "label": STAGE_LABELS[stage], "cards": candidates.list(job_id=selected, stage=stage)}
        for stage in BOARD_STAGES
    ]
    return templates.TemplateResponse(
        request, "board.html", {"columns": columns, "jobs": jobs.list(), "selected": selected, "page": "board"}
    )


@router.get("/jobs", response_class=HTMLResponse)
def job_list(
    request: Request,
    jobs: JobRepository = Depends(get_job_repo),
    candidates: CandidateRepository = Depends(get_candidate_repo),
):
    rows = []
    for job in jobs.list():
        counts = candidates.count_by_stage(job.id)
        rows.append({"job": job, "total": sum(counts.values()), "hired": counts.get(Stage.HIRED, 0)})
    return templates.TemplateResponse(request, "jobs.html", {"rows": rows, "page": "jobs"})
