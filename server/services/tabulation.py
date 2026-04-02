from collections import defaultdict

from sqlalchemy.orm import Session, joinedload

from server.models.ballot import Ballot, OralistScore
from server.models.pairing import JudgeAssignment, Pairing
from server.models.round import Round
from server.models.ruleset import Ruleset
from server.models.team import Oralist, Team
from server.models.tournament import Tournament
from server.schemas.scoring import TeamStanding


def _compute_win_counts(past_pairings: list[Pairing], ruleset: Ruleset) -> dict[int, int]:
    wins: dict[int, int] = defaultdict(int)
    for p in past_pairings:
        winner = _pairing_winner(p, ruleset)
        if winner:
            wins[winner] += 1
    return dict(wins)


def _pairing_winner(pairing: Pairing, ruleset: Ruleset) -> int | None:
    ballots: list[Ballot] = []
    for ja in pairing.judge_assignments:
        if ja.ballot and ja.ballot.submitted:
            ballots.append(ja.ballot)

    if not ballots:
        return None

    if ruleset.win_determination == "ballot":
        votes: dict[int, int] = defaultdict(int)
        for b in ballots:
            if b.winner_team_id:
                votes[b.winner_team_id] += 1
        if not votes:
            return None
        return max(votes, key=lambda tid: votes[tid])

    pet_total = 0.0
    res_total = 0.0
    pet_oralist_ids = {o.id for o in pairing.petitioner_team.oralists}
    for b in ballots:
        for s in b.scores:
            if s.oralist_id in pet_oralist_ids:
                pet_total += s.score
            else:
                res_total += s.score

    if pet_total > res_total:
        return pairing.petitioner_team_id
    elif res_total > pet_total:
        return pairing.respondent_team_id
    return None


def compute_standings(tournament_id: int, db: Session) -> list[TeamStanding]:
    tournament = db.query(Tournament).options(joinedload(Tournament.ruleset)).get(tournament_id)
    if not tournament:
        return []

    ruleset = tournament.ruleset
    teams = db.query(Team).filter(Team.tournament_id == tournament_id).all()
    team_map = {t.id: t for t in teams}

    pairings = (
        db.query(Pairing)
        .join(Round)
        .filter(Round.tournament_id == tournament_id, Round.round_type == "preliminary")
        .options(
            joinedload(Pairing.judge_assignments).joinedload(JudgeAssignment.ballot).joinedload(Ballot.scores),
            joinedload(Pairing.petitioner_team).joinedload(Team.oralists),
            joinedload(Pairing.respondent_team).joinedload(Team.oralists),
        )
        .all()
    )

    wins: dict[int, int] = defaultdict(int)
    losses: dict[int, int] = defaultdict(int)
    total_points: dict[int, float] = defaultdict(float)
    opponents: dict[int, list[int]] = defaultdict(list)
    point_diff: dict[int, float] = defaultdict(float)

    for p in pairings:
        pet_id = p.petitioner_team_id
        res_id = p.respondent_team_id
        opponents[pet_id].append(res_id)
        opponents[res_id].append(pet_id)

        pet_pts = 0.0
        res_pts = 0.0
        pet_oralist_ids = {o.id for o in p.petitioner_team.oralists}
        for ja in p.judge_assignments:
            if ja.ballot and ja.ballot.submitted:
                for s in ja.ballot.scores:
                    if s.oralist_id in pet_oralist_ids:
                        pet_pts += s.score
                    else:
                        res_pts += s.score

        total_points[pet_id] += pet_pts
        total_points[res_id] += res_pts
        point_diff[pet_id] += pet_pts - res_pts
        point_diff[res_id] += res_pts - pet_pts

        winner = _pairing_winner(p, ruleset)
        if winner == pet_id:
            wins[pet_id] += 1
            losses[res_id] += 1
        elif winner == res_id:
            wins[res_id] += 1
            losses[pet_id] += 1

    standings: list[TeamStanding] = []
    for t in teams:
        opp_w = sum(wins.get(oid, 0) for oid in opponents.get(t.id, []))
        standings.append(TeamStanding(
            team_id=t.id,
            team_code=t.team_code,
            school_name=t.school_name,
            wins=wins.get(t.id, 0),
            losses=losses.get(t.id, 0),
            total_points=total_points.get(t.id, 0.0),
            opponent_wins=opp_w,
            point_differential=point_diff.get(t.id, 0.0),
        ))

    tiebreaker_keys = ruleset.ranking_tiebreakers or ["wins", "total_points"]

    def sort_key(s: TeamStanding):
        parts = []
        for key in tiebreaker_keys:
            val = getattr(s, key, 0)
            parts.append(-val if isinstance(val, (int, float)) else val)
        return tuple(parts)

    standings.sort(key=sort_key)
    for i, s in enumerate(standings, 1):
        s.rank = i

    return standings
