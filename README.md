# TalentFlow

Recruitment pipeline for IT teams: job openings, candidates, a drag-and-drop kanban board, an explainable
candidate score and a hiring funnel. Built with Python, FastAPI and SQLAlchemy.

Personal demo project written in 2026 to practise a layered Python architecture. All data is fictional.

## Features

- Dashboard: open jobs, applications, hires, average score, cumulative hiring funnel and conversion rate.
- Pipeline board: drag a candidate between stages (`new`, `screening`, `interview`, `technical`, `offer`, `hired`, `rejected`).
  The server validates every move and the card goes back if the move is refused.
- Explainable score (0-100): 60 points for matching the job's required skills, up to 40 for experience.
- JSON API with automatic OpenAPI docs at `/docs`.

Business rules (in `app/services/pipeline.py`):

- A candidate can only be hired from the `offer` stage.
- Hiring the last opening closes the job; a closed job rejects new applications.
- The same e-mail cannot apply twice to the same job.
- `hired` is final; a `rejected` candidate can only be reconsidered as `new`.

## Architecture

```
app/
  api/            routes.py (JSON API), web.py (HTML pages), deps.py (dependency injection)
  services/       pipeline.py (rules), analytics.py (funnel), scoring.py (score), errors.py
  repositories/   jobs.py, candidates.py (the only place that builds queries)
  models/         SQLAlchemy entities and the Stage enum
  schemas/        Pydantic request/response models
  core/           settings and database session
  templates/ static/   Jinja2 pages, CSS and the drag-and-drop script
tests/            unit tests (rules, scoring), API tests, page rendering tests
```

Dependencies point one way: `api -> services -> repositories -> models`. Services raise domain errors
(`NotFound`, `Conflict`); one exception handler maps them to HTTP 404 and 409.

## Run

```bash
python -m venv .venv
.venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. The first start creates a SQLite file with demo data
(set `SEED_DEMO_DATA=0` to start empty, or `DATABASE_URL` to use another database).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

20 tests: scoring, pipeline rules, API behaviour and page rendering.

## Screenshots

In `docs/screenshots/`: dashboard, pipeline board, job list.
