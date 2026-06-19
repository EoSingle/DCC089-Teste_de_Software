"""Unit tests for team-related service functions."""

import pytest

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


def test_list_teams_returns_empty_list_when_no_teams_exist(db_session):
    assert list_teams(db_session) == []
