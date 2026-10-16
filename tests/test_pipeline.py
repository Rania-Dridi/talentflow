import pytest

from app.models import JobStatus, Stage
from app.schemas.dto import CandidateCreate, JobCreate
from app.services import Conflict, NotFound


def make_job(service, openings=1):
    return service.create_job(JobCreate(title="QA engineer", department="Quality", location="Tunis", skills="python, playwright", openings=openings))


def apply(service, job, email="a@example.com", **kw):
    data = dict(job_id=job.id, full_name="Alice Test", email=email, skills="python", years_experience=2)
    data.update(kw)
    return service.add_candidate(CandidateCreate(**data))


def test_new_candidate_starts_in_new_stage_with_a_score(service):
    candidate = apply(service, make_job(service))
    assert candidate.stage is Stage.NEW
    assert candidate.score == 38  # 1 of 2 skills (30) + 2 years (8)


def test_same_email_cannot_apply_twice_to_the_same_job(service):
    job = make_job(service)
    apply(service, job)
    with pytest.raises(Conflict):
        apply(service, job)


def test_unknown_job_is_not_found(service):
    with pytest.raises(NotFound):
        service.add_candidate(CandidateCreate(job_id=99, full_name="Bob", email="b@example.com"))


def test_cannot_hire_without_an_offer(service):
    candidate = apply(service, make_job(service))
    with pytest.raises(Conflict):
        service.move(candidate.id, Stage.HIRED)


def test_hiring_the_last_opening_closes_the_job(service):
    job = make_job(service, openings=1)
    candidate = apply(service, job)
    service.move(candidate.id, Stage.OFFER)
    service.move(candidate.id, Stage.HIRED)
    assert job.status is JobStatus.CLOSED
    with pytest.raises(Conflict):
        apply(service, job, email="late@example.com")


def test_job_with_two_openings_stays_open_after_one_hire(service):
    job = make_job(service, openings=2)
    first = apply(service, job)
    service.move(first.id, Stage.OFFER)
    service.move(first.id, Stage.HIRED)
    assert job.status is JobStatus.OPEN


def test_hired_candidate_is_final(service):
    job = make_job(service, openings=2)
    candidate = apply(service, job)
    service.move(candidate.id, Stage.OFFER)
    service.move(candidate.id, Stage.HIRED)
    with pytest.raises(Conflict):
        service.move(candidate.id, Stage.INTERVIEW)


def test_rejected_candidate_can_be_reconsidered_as_new(service):
    candidate = apply(service, make_job(service))
    service.move(candidate.id, Stage.REJECTED)
    assert service.move(candidate.id, Stage.NEW).stage is Stage.NEW
    service.move(candidate.id, Stage.REJECTED)
    with pytest.raises(Conflict):
        service.move(candidate.id, Stage.INTERVIEW)
