from typing import Literal

from pydantic import BaseModel, Field


class ScoringCriterion(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    max_points: float = Field(gt=0, le=1000)
    weight: float = Field(gt=0, le=10, default=1.0)


PAIRING_METHODS = Literal["swiss", "random", "manual"]
WIN_DETERMINATIONS = Literal["ballot", "points"]
RANKING_METHODS = Literal["wins_then_points", "points_only"]
TIEBREAKER_KEYS = Literal["wins", "total_points", "opponent_wins", "head_to_head", "point_differential"]


class RulesetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    oralists_per_team: int = Field(ge=1, le=10, default=2)
    num_preliminary_rounds: int = Field(ge=1, le=20, default=4)
    judges_per_round: int = Field(ge=1, le=10, default=1)
    pairing_method: PAIRING_METHODS = "swiss"
    same_school_constraint: bool = True
    win_determination: WIN_DETERMINATIONS = "ballot"
    ranking_method: RANKING_METHODS = "wins_then_points"
    scoring_criteria: list[ScoringCriterion] = []
    ranking_tiebreakers: list[TIEBREAKER_KEYS] = []


class RulesetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    oralists_per_team: int | None = Field(default=None, ge=1, le=10)
    num_preliminary_rounds: int | None = Field(default=None, ge=1, le=20)
    judges_per_round: int | None = Field(default=None, ge=1, le=10)
    pairing_method: PAIRING_METHODS | None = None
    same_school_constraint: bool | None = None
    win_determination: WIN_DETERMINATIONS | None = None
    ranking_method: RANKING_METHODS | None = None
    scoring_criteria: list[ScoringCriterion] | None = None
    ranking_tiebreakers: list[TIEBREAKER_KEYS] | None = None


class RulesetRead(BaseModel):
    id: int
    name: str
    oralists_per_team: int
    num_preliminary_rounds: int
    judges_per_round: int
    pairing_method: str
    same_school_constraint: bool
    win_determination: str
    ranking_method: str
    scoring_criteria: list[ScoringCriterion]
    ranking_tiebreakers: list[str]

    model_config = {"from_attributes": True}
