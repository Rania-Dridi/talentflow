from app.seed import seed_demo_data


def test_pages_render_with_demo_data(client, session):
    seed_demo_data(session)
    for path in ("/", "/board", "/jobs", "/board?job_id=2"):
        response = client.get(path)
        assert response.status_code == 200, path
    assert "Entonnoir de recrutement" in client.get("/").text


def test_seed_is_idempotent(session):
    seed_demo_data(session)
    seed_demo_data(session)
    from app.repositories import JobRepository

    assert len(JobRepository(session).list()) == 5


def test_pages_render_on_empty_database(client):
    assert client.get("/").status_code == 200
    assert client.get("/board").status_code == 200
