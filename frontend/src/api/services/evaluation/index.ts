import { apiClient } from '@/api/client'
import type {
  AssignJuryArgs,
  CreateEvaluationArgs,
  CreateEvaluationResponse,
  DeleteEvaluationArgs,
  GetAssignmentDetailArgs,
  GetAssignmentDetailResponse,
  GetAssignmentsArgs,
  GetAssignmentsResponse,
  GetAvailableJuryArgs,
  GetAvailableJuryResponse,
  GetRoundLeaderboardArgs,
  GetRoundLeaderboardResponse,
  GetTournamentLeaderboardArgs,
  GetTournamentLeaderboardResponse,
  JuryAssignmentData,
  RoundCriterion,
  UpdateEvaluationArgs,
  UpdateEvaluationResponse,
} from './types'
import { toValue } from 'vue'
import type { MaybeRefArgs } from '@/api/queries/types'

const prefix = '/api/evaluation'

const toCriteria = (assignment: JuryAssignmentData): RoundCriterion[] => {
  return assignment.submission_details?.round_details?.criteria ?? []
}

const normalizeAssignment = (
  assignment: Omit<JuryAssignmentData, 'round_details' | 'criteria'>,
): JuryAssignmentData => {
  const criteria = toCriteria(assignment as JuryAssignmentData)
  return {
    ...assignment,
    round_details: assignment.submission_details.round_details,
    criteria,
  }
}

export const evaluationService = {
  getAvailableJury: async (args: MaybeRefArgs<GetAvailableJuryArgs>) => {
    const { data } = await apiClient.get<GetAvailableJuryResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/available-jury/`,
    )
    return data
  },

  getRoundLeaderboard: async (args: MaybeRefArgs<GetRoundLeaderboardArgs>) => {
    const { data } = await apiClient.get<GetRoundLeaderboardResponse>(
      `${prefix}/tournaments/rounds/${toValue(args.roundId)}/leaderboard/`,
    )
    return data
  },

  getTournamentLeaderboard: async (args: MaybeRefArgs<GetTournamentLeaderboardArgs>) => {
    const { data } = await apiClient.get<GetTournamentLeaderboardResponse>(
      `${prefix}/tournaments/${toValue(args.tournamentId)}/leaderboard/`,
    )
    return data
  },

  assignJury: async (args: AssignJuryArgs) => {
    const { data } = await apiClient.post(
      `${prefix}/rounds/${args.roundId}/assign-jury/`,
      args.body,
    )
    return data
  },

  getAssignments: async (args?: MaybeRefArgs<GetAssignmentsArgs>) => {
    const params = new URLSearchParams()
    const roundId = args?.roundId ? toValue(args.roundId) : undefined
    if (roundId) {
      params.append('round_id', String(roundId))
    }

    const query = params.toString()
    const { data } = await apiClient.get<GetAssignmentsResponse>(
      `${prefix}/assignments/${query ? `?${query}` : ''}`,
    )
    return data.map((item) =>
      normalizeAssignment(item as Omit<JuryAssignmentData, 'round_details' | 'criteria'>),
    )
  },

  getAssignmentDetail: async (args: MaybeRefArgs<GetAssignmentDetailArgs>) => {
    const { data } = await apiClient.get<GetAssignmentDetailResponse>(
      `${prefix}/assignments/${toValue(args.id)}/`,
    )
    return normalizeAssignment(data as Omit<JuryAssignmentData, 'round_details' | 'criteria'>)
  },

  createEvaluation: async (args: MaybeRefArgs<CreateEvaluationArgs>) => {
    const { data } = await apiClient.post<CreateEvaluationResponse>(
      `${prefix}/evaluate/`,
      toValue(args.body),
    )
    return data
  },

  updateEvaluation: async (args: MaybeRefArgs<UpdateEvaluationArgs>) => {
    const { data } = await apiClient.patch<UpdateEvaluationResponse>(
      `${prefix}/evaluate/${toValue(args.id)}/`,
      toValue(args.body),
    )
    return data
  },

  deleteEvaluation: async (args: MaybeRefArgs<DeleteEvaluationArgs>) => {
    const { data } = await apiClient.delete(`${prefix}/evaluate/${toValue(args.id)}/`)
    return data
  },
}
