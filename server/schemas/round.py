from typing import Literal

from pydantic import BaseModel, Field

ROUND_TYPES = Literal["preliminary", "elimination"]
ROUND_STATUSES = Literal["pending", "in_progress", "completed"]


class JudgeAssignmentCreate(BaseModel):
    judge_name: str = Field(max_length=200, default="")


class JudgeAssignmentRead(BaseModel):
    id: int
    pairing_id: int
    judge_name: str
    access_code: str

    model_config = {"from_attributes": True}


class PairingCreate(BaseModel):
    petitioner_team_id: int = Field(gt=0)
    respondent_team_id: int = Field(gt=0)
    room: str = Field(default="", max_length=100)
    judges: list[JudgeAssignmentCreate] = []


class PairingRead(BaseModel):
    id: int
    round_id: int
    petitioner_team_id: int
    respondent_team_id: int
    room: str
    status: str

    model_config = {"from_attributes": True}


class PairingDetail(PairingRead):
    petitioner_team_code: str = ""
    respondent_team_code: str = ""
    petitioner_school: str = ""
    respondent_school: str = ""
    judge_assignments: list[JudgeAssignmentRead] = []


class RoundCreate(BaseModel):
    round_type: ROUND_TYPES = "preliminary"
    elim_level: str | None = Field(default=None, max_length=20)


class RoundRead(BaseModel):
    id: int
    tournament_id: int
    round_number: int
    round_type: str
    elim_level: str | None
    status: str

    model_config = {"from_attributes": True}


class RoundDetail(RoundRead):
    pairings: list[PairingDetail] = []
