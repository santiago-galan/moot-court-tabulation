from datetime import datetime

from pydantic import BaseModel, Field


class OralistScoreEntry(BaseModel):
    oralist_id: int = Field(gt=0)
    criterion_name: str = Field(min_length=1, max_length=200)
    score: float = Field(ge=0, le=1000)


class BallotSubmission(BaseModel):
    winner_team_id: int | None = Field(default=None, gt=0)
    scores: list[OralistScoreEntry] = []


class OralistScoreRead(BaseModel):
    id: int
    oralist_id: int
    criterion_name: str
    score: float

    model_config = {"from_attributes": True}


class BallotRead(BaseModel):
    id: int
    judge_assignment_id: int
    winner_team_id: int | None
    submitted: bool
    submitted_at: datetime | None
    scores: list[OralistScoreRead] = []

    model_config = {"from_attributes": True}


class TeamStanding(BaseModel):
    team_id: int
    team_code: str
    school_name: str
    wins: int = 0
    losses: int = 0
    total_points: float = 0.0
    opponent_wins: int = 0
    point_differential: float = 0.0
    rank: int = 0
