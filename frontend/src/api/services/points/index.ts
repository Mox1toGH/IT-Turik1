import { apiClient } from '@/api/client'
import type {
  AdminModifyPointsBody,
  AdminModifyPointsResponse,
  PaginatedPointsTransactions,
  PointsBalance,
  PointsOrdering,
} from './types'

const prefix = '/api/points'

export const pointsService = {
  async getMyBalance() {
    const { data } = await apiClient.get<PointsBalance>(`${prefix}/balance/`)
    return data
  },

  async getMyTransactions(args?: { page?: number; pageSize?: number; ordering?: PointsOrdering }) {
    const { data } = await apiClient.get<PaginatedPointsTransactions>(`${prefix}/transactions/`, {
      params: {
        page: args?.page ?? 1,
        page_size: args?.pageSize ?? 20,
        ordering: args?.ordering ?? '-created_at',
      },
    })
    return data
  },

  async getUserBalance(userId: number) {
    const { data } = await apiClient.get<PointsBalance>(`${prefix}/admin/users/${userId}/balance/`)
    return data
  },

  async getUserTransactions(
    userId: number,
    args?: { page?: number; pageSize?: number; ordering?: PointsOrdering },
  ) {
    const { data } = await apiClient.get<PaginatedPointsTransactions>(
      `${prefix}/admin/users/${userId}/transactions/`,
      {
        params: {
          page: args?.page ?? 1,
          page_size: args?.pageSize ?? 20,
          ordering: args?.ordering ?? '-created_at',
        },
      },
    )
    return data
  },

  async modifyUserBalance(userId: number, body: AdminModifyPointsBody) {
    const { data } = await apiClient.post<AdminModifyPointsResponse>(
      `${prefix}/admin/users/${userId}/modify/`,
      body,
    )
    return data
  },
}
