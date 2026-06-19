"""Unit tests for database module setup."""

import inspect


def test_database_base_contains_challenges_table():
    from app.database import Base
    assert "challenges" in Base.metadata.tables


def test_database_base_contains_teams_table():
    from app.database import Base
    assert "teams" in Base.metadata.tables


def test_database_base_contains_submissions_table():
    from app.database import Base
    assert "submissions" in Base.metadata.tables


def test_get_db_is_a_generator_function():
    from app.database import get_db
    assert inspect.isgeneratorfunction(get_db)
