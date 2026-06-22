"""Integration tests for the CTF Platform HTTP API.

Each test exercises a complete user flow through the HTTP layer using a
dedicated in-memory SQLite database, keeping tests fully independent.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_challenge(client, *, name="Crypto 101", flag="CTF{secret}", points=100):
    resp = client.post(
        "/api/v1/challenges",
        json={"name": name, "description": "A test challenge", "flag": flag, "base_points": points},
    )
    assert resp.status_code == 201
    return resp.json()


def _create_team(client, *, name="Team Alpha"):
    resp = client.post("/api/v1/teams", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


def _submit(client, *, team_id, challenge_id, flag):
    return client.post(
        "/api/v1/submissions",
        json={"team_id": team_id, "challenge_id": challenge_id, "flag": flag},
    )


# ---------------------------------------------------------------------------
# Test 1 — creating a challenge persists it and returns its data
# ---------------------------------------------------------------------------


def test_cors_headers_are_present_in_api_response(client):
    resp = client.get("/api/v1/health", headers={"Origin": "http://example.com"})

    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers


def test_health_endpoint_returns_ok_with_connected_database(client):
    resp = client.get("/api/v1/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


def test_create_challenge_returns_persisted_resource(client):
    resp = client.post(
        "/api/v1/challenges",
        json={
            "name": "Web 101",
            "description": "Inspect the HTTP headers",
            "category": "web",
            "flag": "CTF{hidden_header}",
            "base_points": 200,
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Web 101"
    assert body["category"] == "web"
    assert body["base_points"] == 200
    assert "id" in body
    # Flag must NOT be returned in plaintext
    assert "flag" not in body


# ---------------------------------------------------------------------------
# Test 2 — submitting the correct flag awards points and marks as correct
# ---------------------------------------------------------------------------


def test_correct_flag_submission_awards_points_and_first_blood_bonus(client):
    challenge = _create_challenge(client, flag="CTF{correct}", points=100)
    team = _create_team(client)

    resp = _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{correct}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is True
    # First solve = 100 base + 50 first-blood bonus
    assert body["points_awarded"] == 150
    assert "First blood" in body["message"]


# ---------------------------------------------------------------------------
# Test 3 — submitting the wrong flag awards zero points
# ---------------------------------------------------------------------------


def test_wrong_flag_submission_is_rejected_with_zero_points(client):
    challenge = _create_challenge(client, flag="CTF{real_flag}")
    team = _create_team(client)

    resp = _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{wrong}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is False
    assert body["points_awarded"] == 0


# ---------------------------------------------------------------------------
# Test 4 — a team that already solved a challenge gets zero points on re-submit
# ---------------------------------------------------------------------------


def test_duplicate_submission_by_same_team_awards_zero_points(client):
    challenge = _create_challenge(client, flag="CTF{once}")
    team = _create_team(client)

    first = _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{once}")
    assert first.json()["correct"] is True

    second = _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{once}")
    body = second.json()
    assert body["correct"] is True
    assert body["points_awarded"] == 0
    assert "already solved" in body["message"]


# ---------------------------------------------------------------------------
# Test 5 — scoreboard reflects team scores in descending order
# ---------------------------------------------------------------------------


def test_submission_with_nonexistent_challenge_returns_404(client):
    team = _create_team(client)

    resp = _submit(client, team_id=team["id"], challenge_id=9999, flag="CTF{x}")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_submission_with_nonexistent_team_returns_404(client):
    challenge = _create_challenge(client, flag="CTF{x}")

    resp = _submit(client, team_id=9999, challenge_id=challenge["id"], flag="CTF{x}")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_duplicate_team_name_returns_409(client):
    _create_team(client, name="Unique Team")

    resp = client.post("/api/v1/teams", json={"name": "Unique Team"})

    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_duplicate_challenge_name_returns_409(client):
    _create_challenge(client, name="Unique Challenge", flag="CTF{u1}")

    resp = client.post(
        "/api/v1/challenges",
        json={"name": "Unique Challenge", "description": "desc", "flag": "CTF{u2}", "base_points": 50},
    )

    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_category_filter_returns_only_matching_challenges(client):
    client.post(
        "/api/v1/challenges",
        json={"name": "Web 101", "description": "desc", "category": "web", "flag": "CTF{w1}", "base_points": 100},
    )
    client.post(
        "/api/v1/challenges",
        json={"name": "Pwn 101", "description": "desc", "category": "pwn", "flag": "CTF{p1}", "base_points": 100},
    )

    resp = client.get("/api/v1/challenges?category=web")

    assert resp.status_code == 200
    results = resp.json()
    assert all(c["category"] == "web" for c in results)
    assert any(c["name"] == "Web 101" for c in results)
    assert not any(c["name"] == "Pwn 101" for c in results)


def test_list_teams_returns_all_created_teams(client):
    _create_team(client, name="Alpha")
    _create_team(client, name="Beta")

    resp = client.get("/api/v1/teams")

    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert "Alpha" in names
    assert "Beta" in names


def test_team_solves_endpoint_returns_correct_solve_history(client):
    challenge = _create_challenge(client, name="Rev 101", flag="CTF{rev}", points=100)
    team = _create_team(client, name="Hackers")
    _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{rev}")

    resp = client.get(f"/api/v1/teams/{team['id']}/solves")

    assert resp.status_code == 200
    body = resp.json()
    assert body["team_name"] == "Hackers"
    assert len(body["solves"]) == 1
    assert body["solves"][0]["challenge_name"] == "Rev 101"
    assert body["solves"][0]["points_awarded"] > 0


def test_team_solves_is_empty_before_any_submission(client):
    team = _create_team(client, name="Fresh Team")

    resp = client.get(f"/api/v1/teams/{team['id']}/solves")

    assert resp.status_code == 200
    assert resp.json()["solves"] == []


def test_scoreboard_pagination_limits_number_of_entries(client):
    for i in range(5):
        _create_team(client, name=f"Team {i}")

    resp = client.get("/api/v1/scoreboard?limit=2&offset=0")

    assert resp.status_code == 200
    assert len(resp.json()["entries"]) == 2


def test_scoreboard_pagination_offset_adjusts_rank(client):
    _create_team(client, name="Team A")
    _create_team(client, name="Team B")
    _create_team(client, name="Team C")

    resp = client.get("/api/v1/scoreboard?limit=2&offset=1")

    entries = resp.json()["entries"]
    assert entries[0]["rank"] == 2


def test_scoreboard_orders_teams_by_score_descending(client):
    challenge_a = _create_challenge(client, name="Pwn 1", flag="CTF{pwn1}", points=200)
    challenge_b = _create_challenge(client, name="Pwn 2", flag="CTF{pwn2}", points=100)

    team_low = _create_team(client, name="LowScore")
    team_high = _create_team(client, name="HighScore")

    # LowScore solves only the 100-pt challenge (second, no first-blood on it)
    _submit(client, team_id=team_high["id"], challenge_id=challenge_a["id"], flag="CTF{pwn1}")
    _submit(client, team_id=team_high["id"], challenge_id=challenge_b["id"], flag="CTF{pwn2}")
    _submit(client, team_id=team_low["id"], challenge_id=challenge_b["id"], flag="CTF{pwn2}")

    resp = client.get("/api/v1/scoreboard")
    assert resp.status_code == 200
    entries = resp.json()["entries"]

    assert entries[0]["team_name"] == "HighScore"
    assert entries[1]["team_name"] == "LowScore"
    assert entries[0]["score"] > entries[1]["score"]
    assert entries[0]["rank"] == 1
    assert entries[1]["rank"] == 2


# ---------------------------------------------------------------------------
# GET /api/v1/challenges/{id} — previously had no integration coverage at all
# ---------------------------------------------------------------------------


def test_get_challenge_detail_returns_full_challenge_with_solve_count(client):
    challenge = _create_challenge(client, name="Forensics 101", flag="CTF{forensics}", points=150)
    team = _create_team(client, name="Investigators")
    _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{forensics}")

    resp = client.get(f"/api/v1/challenges/{challenge['id']}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == challenge["id"]
    assert body["name"] == "Forensics 101"
    assert body["base_points"] == 150
    assert body["solve_count"] == 1
    # Flag must NOT be exposed by the detail endpoint either
    assert "flag" not in body


def test_get_challenge_detail_solve_count_is_zero_before_any_submission(client):
    challenge = _create_challenge(client, name="Unsolved Detail", flag="CTF{unsolved}")

    resp = client.get(f"/api/v1/challenges/{challenge['id']}")

    assert resp.status_code == 200
    assert resp.json()["solve_count"] == 0


def test_get_nonexistent_challenge_returns_404(client):
    resp = client.get("/api/v1/challenges/9999")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# GET /api/v1/teams/{id} — previously had no integration coverage at all
# ---------------------------------------------------------------------------


def test_get_team_detail_returns_team_data(client):
    team = _create_team(client, name="Detail Team")

    resp = client.get(f"/api/v1/teams/{team['id']}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == team["id"]
    assert body["name"] == "Detail Team"
    assert body["score"] == 0


def test_get_team_detail_reflects_score_after_a_correct_submission(client):
    challenge = _create_challenge(client, name="Score Detail", flag="CTF{score_detail}", points=100)
    team = _create_team(client, name="Scorer")
    _submit(client, team_id=team["id"], challenge_id=challenge["id"], flag="CTF{score_detail}")

    resp = client.get(f"/api/v1/teams/{team['id']}")

    assert resp.status_code == 200
    assert resp.json()["score"] > 0


def test_get_nonexistent_team_returns_404(client):
    resp = client.get("/api/v1/teams/9999")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# GET /api/v1/teams/{id}/solves — 404 path was not covered
# ---------------------------------------------------------------------------


def test_team_solves_for_nonexistent_team_returns_404(client):
    resp = client.get("/api/v1/teams/9999/solves")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Root-level health check exposed directly by app.main (no /api/v1 prefix)
# ---------------------------------------------------------------------------


def test_root_health_endpoint_returns_ok_status(client):
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
