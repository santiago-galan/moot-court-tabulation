from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.ruleset import Ruleset
from server.models.tournament import Tournament
from server.schemas.tournament import TournamentCreate, TournamentRead, TournamentUpdate

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("/", response_model=list[TournamentRead])
def list_tournaments(db: Session = Depends(get_db)):
    return db.query(Tournament).options(joinedload(Tournament.ruleset)).all()


@router.post("/", response_model=TournamentRead, status_code=201)
def create_tournament(payload: TournamentCreate, db: Session = Depends(get_db)):
    if not db.get(Ruleset, payload.ruleset_id):
        raise HTTPException(400, "Ruleset not found")
    tournament = Tournament(**payload.model_dump())
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return db.query(Tournament).options(joinedload(Tournament.ruleset)).get(tournament.id)


@router.get("/{tournament_id}", response_model=TournamentRead)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    t = db.query(Tournament).options(joinedload(Tournament.ruleset)).get(tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    return t


@router.patch("/{tournament_id}", response_model=TournamentRead)
def update_tournament(tournament_id: int, payload: TournamentUpdate, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return db.query(Tournament).options(joinedload(Tournament.ruleset)).get(t.id)


@router.delete("/{tournament_id}", status_code=204)
def delete_tournament(tournament_id: int, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    db.delete(t)
    db.commit()
