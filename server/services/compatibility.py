from sqlalchemy.orm import Session

from server.models.pairing import Pairing
from server.models.round import Round
from server.models.ruleset import Ruleset
from server.models.team import Team


def check_pairing_compatibility(
    pet_id: int,
    res_id: int,
    tournament_id: int,
    current_round_id: int,
    ruleset: Ruleset,
    db: Session,
) -> list[str]:
    violations: list[str] = []

    pet = db.get(Team, pet_id)
    res = db.get(Team, res_id)
    if not pet or not res:
        violations.append("One or both teams not found")
        return violations

    if ruleset.same_school_constraint and pet.school_name == res.school_name:
        violations.append(f"Same-school matchup: both teams from {pet.school_name}")

    past = (
        db.query(Pairing)
        .join(Round)
        .filter(Round.tournament_id == tournament_id, Round.id != current_round_id)
        .all()
    )

    for p in past:
        ids = {p.petitioner_team_id, p.respondent_team_id}
        if {pet_id, res_id} == ids:
            violations.append("These teams have already faced each other")
            break

    pet_counts = {"petitioner": 0, "respondent": 0}
    res_counts = {"petitioner": 0, "respondent": 0}
    for p in past:
        if p.petitioner_team_id == pet_id:
            pet_counts["petitioner"] += 1
        if p.respondent_team_id == pet_id:
            pet_counts["respondent"] += 1
        if p.petitioner_team_id == res_id:
            res_counts["petitioner"] += 1
        if p.respondent_team_id == res_id:
            res_counts["respondent"] += 1

    pet_imbalance = abs((pet_counts["petitioner"] + 1) - pet_counts["respondent"])
    res_imbalance = abs(res_counts["petitioner"] - (res_counts["respondent"] + 1))
    if pet_imbalance > 1:
        violations.append(f"Side imbalance for petitioner team {pet.team_code}")
    if res_imbalance > 1:
        violations.append(f"Side imbalance for respondent team {res.team_code}")

    return violations
