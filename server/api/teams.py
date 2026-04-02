import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.ruleset import Ruleset
from server.models.team import Oralist, Team
from server.models.tournament import Tournament
from server.schemas.team import TeamCreate, TeamRead, TeamUpdate

router = APIRouter(prefix="/tournaments/{tournament_id}/teams", tags=["teams"])


def _get_tournament(tournament_id: int, db: Session) -> Tournament:
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    return t


@router.get("/", response_model=list[TeamRead])
def list_teams(tournament_id: int, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    return (
        db.query(Team)
        .filter(Team.tournament_id == tournament_id)
        .options(joinedload(Team.oralists))
        .all()
    )


@router.post("/", response_model=TeamRead, status_code=201)
def create_team(tournament_id: int, payload: TeamCreate, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    team = Team(
        tournament_id=tournament_id,
        team_code=payload.team_code,
        school_name=payload.school_name,
        contact_email=payload.contact_email,
    )
    db.add(team)
    db.flush()
    for o in payload.oralists:
        db.add(Oralist(team_id=team.id, name=o.name, position=o.position))
    db.commit()
    return db.query(Team).options(joinedload(Team.oralists)).get(team.id)


@router.post("/import", response_model=list[TeamRead], status_code=201)
async def import_teams_csv(
    tournament_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    tournament = _get_tournament(tournament_id, db)
    ruleset = db.get(Ruleset, tournament.ruleset_id)
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    created: list[Team] = []
    for row in reader:
        team = Team(
            tournament_id=tournament_id,
            team_code=row.get("team_code", "").strip(),
            school_name=row.get("school_name", "").strip(),
            contact_email=row.get("contact_email", "").strip(),
        )
        db.add(team)
        db.flush()
        for i in range(1, ruleset.oralists_per_team + 1):
            name = row.get(f"oralist_{i}", "").strip()
            if name:
                db.add(Oralist(team_id=team.id, name=name, position=i))
        created.append(team)
    db.commit()
    ids = [t.id for t in created]
    return db.query(Team).options(joinedload(Team.oralists)).filter(Team.id.in_(ids)).all()


@router.get("/{team_id}", response_model=TeamRead)
def get_team(tournament_id: int, team_id: int, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    team = db.query(Team).options(joinedload(Team.oralists)).get(team_id)
    if not team or team.tournament_id != tournament_id:
        raise HTTPException(404, "Team not found")
    return team


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(tournament_id: int, team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    team = db.get(Team, team_id)
    if not team or team.tournament_id != tournament_id:
        raise HTTPException(404, "Team not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(team, k, v)
    db.commit()
    return db.query(Team).options(joinedload(Team.oralists)).get(team.id)


@router.delete("/{team_id}", status_code=204)
def delete_team(tournament_id: int, team_id: int, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    team = db.get(Team, team_id)
    if not team or team.tournament_id != tournament_id:
        raise HTTPException(404, "Team not found")
    db.delete(team)
    db.commit()
