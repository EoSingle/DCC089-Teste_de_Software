"""Unit tests for team-related service functions."""

import pytest

from app.exceptions import ConflictError
from app.schemas import TeamCreate
from app.services import create_team, get_team_by_id, list_teams


def test_get_team_by_id_returns_the_correct_team(db_session):
    data = TeamCreate(name="Team Rocket")
    created = create_team(db_session, data)

    fetched = get_team_by_id(db_session, created.id)

    assert fetched.id == created.id
    assert fetched.name == "Team Rocket"


def test_get_team_by_id_raises_for_nonexistent_id(db_session):
    with pytest.raises(ValueError, match="not found"):
        get_team_by_id(db_session, 9999)


def test_list_teams_returns_all_teams(db_session):
    create_team(db_session, TeamCreate(name="Alpha"))
    create_team(db_session, TeamCreate(name="Beta"))

    teams = list_teams(db_session)

    assert len(teams) == 2
    names = {t.name for t in teams}
    assert names == {"Alpha", "Beta"}


def test_create_team_initializes_score_to_zero(db_session):
    team = create_team(db_session, TeamCreate(name="Zero Score"))

    assert team.score == 0


def test_create_team_raises_conflict_for_duplicate_name(db_session):
    create_team(db_session, TeamCreate(name="Taken"))

    with pytest.raises(ConflictError):
        create_team(db_session, TeamCreate(name="Taken"))


def test_list_teams_returns_empty_list_when_no_teams_exist(db_session):
    assert list_teams(db_session) == []


def test_scoreboard_ranks_higher_scoring_team_first(db_session):
    from app.schemas import ChallengeCreate, SubmissionCreate
    from app.services import create_challenge, get_scoreboard, submit_flag

    ch = create_challenge(db_session, ChallengeCreate(name="Rank Ch", description="d", flag="CTF{r}", base_points=100))
    low = create_team(db_session, TeamCreate(name="LowRank"))
    high = create_team(db_session, TeamCreate(name="HighRank"))

    submit_flag(db_session, SubmissionCreate(team_id=high.id, challenge_id=ch.id, flag="CTF{r}"))

    entries = get_scoreboard(db_session).entries
    assert entries[0].team_name == "HighRank"
    assert entries[1].team_name == "LowRank"


def test_scoreboard_returns_empty_entries_when_no_teams_exist(db_session):
    from app.services import get_scoreboard

    scoreboard = get_scoreboard(db_session)

    assert scoreboard.entries == []


def test_scoreboard_total_solves_is_zero_for_team_with_no_solves(db_session):
    from app.services import create_team, get_scoreboard
    create_team(db_session, TeamCreate(name="No Solves"))

    scoreboard = get_scoreboard(db_session)

    assert scoreboard.entries[0].total_solves == 0


def test_scoreboard_total_solves_reflects_correct_submissions(db_session):
    from app.schemas import ChallengeCreate, SubmissionCreate
    from app.services import create_challenge, create_team, get_scoreboard, submit_flag

    team = create_team(db_session, TeamCreate(name="Solver"))
    ch1 = create_challenge(db_session, ChallengeCreate(name="Ch1", description="d", flag="CTF{1}", base_points=100))
    ch2 = create_challenge(db_session, ChallengeCreate(name="Ch2", description="d", flag="CTF{2}", base_points=100))

    submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch1.id, flag="CTF{1}"))
    submit_flag(db_session, SubmissionCreate(team_id=team.id, challenge_id=ch2.id, flag="CTF{2}"))

    scoreboard = get_scoreboard(db_session)

    assert scoreboard.entries[0].total_solves == 2
