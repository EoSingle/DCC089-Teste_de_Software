from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas, services
from app.database import get_db
from app.exceptions import ConflictError

router = APIRouter()


@router.post("/challenges", response_model=schemas.ChallengeResponse, status_code=201)
def create_challenge(data: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    try:
        return services.create_challenge(db, data)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/challenges/{challenge_id}", response_model=schemas.ChallengeDetailResponse)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_challenge_with_stats(db, challenge_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/challenges", response_model=list[schemas.ChallengeResponse])
def list_challenges(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    return services.list_challenges(db, category=category)


@router.get("/teams/{team_id}", response_model=schemas.TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_team_by_id(db, team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/teams", response_model=list[schemas.TeamResponse])
def list_teams(db: Session = Depends(get_db)):
    return services.list_teams(db)


@router.post("/teams", response_model=schemas.TeamResponse, status_code=201)
def create_team(data: schemas.TeamCreate, db: Session = Depends(get_db)):
    try:
        return services.create_team(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/teams/{team_id}/solves", response_model=schemas.TeamSolvesResponse)
def get_team_solves(team_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_team_solves(db, team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/submissions", response_model=schemas.SubmissionResult)
def submit_flag(data: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    try:
        return services.submit_flag(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/scoreboard", response_model=schemas.ScoreboardResponse)
def get_scoreboard(db: Session = Depends(get_db)):
    return services.get_scoreboard(db)
