"""Unit tests for Pydantic request/response schema validation."""

import pytest
from pydantic import ValidationError

from app.schemas import ChallengeCreate, Difficulty, SubmissionCreate, TeamCreate


# --- ChallengeCreate ---


def test_valid_challenge_schema_is_accepted():
    data = ChallengeCreate(
        name="Web 101",
        description="Simple web challenge",
        flag="CTF{web_flag}",
        base_points=100,
    )
    assert data.name == "Web 101"
    assert data.base_points == 100


def test_challenge_with_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="", description="desc", flag="CTF{x}", base_points=100)


def test_challenge_with_zero_base_points_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=0)


def test_challenge_with_negative_base_points_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=-50)


def test_challenge_with_empty_flag_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="Test", description="desc", flag="", base_points=100)


def test_challenge_default_difficulty_is_medium():
    data = ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=100)
    assert data.difficulty == Difficulty.medium


def test_challenge_accepts_easy_difficulty():
    data = ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=100, difficulty="easy")
    assert data.difficulty == Difficulty.easy


def test_challenge_accepts_hard_difficulty():
    data = ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=100, difficulty="hard")
    assert data.difficulty == Difficulty.hard


def test_challenge_with_invalid_difficulty_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=100, difficulty="impossible")


def test_challenge_default_category_is_misc():
    data = ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=100)
    assert data.category == "misc"


# --- TeamCreate ---


def test_valid_team_schema_is_accepted():
    data = TeamCreate(name="Team Alpha")
    assert data.name == "Team Alpha"


def test_team_with_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        TeamCreate(name="")


def test_team_name_exceeding_max_length_is_rejected():
    with pytest.raises(ValidationError):
        TeamCreate(name="a" * 101)


# --- SubmissionCreate ---


def test_valid_submission_schema_is_accepted():
    data = SubmissionCreate(team_id=1, challenge_id=2, flag="CTF{flag}")
    assert data.team_id == 1
    assert data.challenge_id == 2
    assert data.flag == "CTF{flag}"


def test_submission_with_empty_flag_is_rejected():
    with pytest.raises(ValidationError):
        SubmissionCreate(team_id=1, challenge_id=1, flag="")


def test_challenge_with_base_points_above_maximum_is_rejected():
    with pytest.raises(ValidationError):
        ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=1001)


def test_challenge_with_base_points_at_maximum_is_accepted():
    data = ChallengeCreate(name="Test", description="desc", flag="CTF{x}", base_points=1000)
    assert data.base_points == 1000


def test_submission_with_non_positive_team_id_is_rejected():
    with pytest.raises(ValidationError):
        SubmissionCreate(team_id=0, challenge_id=1, flag="CTF{x}")
