import { apiClient } from '@/api/client'
import type { AssignJuryArgs, GetAvailableJuryArgs, GetAvailableJuryResponse } from './types'

const prefix = '/api/evaluation'

export const evaluationSerice = {
  getAvailableJury: async (args: GetAvailableJuryArgs) => {
    const { data } = await apiClient.get<GetAvailableJuryResponse>(
      `${prefix}/rounds/${args.roundId}/available-jury`,
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
}
