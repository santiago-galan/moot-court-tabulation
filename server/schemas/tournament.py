from datetime import date

from pydantic import BaseModel

from server.schemas.ruleset import RulesetRead


class TournamentCreate(BaseModel):
    name: str
    event_date: date | None = None
    ruleset_id: int


class TournamentUpdate(BaseModel):
    name: str | None = None
    event_date: date | None = None
    status: str | None = None


class TournamentRead(BaseModel):
    id: int
    name: str
    event_date: date | None
    status: str
    ruleset_id: int
    ruleset: RulesetRead | None = None

    model_config = {"from_attributes": True}
