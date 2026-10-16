import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_session, make_engine
from app.main import create_app
from app.repositories import CandidateRepository, JobRepository
from app.services import PipelineService


@pytest.fixture()
def session():
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    yield db
    db.close()


@pytest.fixture()
def service(session):
    return PipelineService(JobRepository(session), CandidateRepository(session))


@pytest.fixture()
def client(session, monkeypatch):
    monkeypatch.setenv("SEED_DEMO_DATA", "0")
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    # No lifespan: the test database is created by the `session` fixture.
    return TestClient(app)
