from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from server.database import get_db
from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.team import Oralist, Team
from server.models.tournament import Tournament

router = APIRouter(prefix="/judge", tags=["judge_portal"])


@router.get("/login/{access_code}")
def judge_login(access_code: str, db: Session = Depends(get_db)):
    ja = (
        db.query(JudgeAssignment)
        .filter(JudgeAssignment.access_code == access_code.upper())
        .options(
            joinedload(JudgeAssignment.pairing)
            .joinedload(Pairing.petitioner_team)
            .joinedload(Team.oralists),
            joinedload(JudgeAssignment.pairing)
            .joinedload(Pairing.respondent_team)
            .joinedload(Team.oralists),
            joinedload(JudgeAssignment.pairing)
            .joinedload(Pairing.round)
            .joinedload(Round.tournament)
            .joinedload(Tournament.ruleset),
            joinedload(JudgeAssignment.ballot),
        )
        .first()
    )
    if not ja:
        raise HTTPException(404, "Invalid access code")

    pairing = ja.pairing
    rnd = pairing.round
    tournament = rnd.tournament
    ruleset = tournament.ruleset

    return {
        "assignment_id": ja.id,
        "judge_name": ja.judge_name,
        "tournament_name": tournament.name,
        "round_number": rnd.round_number,
        "round_type": rnd.round_type,
        "room": pairing.room,
        "win_determination": ruleset.win_determination,
        "scoring_criteria": ruleset.scoring_criteria,
        "petitioner": {
            "team_id": pairing.petitioner_team.id,
            "team_code": pairing.petitioner_team.team_code,
            "school_name": pairing.petitioner_team.school_name,
            "oralists": [
                {"id": o.id, "name": o.name, "position": o.position}
                for o in sorted(pairing.petitioner_team.oralists, key=lambda o: o.position)
            ],
        },
        "respondent": {
            "team_id": pairing.respondent_team.id,
            "team_code": pairing.respondent_team.team_code,
            "school_name": pairing.respondent_team.school_name,
            "oralists": [
                {"id": o.id, "name": o.name, "position": o.position}
                for o in sorted(pairing.respondent_team.oralists, key=lambda o: o.position)
            ],
        },
        "already_submitted": ja.ballot.submitted if ja.ballot else False,
    }
