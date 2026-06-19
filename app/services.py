from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import ConflictError
from app.flag_utils import hash_flag, validate_flag
from app.scoring import FIRST_BLOOD_BONUS, calculate_points, is_first_blood


def _get_solve_order(db: Session, challenge_id: int) -> int:
    """Return 1-indexed position of the next correct solve for a challenge."""
    count = (
        db.query(models.Submission)
        .filter(
            models.Submission.challenge_id == challenge_id,
            models.Submission.is_correct == True,
        )
        .count()
    )
    return count + 1


def _has_team_solved(db: Session, team_id: int, challenge_id: int) -> bool:
    """Return True if the team already has a correct submission for this challenge."""
    return (
        db.query(models.Submission)
        .filter(
            models.Submission.team_id == team_id,
            models.Submission.challenge_id == challenge_id,
            models.Submission.is_correct == True,
        )
        .first()
        is not None
    )


def create_challenge(db: Session, data: schemas.ChallengeCreate) -> models.Challenge:
    if db.query(models.Challenge).filter(models.Challenge.name == data.name).first():
        raise ConflictError(f"A challenge named '{data.name}' already exists")
    challenge = models.Challenge(
        name=data.name,
        description=data.description,
        category=data.category,
        flag_hash=hash_flag(data.flag),
        base_points=data.base_points,
        difficulty=data.difficulty.value,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def get_challenge_by_id(db: Session, challenge_id: int) -> models.Challenge:
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not challenge:
        raise ValueError(f"Challenge {challenge_id} not found")
    return challenge


def get_challenge_with_stats(db: Session, challenge_id: int) -> schemas.ChallengeDetailResponse:
    challenge = get_challenge_by_id(db, challenge_id)
    solve_count = (
        db.query(models.Submission)
        .filter(models.Submission.challenge_id == challenge_id, models.Submission.is_correct == True)
        .count()
    )
    return schemas.ChallengeDetailResponse(
        id=challenge.id,
        name=challenge.name,
        description=challenge.description,
        category=challenge.category,
        base_points=challenge.base_points,
        difficulty=challenge.difficulty,
        solve_count=solve_count,
    )


def list_challenges(db: Session, category: str | None = None) -> list[models.Challenge]:
    query = db.query(models.Challenge)
    if category:
        query = query.filter(models.Challenge.category == category)
    return query.all()


def list_teams(db: Session) -> list[models.Team]:
    return db.query(models.Team).all()


def get_team_by_id(db: Session, team_id: int) -> models.Team:
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise ValueError(f"Team {team_id} not found")
    return team


def create_team(db: Session, data: schemas.TeamCreate) -> models.Team:
    if db.query(models.Team).filter(models.Team.name == data.name).first():
        raise ConflictError(f"A team named '{data.name}' already exists")
    team = models.Team(name=data.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def submit_flag(db: Session, data: schemas.SubmissionCreate) -> schemas.SubmissionResult:
    team = db.query(models.Team).filter(models.Team.id == data.team_id).first()
    if not team:
        raise ValueError(f"Team {data.team_id} not found")

    challenge = db.query(models.Challenge).filter(models.Challenge.id == data.challenge_id).first()
    if not challenge:
        raise ValueError(f"Challenge {data.challenge_id} not found")

    if _has_team_solved(db, data.team_id, data.challenge_id):
        return schemas.SubmissionResult(
            correct=True,
            points_awarded=0,
            message="Your team has already solved this challenge.",
        )

    is_correct = validate_flag(data.flag, challenge.flag_hash)
    points = 0
    message = "Wrong flag. Try again!"

    if is_correct:
        solve_order = _get_solve_order(db, data.challenge_id)
        points = calculate_points(challenge.base_points, solve_order)
        if is_first_blood(solve_order):
            points += FIRST_BLOOD_BONUS
            message = f"Correct! First blood! You earned {points} points."
        else:
            message = f"Correct! You earned {points} points."
        team.score += points

    submission = models.Submission(
        team_id=data.team_id,
        challenge_id=data.challenge_id,
        is_correct=is_correct,
        points_awarded=points,
    )
    db.add(submission)
    db.commit()

    return schemas.SubmissionResult(correct=is_correct, points_awarded=points, message=message)


def get_team_solves(db: Session, team_id: int) -> schemas.TeamSolvesResponse:
    team = get_team_by_id(db, team_id)
    submissions = (
        db.query(models.Submission)
        .filter(models.Submission.team_id == team_id, models.Submission.is_correct == True)
        .all()
    )
    solves = [
        schemas.SolveEntry(
            challenge_id=s.challenge_id,
            challenge_name=s.challenge.name,
            points_awarded=s.points_awarded,
        )
        for s in submissions
    ]
    return schemas.TeamSolvesResponse(team_id=team.id, team_name=team.name, solves=solves)


def get_scoreboard(db: Session, limit: int = 50, offset: int = 0) -> schemas.ScoreboardResponse:
    teams = (
        db.query(models.Team)
        .order_by(models.Team.score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    entries = []
    for i, team in enumerate(teams):
        total_solves = (
            db.query(models.Submission)
            .filter(models.Submission.team_id == team.id, models.Submission.is_correct == True)
            .count()
        )
        entries.append(
            schemas.ScoreboardEntry(
                rank=offset + i + 1,
                team_name=team.name,
                score=team.score,
                total_solves=total_solves,
            )
        )
    return schemas.ScoreboardResponse(entries=entries)
