"""Unit tests for flag submission service logic."""

import pytest

from app.schemas import ChallengeCreate, SubmissionCreate, TeamCreate
from app.services import create_challenge, create_team, submit_flag


def _make_challenge(db, name="Web 101", flag="CTF{flag}", points=100):
    return create_challenge(db, ChallengeCreate(name=name, description="d", flag=flag, base_points=points))


def _make_team(db, name="Alpha"):
    return create_team(db, TeamCreate(name=name))


def test_submit_correct_flag_returns_correct_true(db_session):
    ch = _make_challenge(db_session, flag="CTF{ok}")
    team = _make_team(db_session)

    result = submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{ok}"))

    assert result.correct is True


def test_submit_correct_flag_awards_nonzero_points(db_session):
    ch = _make_challenge(db_session, flag="CTF{pts}", points=100)
    team = _make_team(db_session)

    result = submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{pts}"))

    assert result.points_awarded > 0


def test_submit_wrong_flag_returns_correct_false(db_session):
    ch = _make_challenge(db_session, flag="CTF{real}")
    team = _make_team(db_session)

    result = submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{wrong}"))

    assert result.correct is False


def test_submit_wrong_flag_awards_zero_points(db_session):
    ch = _make_challenge(db_session, flag="CTF{real}")
    team = _make_team(db_session)

    result = submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{wrong}"))

    assert result.points_awarded == 0


def test_submit_wrong_flag_does_not_change_team_score(db_session):
    ch = _make_challenge(db_session, flag="CTF{real}")
    team = _make_team(db_session)

    submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{wrong}"))

    db_session.refresh(team)
    assert team.score == 0


def test_first_submission_receives_first_blood_bonus(db_session):
    from app.scoring import FIRST_BLOOD_BONUS
    ch = _make_challenge(db_session, flag="CTF{fb}", points=100)
    team = _make_team(db_session)

    result = submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{fb}"))

    assert result.points_awarded == 100 + FIRST_BLOOD_BONUS
    assert "First blood" in result.message


def test_second_team_submission_does_not_receive_first_blood_bonus(db_session):
    from app.scoring import FIRST_BLOOD_BONUS
    ch = _make_challenge(db_session, flag="CTF{nfb}", points=100)
    team1 = _make_team(db_session, name="First")
    team2 = _make_team(db_session, name="Second")

    submit_flag(db_session, SubmissionCreate(team_id=team1.id, challenge_id=ch.id, flag="CTF{nfb}"))
    result = submit_flag(db_session, SubmissionCreate(team_id=team2.id, challenge_id=ch.id, flag="CTF{nfb}"))

    assert result.points_awarded < 100 + FIRST_BLOOD_BONUS


def test_submit_correct_flag_increases_team_score(db_session):
    ch = _make_challenge(db_session, flag="CTF{score}")
    team = _make_team(db_session)

    submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch.id, flag="CTF{score}"))

    db_session.refresh(team)
    assert team.score > 0
