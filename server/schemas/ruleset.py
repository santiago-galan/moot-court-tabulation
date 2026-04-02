from pydantic import BaseModel


class ScoringCriterion(BaseModel):
    name: str
    max_points: float
    weight: float = 1.0


class RulesetCreate(BaseModel):
    name: str
    oralists_per_team: int = 2
    num_preliminary_rounds: int = 4
    judges_per_round: int = 1
    pairing_method: str = "swiss"
    same_school_constraint: bool = True
    win_determination: str = "ballot"
    ranking_method: str = "wins_then_points"
    scoring_criteria: list[ScoringCriterion] = []
    ranking_tiebreakers: list[str] = []


class RulesetUpdate(BaseModel):
    name: str | None = None
    oralists_per_team: int | None = None
    num_preliminary_rounds: int | None = None
    judges_per_round: int | None = None
    pairing_method: str | None = None
    same_school_constraint: bool | None = None
    win_determination: str | None = None
    ranking_method: str | None = None
    scoring_criteria: list[ScoringCriterion] | None = None
    ranking_tiebreakers: list[str] | None = None


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
