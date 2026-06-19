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
