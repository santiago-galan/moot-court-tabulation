from typing import Literal

from pydantic import BaseModel


class BracketCreate(BaseModel):
    size: Literal[8, 16, 32] = 8


class BracketMatchRead(BaseModel):
    pairing_id: int
    round_number: int
    elim_level: str
    petitioner_team_id: int | None = None
    respondent_team_id: int | None = None
    petitioner_team_code: str = ""
    respondent_team_code: str = ""
    winner_team_id: int | None = None
    status: str = "pending"
