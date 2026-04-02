import random
from collections import defaultdict

from server.models.pairing import Pairing
from server.models.ruleset import Ruleset
from server.models.team import Team


def _side_history(past_pairings: list[Pairing]) -> dict[int, dict[str, int]]:
    history: dict[int, dict[str, int]] = defaultdict(lambda: {"petitioner": 0, "respondent": 0})
    for p in past_pairings:
        history[p.petitioner_team_id]["petitioner"] += 1
        history[p.respondent_team_id]["respondent"] += 1
    return history


def _opponent_history(past_pairings: list[Pairing]) -> dict[int, set[int]]:
    opponents: dict[int, set[int]] = defaultdict(set)
    for p in past_pairings:
        opponents[p.petitioner_team_id].add(p.respondent_team_id)
        opponents[p.respondent_team_id].add(p.petitioner_team_id)
    return opponents


def _assign_sides(
    team_a_id: int,
    team_b_id: int,
    side_hist: dict[int, dict[str, int]],
) -> tuple[int, int]:
    a_pet = side_hist[team_a_id]["petitioner"]
    b_pet = side_hist[team_b_id]["petitioner"]
    if a_pet < b_pet:
        return team_a_id, team_b_id
    elif b_pet < a_pet:
        return team_b_id, team_a_id
    return (team_a_id, team_b_id) if random.random() < 0.5 else (team_b_id, team_a_id)


def generate_pairings(
    teams: list[Team],
    past_pairings: list[Pairing],
    ruleset: Ruleset,
) -> list[tuple[int, int]]:
    if ruleset.pairing_method == "swiss":
        return _swiss_pair(teams, past_pairings, ruleset)
    return _random_pair(teams, past_pairings, ruleset)


def _random_pair(
    teams: list[Team],
    past_pairings: list[Pairing],
    ruleset: Ruleset,
) -> list[tuple[int, int]]:
    side_hist = _side_history(past_pairings)
    opp_hist = _opponent_history(past_pairings)
    school_map = {t.id: t.school_name for t in teams}

    pool = [t.id for t in teams]
    random.shuffle(pool)
    pairs: list[tuple[int, int]] = []

    paired: set[int] = set()
    for i, tid in enumerate(pool):
        if tid in paired:
            continue
        for j in range(i + 1, len(pool)):
            oid = pool[j]
            if oid in paired:
                continue
            if ruleset.same_school_constraint and school_map[tid] == school_map[oid]:
                continue
            if oid in opp_hist.get(tid, set()):
                continue
            pet, res = _assign_sides(tid, oid, side_hist)
            pairs.append((pet, res))
            side_hist[pet]["petitioner"] += 1
            side_hist[res]["respondent"] += 1
            paired.add(tid)
            paired.add(oid)
            break

    unpaired = [tid for tid in pool if tid not in paired]
    for i in range(0, len(unpaired) - 1, 2):
        pet, res = _assign_sides(unpaired[i], unpaired[i + 1], side_hist)
        pairs.append((pet, res))

    return pairs


def _swiss_pair(
    teams: list[Team],
    past_pairings: list[Pairing],
    ruleset: Ruleset,
) -> list[tuple[int, int]]:
    if not past_pairings:
        return _random_pair(teams, past_pairings, ruleset)

    from server.services.tabulation import _compute_win_counts

    side_hist = _side_history(past_pairings)
    opp_hist = _opponent_history(past_pairings)
    school_map = {t.id: t.school_name for t in teams}
    win_counts = _compute_win_counts(past_pairings, ruleset)

    team_ids = [t.id for t in teams]
    team_ids.sort(key=lambda tid: win_counts.get(tid, 0), reverse=True)

    result = _backtrack_pair(
        team_ids, side_hist, opp_hist, school_map,
        ruleset.same_school_constraint, win_counts,
    )
    if result is None:
        return _random_pair(teams, past_pairings, ruleset)
    return result


def _backtrack_pair(
    remaining: list[int],
    side_hist: dict[int, dict[str, int]],
    opp_hist: dict[int, set[int]],
    school_map: dict[int, str],
    same_school_constraint: bool,
    win_counts: dict[int, int],
) -> list[tuple[int, int]] | None:
    if len(remaining) <= 1:
        return []

    first = remaining[0]
    rest = remaining[1:]

    for i, candidate in enumerate(rest):
        if candidate in opp_hist.get(first, set()):
            continue
        if same_school_constraint and school_map.get(first) == school_map.get(candidate):
            continue

        new_remaining = rest[:i] + rest[i + 1:]
        sub = _backtrack_pair(
            new_remaining, side_hist, opp_hist, school_map,
            same_school_constraint, win_counts,
        )
        if sub is not None:
            pet, res = _assign_sides(first, candidate, side_hist)
            return [(pet, res), *sub]

    return None
