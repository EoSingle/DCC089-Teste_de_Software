"""Unit tests for challenge-related service functions."""

import pytest

from app.exceptions import ConflictError
from app.flag_utils import hash_flag
from app.schemas import ChallengeCreate, Difficulty
from app.services import create_challenge, get_challenge_by_id, list_challenges


def test_get_challenge_by_id_returns_the_correct_challenge(db_session):
    data = ChallengeCreate(name="Crypto 101", description="Break the cipher", flag="CTF{x}", base_points=100)
    created = create_challenge(db_session, data)

    fetched = get_challenge_by_id(db_session, created.id)

    assert fetched.id == created.id
    assert fetched.name == "Crypto 101"


def test_get_challenge_by_id_raises_for_nonexistent_id(db_session):
    with pytest.raises(ValueError, match="not found"):
        get_challenge_by_id(db_session, 9999)


def test_get_challenge_with_stats_returns_zero_solve_count_initially(db_session):
    from app.services import get_challenge_with_stats

    data = ChallengeCreate(name="Unsolved", description="Not yet solved", flag="CTF{u}", base_points=50)
    created = create_challenge(db_session, data)

    detail = get_challenge_with_stats(db_session, created.id)

    assert detail.solve_count == 0


def test_create_challenge_stores_flag_as_hash_not_plaintext(db_session):
    data = ChallengeCreate(name="Hash Test", description="desc", flag="CTF{secret}", base_points=100)
    created = create_challenge(db_session, data)

    assert created.flag_hash == hash_flag("CTF{secret}")
    assert "CTF{secret}" not in created.flag_hash


def test_create_challenge_sets_default_difficulty_to_medium(db_session):
    data = ChallengeCreate(name="Default Diff", description="desc", flag="CTF{d}", base_points=100)
    created = create_challenge(db_session, data)

    assert created.difficulty == "medium"


def test_create_challenge_raises_conflict_for_duplicate_name(db_session):
    data = ChallengeCreate(name="Duplicate", description="desc", flag="CTF{d1}", base_points=100)
    create_challenge(db_session, data)

    with pytest.raises(ConflictError):
        create_challenge(db_session, ChallengeCreate(name="Duplicate", description="d2", flag="CTF{d2}", base_points=50))


def test_list_challenges_with_category_filter_returns_only_matching(db_session):
    create_challenge(db_session, ChallengeCreate(name="Web1", description="d", category="web", flag="CTF{w1}", base_points=100))
    create_challenge(db_session, ChallengeCreate(name="Pwn1", description="d", category="pwn", flag="CTF{p1}", base_points=100))

    results = list_challenges(db_session, category="web")

    assert len(results) == 1
    assert results[0].name == "Web1"


def test_get_challenge_with_stats_increments_solve_count_after_correct_submission(db_session):
    from app.schemas import SubmissionCreate, TeamCreate
    from app.services import create_team, get_challenge_with_stats, submit_flag

    ch = create_challenge(db_session, ChallengeCreate(name="Countable", description="d", flag="CTF{c}", base_points=100))
    team = create_team(db_session, TeamCreate(name="Solver"))
    submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{c}"))

    detail = get_challenge_with_stats(db_session, ch.id)

    assert detail.solve_count == 1


def test_get_challenge_by_id_preserves_all_fields(db_session):
    data = ChallengeCreate(
        name="Web 202",
        description="Find the hidden param",
        category="web",
        flag="CTF{web}",
        base_points=200,
    )
    created = create_challenge(db_session, data)

    fetched = get_challenge_by_id(db_session, created.id)

    assert fetched.category == "web"
    assert fetched.base_points == 200
    assert fetched.description == "Find the hidden param"
