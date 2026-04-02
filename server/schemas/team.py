from pydantic import BaseModel, Field


class OralistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    position: int = Field(ge=1, le=10, default=1)


class OralistRead(BaseModel):
    id: int
    team_id: int
    name: str
    position: int

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    team_code: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_\- ]+$")
    school_name: str = Field(min_length=1, max_length=300)
    contact_email: str = Field(default="", max_length=300)
    oralists: list[OralistCreate] = []


class TeamUpdate(BaseModel):
    team_code: str | None = Field(default=None, min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_\- ]+$")
    school_name: str | None = Field(default=None, min_length=1, max_length=300)
    contact_email: str | None = Field(default=None, max_length=300)


class TeamRead(BaseModel):
    id: int
    tournament_id: int
    team_code: str
    school_name: str
    contact_email: str
    oralists: list[OralistRead] = []

    model_config = {"from_attributes": True}
