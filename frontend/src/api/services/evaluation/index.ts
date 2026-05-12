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
  getAvailableJury: async (args: GetAvailableJuryArgs) => {
    const { data } = await apiClient.get<GetAvailableJuryResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/available-jury/`,
    )
    return data
  },

  getRoundLeaderboard: async (args: GetRoundLeaderboardArgs) => {
    const { data } = await apiClient.get<GetRoundLeaderboardResponse>(
      `${prefix}/tournaments/rounds/${toValue(args.roundId)}/leaderboard/`,
    )
    return data
  },

  getTournamentLeaderboard: async (args: GetTournamentLeaderboardArgs) => {
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

  getAssignments: async (args?: GetAssignmentsArgs) => {
    const params = new URLSearchParams()
    if (args?.roundId) {
      params.append('round_id', String(args.roundId))
    }
    if (args?.roundIds?.length) {
      params.append('round_ids', args.roundIds.join(','))
    }
    if (args?.tournamentIds?.length) {
      params.append('tournament_ids', args.tournamentIds.join(','))
    }
    if (args?.evaluationStatus) {
      params.append('evaluation_status', args.evaluationStatus)
    }
    if (args?.page) {
      params.append('page', String(args.page))
    }
    if (args?.pageSize) {
      params.append('page_size', String(args.pageSize))
    }

    const query = params.toString()
    const { data } = await apiClient.get<GetAssignmentsResponse>(
      `${prefix}/assignments/${query ? `?${query}` : ''}`,
    )
    return {
      ...data,
      results: data.results.map((item) =>
        normalizeAssignment(item as Omit<JuryAssignmentData, 'round_details' | 'criteria'>),
      ),
    }
  },

  getAssignmentDetail: async (args: GetAssignmentDetailArgs) => {
    const { data } = await apiClient.get<GetAssignmentDetailResponse>(`${prefix}/assignments/${args.id}/`)
    return normalizeAssignment(data as Omit<JuryAssignmentData, 'round_details' | 'criteria'>)
  },

  createEvaluation: async (args: CreateEvaluationArgs) => {
    const { data } = await apiClient.post<CreateEvaluationResponse>(`${prefix}/evaluate/`, args.body)
    return data
  },

  updateEvaluation: async (args: UpdateEvaluationArgs) => {
    const { data } = await apiClient.patch<UpdateEvaluationResponse>(
      `${prefix}/evaluate/${args.id}/`,
      args.body,
    )
    return data
  },

  deleteEvaluation: async (args: DeleteEvaluationArgs) => {
    const { data } = await apiClient.delete(`${prefix}/evaluate/${args.id}/`)
    return data
  },
}

export const evaluationSerice = evaluationService
