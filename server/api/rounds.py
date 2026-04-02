import secrets
import string
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.team import Team
from server.models.tournament import Tournament
from server.schemas.round import PairingCreate, PairingDetail, RoundCreate, RoundDetail, RoundRead
from server.services.compatibility import check_pairing_compatibility
from server.services.pairing import generate_pairings

router = APIRouter(prefix="/tournaments/{tournament_id}/rounds", tags=["rounds"])

_CODE_CHARS = string.ascii_uppercase + string.digits


def _access_code() -> str:
    return "".join(secrets.choice(_CODE_CHARS) for _ in range(6))


def _get_tournament(tid: int, db: Session) -> Tournament:
    t = db.get(Tournament, tid)
    if not t:
        raise HTTPException(404, "Tournament not found")
    return t


def _pairing_detail(p: Pairing) -> PairingDetail:
    return PairingDetail(
        id=p.id,
        round_id=p.round_id,
        petitioner_team_id=p.petitioner_team_id,
        respondent_team_id=p.respondent_team_id,
        petitioner_team_code=p.petitioner_team.team_code,
        respondent_team_code=p.respondent_team.team_code,
        petitioner_school=p.petitioner_team.school_name,
        respondent_school=p.respondent_team.school_name,
        room=p.room,
        status=p.status,
        judge_assignments=[ja for ja in p.judge_assignments],
    )


@router.get("/", response_model=list[RoundRead])
def list_rounds(tournament_id: int, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    return db.query(Round).filter(Round.tournament_id == tournament_id).order_by(Round.round_number).all()


@router.post("/", response_model=RoundDetail)
def create_round(tournament_id: int, payload: RoundCreate, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    existing = db.query(Round).filter(Round.tournament_id == tournament_id).count()
    rnd = Round(
        tournament_id=tournament_id,
        round_number=existing + 1,
        round_type=payload.round_type,
        elim_level=payload.elim_level,
    )
    db.add(rnd)
    db.commit()
    db.refresh(rnd)
    return RoundDetail(
        id=rnd.id,
        tournament_id=rnd.tournament_id,
        round_number=rnd.round_number,
        round_type=rnd.round_type,
        elim_level=rnd.elim_level,
        status=rnd.status,
        pairings=[],
    )


@router.get("/{round_id}", response_model=RoundDetail)
def get_round(tournament_id: int, round_id: int, db: Session = Depends(get_db)):
    _get_tournament(tournament_id, db)
    rnd = (
        db.query(Round)
        .options(
            joinedload(Round.pairings)
            .joinedload(Pairing.petitioner_team),
            joinedload(Round.pairings)
            .joinedload(Pairing.respondent_team),
            joinedload(Round.pairings)
            .joinedload(Pairing.judge_assignments),
        )
        .get(round_id)
    )
    if not rnd or rnd.tournament_id != tournament_id:
        raise HTTPException(404, "Round not found")
    return RoundDetail(
        id=rnd.id,
        tournament_id=rnd.tournament_id,
        round_number=rnd.round_number,
        round_type=rnd.round_type,
        elim_level=rnd.elim_level,
        status=rnd.status,
        pairings=[_pairing_detail(p) for p in rnd.pairings],
    )


@router.post("/{round_id}/generate", response_model=RoundDetail)
def auto_generate_pairings(tournament_id: int, round_id: int, db: Session = Depends(get_db)):
    tournament = _get_tournament(tournament_id, db)
    rnd = db.get(Round, round_id)
    if not rnd or rnd.tournament_id != tournament_id:
        raise HTTPException(404, "Round not found")
    if rnd.status != "pending":
        raise HTTPException(400, "Round is not in pending state")

    ruleset = tournament.ruleset
    teams = db.query(Team).filter(Team.tournament_id == tournament_id).all()
    if len(teams) < 2:
        raise HTTPException(400, "Need at least 2 teams")

    past_pairings = (
        db.query(Pairing)
        .join(Round)
        .filter(Round.tournament_id == tournament_id, Round.id != round_id)
        .all()
    )

    pairs = generate_pairings(teams, past_pairings, ruleset)

    for pet_id, res_id in pairs:
        p = Pairing(round_id=rnd.id, petitioner_team_id=pet_id, respondent_team_id=res_id)
        db.add(p)
        db.flush()
        for _ in range(ruleset.judges_per_round):
            db.add(JudgeAssignment(pairing_id=p.id, judge_name="", access_code=_access_code()))

    db.commit()
    return get_round(tournament_id, round_id, db)


@router.post("/{round_id}/pairings", response_model=PairingDetail)
def add_manual_pairing(tournament_id: int, round_id: int, payload: PairingCreate, db: Session = Depends(get_db)):
    tournament = _get_tournament(tournament_id, db)
    rnd = db.get(Round, round_id)
    if not rnd or rnd.tournament_id != tournament_id:
        raise HTTPException(404, "Round not found")

    violations = check_pairing_compatibility(
        payload.petitioner_team_id,
        payload.respondent_team_id,
        tournament_id,
        rnd.id,
        tournament.ruleset,
        db,
    )
    if violations:
        raise HTTPException(400, detail={"violations": violations})

    p = Pairing(
        round_id=rnd.id,
        petitioner_team_id=payload.petitioner_team_id,
        respondent_team_id=payload.respondent_team_id,
        room=payload.room,
    )
    db.add(p)
    db.flush()
    for j in payload.judges:
        db.add(JudgeAssignment(pairing_id=p.id, judge_name=j.judge_name, access_code=_access_code()))
    db.commit()

    p = (
        db.query(Pairing)
        .options(
            joinedload(Pairing.petitioner_team),
            joinedload(Pairing.respondent_team),
            joinedload(Pairing.judge_assignments),
        )
        .get(p.id)
    )
    return _pairing_detail(p)


@router.patch("/{round_id}/status")
def update_round_status(
    tournament_id: int,
    round_id: int,
    status: Literal["pending", "in_progress", "completed"],
    db: Session = Depends(get_db),
):
    _get_tournament(tournament_id, db)
    rnd = db.get(Round, round_id)
    if not rnd or rnd.tournament_id != tournament_id:
        raise HTTPException(404, "Round not found")
    rnd.status = status
    db.commit()
    return {"status": rnd.status}
