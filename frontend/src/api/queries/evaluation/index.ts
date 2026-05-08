import type {
  AssignJuryArgs,
  GetAvailableJuryArgs,
  GetAvailableJuryResponse,
} from '@/api/services/evaluation/types'
import type { MutationConfig, QueryConfig } from '../types'
import type { AxiosError } from 'axios'
import type { ApiError } from '@/api/errors'
import { evaluationKeys } from '../keys'
import { $api } from '@/api/services'
import { toValue } from 'vue'
import { useMutation, useQuery } from '@tanstack/vue-query'

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

export const useAssignJury = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, AssignJuryArgs>,
) => {
  return useMutation<unknown, AxiosError<ApiError>, AssignJuryArgs>({
    mutationFn: $api.evaluation.assignJury,
    ...config,
  })
}
