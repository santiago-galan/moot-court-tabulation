from pydantic import BaseModel


class JudgeAssignmentCreate(BaseModel):
    judge_name: str


class JudgeAssignmentRead(BaseModel):
    id: int
    pairing_id: int
    judge_name: str
    access_code: str

    model_config = {"from_attributes": True}


class PairingCreate(BaseModel):
    petitioner_team_id: int
    respondent_team_id: int
    room: str = ""
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
    round_type: str = "preliminary"
    elim_level: str | None = None


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
