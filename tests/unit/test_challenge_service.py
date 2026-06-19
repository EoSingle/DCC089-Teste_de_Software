"""Unit tests for challenge-related service functions."""

import pytest

from app.schemas import ChallengeCreate
from app.services import create_challenge, get_challenge_by_id


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
