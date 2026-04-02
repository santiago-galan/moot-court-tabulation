from datetime import datetime

from pydantic import BaseModel


class OralistScoreEntry(BaseModel):
    oralist_id: int
    criterion_name: str
    score: float


class BallotSubmission(BaseModel):
    winner_team_id: int | None = None
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
