import secrets
import string

from sqlalchemy.orm import Session, joinedload

from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.tournament import Tournament
from server.schemas.bracket import BracketMatchRead
from server.services.tabulation import compute_standings

_CODE_CHARS = string.ascii_uppercase + string.digits

ELIM_LABELS = {
    2: "final",
    4: "semi",
    8: "quarter",
    16: "top16",
    32: "top32",
}


def generate_bracket(tournament_id: int, size: int, db: Session) -> list[BracketMatchRead]:
    if size not in (8, 16, 32):
        raise ValueError("Bracket size must be 8, 16, or 32")

    standings = compute_standings(tournament_id, db)
    if len(standings) < size:
        raise ValueError(f"Not enough teams ({len(standings)}) for a top-{size} bracket")

    seeded = standings[:size]
    tournament = db.get(Tournament, tournament_id)
    existing_rounds = db.query(Round).filter(Round.tournament_id == tournament_id).count()

    matchups: list[tuple[int, int]] = []
    for i in range(size // 2):
        matchups.append((seeded[i].team_id, seeded[size - 1 - i].team_id))

    current_round_num = existing_rounds + 1
    remaining = size
    elim_level = ELIM_LABELS.get(remaining, f"top{remaining}")

    rnd = Round(
        tournament_id=tournament_id,
        round_number=current_round_num,
        round_type="elimination",
        elim_level=elim_level,
    )
    db.add(rnd)
    db.flush()

    judges_per_round = tournament.ruleset.judges_per_round
    for pet_id, res_id in matchups:
        p = Pairing(round_id=rnd.id, petitioner_team_id=pet_id, respondent_team_id=res_id)
        db.add(p)
        db.flush()
        for _ in range(judges_per_round):
            code = "".join(secrets.choice(_CODE_CHARS) for _ in range(6))
            db.add(JudgeAssignment(pairing_id=p.id, judge_name="", access_code=code))

    db.commit()
    return get_bracket_matches(tournament_id, db)


def get_bracket_matches(tournament_id: int, db: Session) -> list[BracketMatchRead]:
    pairings = (
        db.query(Pairing)
        .join(Round)
        .filter(
            Round.tournament_id == tournament_id,
            Round.round_type == "elimination",
        )
        .options(
            joinedload(Pairing.petitioner_team),
            joinedload(Pairing.respondent_team),
            joinedload(Pairing.round),
        )
        .all()
    )

    results: list[BracketMatchRead] = []
    for p in pairings:
        results.append(BracketMatchRead(
            pairing_id=p.id,
            round_number=p.round.round_number,
            elim_level=p.round.elim_level or "",
            petitioner_team_id=p.petitioner_team_id,
            respondent_team_id=p.respondent_team_id,
            petitioner_team_code=p.petitioner_team.team_code if p.petitioner_team else "",
            respondent_team_code=p.respondent_team.team_code if p.respondent_team else "",
            status=p.status,
        ))

    return results
