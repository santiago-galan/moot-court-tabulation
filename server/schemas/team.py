from pydantic import BaseModel


class OralistCreate(BaseModel):
    name: str
    position: int = 1


class OralistRead(BaseModel):
    id: int
    team_id: int
    name: str
    position: int

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    team_code: str
    school_name: str
    contact_email: str = ""
    oralists: list[OralistCreate] = []


class TeamUpdate(BaseModel):
    team_code: str | None = None
    school_name: str | None = None
    contact_email: str | None = None


class TeamRead(BaseModel):
    id: int
    tournament_id: int
    team_code: str
    school_name: str
    contact_email: str
    oralists: list[OralistRead] = []

    model_config = {"from_attributes": True}
