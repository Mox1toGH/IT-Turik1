import type {
  AssignJuryArgs,
  CreateEvaluationArgs,
  CreateEvaluationResponse,
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
  UpdateEvaluationArgs,
  UpdateEvaluationResponse,
} from '@/api/services/evaluation/types'
import type { MutationConfig, QueryConfig } from '../types'
import type { AxiosError } from 'axios'
import type { ApiError } from '@/api/errors'
import { evaluationKeys } from '../keys'
import { $api } from '@/api/services'
import { computed, toValue } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'

export const useAvailableJury = (
  payload: GetAvailableJuryArgs,
  config?: QueryConfig<GetAvailableJuryResponse>,
) => {
  return useQuery<GetAvailableJuryResponse, AxiosError<ApiError>>({
    queryKey: evaluationKeys.availableJury(toValue(payload.roundId)),
    queryFn: () => $api.evaluation.getAvailableJury({ roundId: toValue(payload.roundId) }),
    ...config,
  })
}

export const useRoundLeaderboard = (
  payload: GetRoundLeaderboardArgs,
  config?: QueryConfig<GetRoundLeaderboardResponse>,
) => {
  return useQuery<GetRoundLeaderboardResponse, AxiosError<ApiError>>({
    queryKey: computed(() => evaluationKeys.roundLeaderboard(toValue(payload.roundId))),
    queryFn: () => $api.evaluation.getRoundLeaderboard({ roundId: toValue(payload.roundId) }),
    ...config,
  })
}

export const useTournamentLeaderboard = (
  payload: GetTournamentLeaderboardArgs,
  config?: QueryConfig<GetTournamentLeaderboardResponse>,
) => {
  return useQuery<GetTournamentLeaderboardResponse, AxiosError<ApiError>>({
    queryKey: computed(() => evaluationKeys.tournamentLeaderboard(toValue(payload.tournamentId))),
    queryFn: () =>
      $api.evaluation.getTournamentLeaderboard({ tournamentId: toValue(payload.tournamentId) }),
    ...config,
  })
}

export const useAssignJury = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, AssignJuryArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, AssignJuryArgs>({
    mutationFn: $api.evaluation.assignJury,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: evaluationKeys.all() })
    },
    ...config,
  })
}

export const useAssignments = (
  payload: GetAssignmentsArgs = {},
  config?: QueryConfig<GetAssignmentsResponse>,
) => {
  return useQuery<GetAssignmentsResponse, AxiosError<ApiError>>({
    queryKey: computed(() => evaluationKeys.assignments(toValue(payload.roundId))),
    queryFn: () => $api.evaluation.getAssignments({ roundId: toValue(payload.roundId) }),
    ...config,
  })
}

export const useAssignmentDetail = (
  payload: GetAssignmentDetailArgs,
  config?: QueryConfig<GetAssignmentDetailResponse>,
) => {
  return useQuery<GetAssignmentDetailResponse, AxiosError<ApiError>>({
    queryKey: computed(() => evaluationKeys.assignment(toValue(payload.id))),
    queryFn: () => $api.evaluation.getAssignmentDetail({ id: toValue(payload.id) }),
    ...config,
  })
}

export const useCreateEvaluation = (
  config?: MutationConfig<
    CreateEvaluationResponse,
    AxiosError<ApiError<keyof CreateEvaluationArgs['body']>>,
    CreateEvaluationArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    CreateEvaluationResponse,
    AxiosError<ApiError<keyof CreateEvaluationArgs['body']>>,
    CreateEvaluationArgs
  >({
    mutationFn: $api.evaluation.createEvaluation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: evaluationKeys.all() })
    },
    ...config,
  })
}

export const useUpdateEvaluation = (
  config?: MutationConfig<
    UpdateEvaluationResponse,
    AxiosError<ApiError<keyof UpdateEvaluationArgs['body']>>,
    UpdateEvaluationArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    UpdateEvaluationResponse,
    AxiosError<ApiError<keyof UpdateEvaluationArgs['body']>>,
    UpdateEvaluationArgs
  >({
    mutationFn: $api.evaluation.updateEvaluation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: evaluationKeys.all() })
    },
    ...config,
  })
}
