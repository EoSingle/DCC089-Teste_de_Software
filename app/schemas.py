from pydantic import BaseModel, Field


class ChallengeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(default="misc", max_length=50)
    flag: str = Field(..., min_length=1)
    base_points: int = Field(..., gt=0, le=1000)


class ChallengeResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    base_points: int

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class TeamResponse(BaseModel):
    id: int
    name: str
    score: int

    model_config = {"from_attributes": True}


class SubmissionCreate(BaseModel):
    team_id: int = Field(..., gt=0)
    challenge_id: int = Field(..., gt=0)
    flag: str = Field(..., min_length=1)


class SubmissionResult(BaseModel):
    correct: bool
    points_awarded: int
    message: str


class ChallengeDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    base_points: int
    solve_count: int


class SolveEntry(BaseModel):
    challenge_id: int
    challenge_name: str
    points_awarded: int


class TeamSolvesResponse(BaseModel):
    team_id: int
    team_name: str
    solves: list[SolveEntry]


class ScoreboardEntry(BaseModel):
    rank: int
    team_name: str
    score: int
    total_solves: int


class ScoreboardResponse(BaseModel):
    entries: list[ScoreboardEntry]
