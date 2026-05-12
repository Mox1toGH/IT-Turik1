import type { RoundId, SubmissionId, User, UserId } from '@/api/dbTypes'
import type { TournamentId } from '@/api/dbTypes'
import type { MaybeRefOrGetter } from 'vue'

// available jury
export interface GetAvailableJuryArgs {
  roundId: MaybeRefOrGetter<RoundId>
}

export type GetAvailableJuryResponse = Pick<User, 'id' | 'username' | 'full_name' | 'email'>[]

// leaderboard
export interface GetRoundLeaderboardArgs {
  roundId: MaybeRefOrGetter<RoundId>
}

export interface GetTournamentLeaderboardArgs {
  tournamentId: MaybeRefOrGetter<TournamentId>
}

export type CriteriaBreakdown = Record<string, number>

export interface RoundLeaderboardRanking {
  rank: number
  team_id: number
  team_name: string
  total_score: number
  average_score: number
  criteria_breakdown: CriteriaBreakdown
  jury_breakdown: unknown | null
}

export interface GetRoundLeaderboardResponse {
  round_id: number
  is_snapshot: boolean
  rankings: RoundLeaderboardRanking[]
}

export interface TournamentLeaderboardRoundBreakdown {
  round_id: number
  round_name: string
  total_score: number
  average_score: number
  criteria_breakdown: CriteriaBreakdown
  jury_breakdown: unknown | null
}

export interface TournamentLeaderboardRanking {
  rank: number
  team_id: number
  team_name: string
  total_score: number
  rounds: TournamentLeaderboardRoundBreakdown[]
}

export interface GetTournamentLeaderboardResponse {
  tournament_id: number
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
  roundIds?: RoundId[]
  tournamentIds?: TournamentId[]
  evaluationStatus?: 'all' | 'evaluated' | 'not_evaluated'
  page?: number
  pageSize?: number
}

export interface GetAssignmentDetailArgs {
  id: number
}

export interface RoundCriterion {
  id: string
  name: string
  description: string
  max_score: number
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
  final_score: number
  comment: string
  created_at: string
}

export interface JuryAssignmentData {
  id: number
  submission: SubmissionId
  submission_details: {
    id: SubmissionId
    round: RoundId
    round_details: {
      id: RoundId
      name: string
      start_date: string
      end_date: string
      status: string
      criteria: RoundCriterion[]
    }
  }
  round_details: {
    id: RoundId
    name: string
    start_date: string
    end_date: string
    status: string
    criteria: RoundCriterion[]
    tournament?: number
  }
  criteria: RoundCriterion[]
  evaluation: EvaluationData | null
  is_evaluated: boolean
  created_at: string
}

export interface PaginatedAssignmentsResponse {
  count: number
  next: string | null
  previous: string | null
  evaluated_count: number
  results: JuryAssignmentData[]
}

export type GetAssignmentsResponse = PaginatedAssignmentsResponse
export type GetAssignmentDetailResponse = JuryAssignmentData

// create/update evaluation
export interface CreateEvaluationBody {
  tournament_id: number
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
    tournament_id: number
    assignment?: number
    scores?: ScoreItem[]
    comment?: string
  }
}

export type UpdateEvaluationResponse = EvaluationData

export interface DeleteEvaluationArgs {
  id: number
}
