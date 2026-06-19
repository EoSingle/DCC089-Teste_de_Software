SCORE_DECAY_PER_SOLVE = 10
FIRST_BLOOD_BONUS = 50


def calculate_points(base_points: int, solve_order: int, decay: int = SCORE_DECAY_PER_SOLVE) -> int:
    """
    Calculate points awarded for a solve.

    Points decrease by `decay` for each solve after the first.
    The minimum is max(1, base_points // 10) to keep challenges rewarding.

    Raises:
        ValueError: If solve_order < 1.
    """
    if solve_order < 1:
        raise ValueError(f"solve_order must be >= 1, got {solve_order}")
    min_points = max(1, base_points // 10)
    points = base_points - (solve_order - 1) * decay
    return max(points, min_points)


def is_first_blood(solve_order: int) -> bool:
    """Return True if this is the first team to solve the challenge."""
    return solve_order == 1
