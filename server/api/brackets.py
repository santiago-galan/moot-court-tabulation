from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.tournament import Tournament
from server.schemas.bracket import BracketCreate, BracketMatchRead
from server.services.bracket import generate_bracket, get_bracket_matches

router = APIRouter(prefix="/tournaments/{tournament_id}/bracket", tags=["brackets"])


@router.post("/", response_model=list[BracketMatchRead], status_code=201)
def create_bracket(tournament_id: int, payload: BracketCreate, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    try:
        matches = generate_bracket(tournament_id, payload.size, db)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    t.status = "elims"
    db.commit()
    return matches


@router.get("/", response_model=list[BracketMatchRead])
def get_bracket(tournament_id: int, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    return get_bracket_matches(tournament_id, db)
