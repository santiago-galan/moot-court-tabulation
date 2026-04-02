import csv
import io
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.ruleset import Ruleset
from server.models.team import Oralist, Team
from server.models.tournament import Tournament
from server.schemas.team import TeamCreate, TeamRead, TeamUpdate

router = APIRouter(prefix="/tournaments/{tournament_id}/teams", tags=["teams"])

_TEAM_CODE_RE = re.compile(r"^[A-Za-z0-9_\- ]+$")
_MAX_CSV_ROWS = 500
_MAX_CSV_BYTES = 2 * 1024 * 1024  # 2 MB


def _get_tournament(tournament_id: int, db: Session) -> Tournament:
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    return t


def _check_duplicate_code(tournament_id: int, team_code: str, db: Session, exclude_id: int | None = None):
    query = db.query(Team).filter(Team.tournament_id == tournament_id, Team.team_code == team_code)
    if exclude_id:
        query = query.filter(Team.id != exclude_id)
    if query.first():
        raise HTTPException(409, f"Team code '{team_code}' already exists in this tournament")


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
    _check_duplicate_code(tournament_id, payload.team_code, db)
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

    raw = await file.read()
    if len(raw) > _MAX_CSV_BYTES:
        raise HTTPException(400, f"CSV file too large (max {_MAX_CSV_BYTES // 1024} KB)")
    content = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    created: list[Team] = []
    seen_codes: set[str] = set()
    for row_num, row in enumerate(reader, start=2):
        if row_num - 1 > _MAX_CSV_ROWS:
            raise HTTPException(400, f"CSV exceeds maximum of {_MAX_CSV_ROWS} rows")

        team_code = row.get("team_code", "").strip()[:50]
        school_name = row.get("school_name", "").strip()[:300]
        contact_email = row.get("contact_email", "").strip()[:300]

        if not team_code or not school_name:
            raise HTTPException(400, f"Row {row_num}: team_code and school_name are required")
        if not _TEAM_CODE_RE.match(team_code):
            raise HTTPException(400, f"Row {row_num}: team_code contains invalid characters")
        if team_code in seen_codes:
            raise HTTPException(400, f"Row {row_num}: duplicate team_code '{team_code}' in CSV")
        _check_duplicate_code(tournament_id, team_code, db)
        seen_codes.add(team_code)

        team = Team(
            tournament_id=tournament_id,
            team_code=team_code,
            school_name=school_name,
            contact_email=contact_email,
        )
        db.add(team)
        db.flush()
        for i in range(1, ruleset.oralists_per_team + 1):
            name = row.get(f"oralist_{i}", "").strip()[:200]
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
    if payload.team_code is not None:
        _check_duplicate_code(tournament_id, payload.team_code, db, exclude_id=team_id)
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
