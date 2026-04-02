from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from server.schemas.ruleset import RulesetRead

TOURNAMENT_STATUSES = Literal["setup", "prelims", "elims", "completed"]


class TournamentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    event_date: date | None = None
    ruleset_id: int = Field(gt=0)


class TournamentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=300)
    event_date: date | None = None
    status: TOURNAMENT_STATUSES | None = None


class TournamentRead(BaseModel):
    id: int
    name: str
    event_date: date | None
    status: str
    ruleset_id: int
    ruleset: RulesetRead | None = None

    model_config = {"from_attributes": True}
