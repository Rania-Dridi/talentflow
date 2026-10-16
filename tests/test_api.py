def create_job(client, **overrides):
    payload = {"title": "Data analyst", "department": "Data", "location": "Sfax", "skills": "sql, python", "openings": 1}
    payload.update(overrides)
    return client.post("/api/jobs", json=payload)


def test_create_and_list_jobs(client):
    created = create_job(client)
    assert created.status_code == 201
    assert created.json()["status"] == "open"
    assert len(client.get("/api/jobs").json()) == 1


def test_job_validation_rejects_short_title(client):
    assert create_job(client, title="x").status_code == 422


def test_candidate_flow_and_stats(client):
    job_id = create_job(client).json()["id"]
    res = client.post("/api/candidates", json={"job_id": job_id, "full_name": "Sara Test", "email": "SARA@Example.com", "skills": "sql, python", "years_experience": 3})
    assert res.status_code == 201
    candidate = res.json()
    assert candidate["email"] == "sara@example.com"
    assert candidate["score"] == 72

    moved = client.patch(f"/api/candidates/{candidate['id']}/stage", json={"stage": "interview"})
    assert moved.json()["stage"] == "interview"

    stats = client.get("/api/stats").json()
    assert stats["candidates"] == 1
    assert stats["funnel"][0]["count"] == 1  # cumulative funnel


def test_business_rules_are_returned_as_http_errors(client):
    job_id = create_job(client).json()["id"]
    candidate = client.post("/api/candidates", json={"job_id": job_id, "full_name": "Sara Test", "email": "s@example.com"}).json()
    hire = client.patch(f"/api/candidates/{candidate['id']}/stage", json={"stage": "hired"})
    assert hire.status_code == 409
    assert "offer" in hire.json()["detail"]
    assert client.patch("/api/candidates/999/stage", json={"stage": "offer"}).status_code == 404


def test_candidate_search_filters_by_skill(client):
    job_id = create_job(client).json()["id"]
    client.post("/api/candidates", json={"job_id": job_id, "full_name": "Sql Person", "email": "a@example.com", "skills": "sql"})
    client.post("/api/candidates", json={"job_id": job_id, "full_name": "Design Person", "email": "b@example.com", "skills": "figma"})
    found = client.get("/api/candidates", params={"q": "figma"}).json()
    assert [c["full_name"] for c in found] == ["Design Person"]
