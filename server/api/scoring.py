from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.ballot import Ballot, OralistScore
from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.team import Team
from server.models.tournament import Tournament
from server.schemas.scoring import BallotRead, BallotSubmission, TeamStanding
from server.services.tabulation import compute_standings
from server.ws.manager import manager

router = APIRouter(tags=["scoring"])


def _validate_ballot(payload: BallotSubmission, ja: JudgeAssignment, db: Session):
    pairing = db.get(Pairing, ja.pairing_id)
    rnd = db.get(Round, pairing.round_id)
    tournament = db.query(Tournament).options(joinedload(Tournament.ruleset)).get(rnd.tournament_id)
    ruleset = tournament.ruleset

    criteria_map = {c["name"]: c for c in ruleset.scoring_criteria}

    pet_team = db.query(Team).options(joinedload(Team.oralists)).get(pairing.petitioner_team_id)
    res_team = db.query(Team).options(joinedload(Team.oralists)).get(pairing.respondent_team_id)
    valid_oralist_ids = {o.id for o in pet_team.oralists} | {o.id for o in res_team.oralists}

    if payload.winner_team_id is not None and payload.winner_team_id not in (
        pairing.petitioner_team_id, pairing.respondent_team_id
    ):
        raise HTTPException(400, "Winner must be one of the two teams in this pairing")

    for entry in payload.scores:
        if entry.oralist_id not in valid_oralist_ids:
            raise HTTPException(400, f"Oralist {entry.oralist_id} is not part of this pairing")
        if entry.criterion_name not in criteria_map:
            raise HTTPException(400, f"Unknown scoring criterion: {entry.criterion_name}")
        max_pts = criteria_map[entry.criterion_name]["max_points"]
        if entry.score > max_pts:
            raise HTTPException(400, f"Score {entry.score} exceeds max {max_pts} for {entry.criterion_name}")


@router.post("/judge-assignments/{assignment_id}/ballot", response_model=BallotRead)
async def submit_ballot(
    assignment_id: int,
    payload: BallotSubmission,
    db: Session = Depends(get_db),
):
    ja = db.query(JudgeAssignment).options(joinedload(JudgeAssignment.ballot)).get(assignment_id)
    if not ja:
        raise HTTPException(404, "Judge assignment not found")

    _validate_ballot(payload, ja, db)

    ballot = ja.ballot
    if not ballot:
        ballot = Ballot(judge_assignment_id=ja.id)
        db.add(ballot)
        db.flush()

    ballot.winner_team_id = payload.winner_team_id
    ballot.submitted = True
    ballot.submitted_at = datetime.now(UTC)

    db.query(OralistScore).filter(OralistScore.ballot_id == ballot.id).delete()
    for entry in payload.scores:
        db.add(OralistScore(
            ballot_id=ballot.id,
            oralist_id=entry.oralist_id,
            criterion_name=entry.criterion_name,
            score=entry.score,
        ))
    db.commit()
    db.refresh(ballot)

    pairing = db.get(Pairing, ja.pairing_id)
    all_submitted = all(
        a.ballot and a.ballot.submitted
        for a in db.query(JudgeAssignment)
        .filter(JudgeAssignment.pairing_id == pairing.id)
        .options(joinedload(JudgeAssignment.ballot))
        .all()
    )
    if all_submitted:
        pairing.status = "completed"
        db.commit()

    await manager.broadcast("ballot_submitted", {
        "assignment_id": assignment_id,
        "pairing_id": ja.pairing_id,
        "all_submitted": all_submitted,
    })

    return db.query(Ballot).options(joinedload(Ballot.scores)).get(ballot.id)


@router.get("/judge-assignments/{assignment_id}/ballot", response_model=BallotRead | None)
def get_ballot(assignment_id: int, db: Session = Depends(get_db)):
    ja = db.get(JudgeAssignment, assignment_id)
    if not ja:
        raise HTTPException(404, "Judge assignment not found")
    ballot = (
        db.query(Ballot)
        .options(joinedload(Ballot.scores))
        .filter(Ballot.judge_assignment_id == assignment_id)
        .first()
    )
    return ballot


@router.get("/tournaments/{tournament_id}/standings", response_model=list[TeamStanding])
def get_standings(tournament_id: int, db: Session = Depends(get_db)):
    return compute_standings(tournament_id, db)
