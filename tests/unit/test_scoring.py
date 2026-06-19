"""Unit tests for point calculation and first-blood detection."""

import pytest

from app.scoring import calculate_points, is_first_blood


# --- calculate_points ---


def test_first_solve_awards_full_base_points():
    assert calculate_points(base_points=100, solve_order=1) == 100


def test_second_solve_awards_fewer_points_than_first():
    first = calculate_points(100, solve_order=1)
    second = calculate_points(100, solve_order=2)
    assert second < first


def test_points_decrease_monotonically_with_each_solve():
    scores = [calculate_points(100, order) for order in range(1, 6)]
    assert scores == sorted(scores, reverse=True)


def test_points_never_fall_below_minimum_of_ten_percent():
    # base=100 → min=10; after many solves, should stay at 10
    assert calculate_points(100, solve_order=1000) == 10


def test_solve_order_zero_raises_value_error():
    with pytest.raises(ValueError):
        calculate_points(100, solve_order=0)


def test_negative_solve_order_raises_value_error():
    with pytest.raises(ValueError):
        calculate_points(100, solve_order=-1)


def test_custom_decay_reduces_points_faster():
    default = calculate_points(100, solve_order=2, decay=10)
    fast_decay = calculate_points(100, solve_order=2, decay=30)
    assert fast_decay < default


def test_minimum_points_is_at_least_one_for_small_base():
    # base=5 → 5//10=0, so min is max(1, 0)=1
    assert calculate_points(5, solve_order=1000) >= 1


# --- is_first_blood ---


def test_solve_order_one_is_first_blood():
    assert is_first_blood(1) is True


def test_solve_order_two_is_not_first_blood():
    assert is_first_blood(2) is False


def test_high_solve_order_is_not_first_blood():
    assert is_first_blood(10) is False
