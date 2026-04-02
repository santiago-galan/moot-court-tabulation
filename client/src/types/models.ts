export interface ScoringCriterion {
  name: string
  max_points: number
  weight: number
}

export interface Ruleset {
  id: number
  name: string
  oralists_per_team: number
  num_preliminary_rounds: number
  judges_per_round: number
  pairing_method: string
  same_school_constraint: boolean
  win_determination: string
  ranking_method: string
  scoring_criteria: ScoringCriterion[]
  ranking_tiebreakers: string[]
}

export interface Tournament {
  id: number
  name: string
  event_date: string | null
  status: string
  ruleset_id: number
  ruleset?: Ruleset
}

export interface Oralist {
  id: number
  team_id: number
  name: string
  position: number
}

export interface Team {
  id: number
  tournament_id: number
  team_code: string
  school_name: string
  contact_email: string
  oralists: Oralist[]
}

export interface JudgeAssignment {
  id: number
  pairing_id: number
  judge_name: string
  access_code: string
}

export interface PairingDetail {
  id: number
  round_id: number
  petitioner_team_id: number
  respondent_team_id: number
  petitioner_team_code: string
  respondent_team_code: string
  petitioner_school: string
  respondent_school: string
  room: string
  status: string
  judge_assignments: JudgeAssignment[]
}

export interface Round {
  id: number
  tournament_id: number
  round_number: number
  round_type: string
  elim_level: string | null
  status: string
}

export interface RoundDetail extends Round {
  pairings: PairingDetail[]
}

export interface OralistScoreEntry {
  oralist_id: number
  criterion_name: string
  score: number
}

export interface TeamStanding {
  team_id: number
  team_code: string
  school_name: string
  wins: number
  losses: number
  total_points: number
  opponent_wins: number
  point_differential: number
  rank: number
}

export interface BracketMatch {
  pairing_id: number
  round_number: number
  elim_level: string
  petitioner_team_id: number | null
  respondent_team_id: number | null
  petitioner_team_code: string
  respondent_team_code: string
  winner_team_id: number | null
  status: string
}

export interface JudgeLoginData {
  assignment_id: number
  judge_name: string
  tournament_name: string
  round_number: number
  round_type: string
  room: string
  win_determination: string
  scoring_criteria: ScoringCriterion[]
  petitioner: {
    team_id: number
    team_code: string
    school_name: string
    oralists: Oralist[]
  }
  respondent: {
    team_id: number
    team_code: string
    school_name: string
    oralists: Oralist[]
  }
  already_submitted: boolean
}
