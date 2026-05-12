import type { Round, RoundId, SubmissionId, TeamId, User, UserId } from '@/api/dbTypes'
import type { TournamentId } from '@/api/dbTypes'

// available jury
export interface GetAvailableJuryArgs {
  roundId: RoundId
}

export type GetAvailableJuryResponse = Pick<User, 'id' | 'username' | 'full_name' | 'email'>[]

// leaderboard
export interface GetRoundLeaderboardArgs {
  roundId: RoundId
}

export interface GetTournamentLeaderboardArgs {
  tournamentId: TournamentId
}

export type CriteriaBreakdown = Record<string, number>

export interface RoundLeaderboardRanking {
  rank: number
  team_id: TeamId
  team_name: string
  total_score: number
  average_score: number
  criteria_breakdown: CriteriaBreakdown
  jury_breakdown: unknown | null
}

export interface GetRoundLeaderboardResponse {
  round_id: RoundId
  is_snapshot: boolean
  rankings: RoundLeaderboardRanking[]
}

export interface TournamentLeaderboardRoundBreakdown {
  round_id: RoundId
  round_name: string
  total_score: number
  average_score: number
  criteria_breakdown: CriteriaBreakdown
  jury_breakdown: unknown | null
}

export interface TournamentLeaderboardRanking {
  rank: number
  team_id: TeamId
  team_name: string
  total_score: number
  rounds: TournamentLeaderboardRoundBreakdown[]
}

export interface GetTournamentLeaderboardResponse {
  tournament_id: TournamentId
  is_snapshot: boolean
  rankings: TournamentLeaderboardRanking[]
}

// assign jury
export interface AssignJuryArgs {
  roundId: RoundId
  body: AssignJuryBody
}

export type AssignJuryBody = {
  submission: SubmissionId
  jury: UserId[]
}[]

// assignments
export interface GetAssignmentsArgs {
  roundId?: RoundId
}

export interface GetAssignmentDetailArgs {
  id: number
}

export interface ScoreItem {
  criterion_id: string
  criterion_name?: string
  score: number
}

export interface EvaluationData {
  id: number
  assignment: number
  scores: ScoreItem[]
  total_score: number
  average_score: number
  comment: string
  created_at: string
}

export interface JuryAssignmentData {
  id: number
  submission: SubmissionId
  submission_details: {
    id: SubmissionId
    round: RoundId
    round_details: Pick<
      Round,
      'id' | 'name' | 'start_date' | 'end_date' | 'status' | 'criteria' | 'tournament'
    >
  }
  round_details: Pick<
    Round,
    'id' | 'name' | 'start_date' | 'end_date' | 'status' | 'criteria' | 'tournament'
  >
  criteria: RoundCriterion[]
  evaluation: EvaluationData | null
  is_evaluated: boolean
  created_at: string
}

export type GetAssignmentsResponse = JuryAssignmentData[]
export type GetAssignmentDetailResponse = JuryAssignmentData

// create/update evaluation
export interface CreateEvaluationBody {
  tournament_id: TournamentId
  assignment: number
  scores: ScoreItem[]
  comment?: string
}

export interface CreateEvaluationArgs {
  body: CreateEvaluationBody
}

export type CreateEvaluationResponse = EvaluationData

export interface UpdateEvaluationArgs {
  id: number
  body: {
    tournament_id: TournamentId
    assignment?: number
    scores?: ScoreItem[]
    comment?: string
  }
}

export type UpdateEvaluationResponse = EvaluationData

export interface DeleteEvaluationArgs {
  id: number
}
