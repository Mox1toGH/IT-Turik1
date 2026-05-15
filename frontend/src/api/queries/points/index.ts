import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import type { AxiosError } from 'axios'

import { $api } from '@/api/services'
import { pointsKeys } from '@/api/queries/keys'
import type { QueryConfig } from '@/api/queries/types'
import type { ApiError } from '@/api/errors'
import type {
  AdminModifyPointsBody,
  AdminModifyPointsResponse,
  PaginatedPointsTransactions,
  PointsBalance,
  PointsOrdering,
} from '@/api/services/points/types'

export const useMyPointsBalance = (config?: QueryConfig<PointsBalance>) => {
  return useQuery<PointsBalance, AxiosError<ApiError>>({
    queryKey: pointsKeys.myBalance(),
    queryFn: $api.points.getMyBalance,
    ...config,
  })
}

export const useMyPointsTransactions = (
  args: {
    page?: MaybeRefOrGetter<number>
    pageSize?: MaybeRefOrGetter<number>
    ordering?: MaybeRefOrGetter<PointsOrdering>
  } = {},
  config?: QueryConfig<PaginatedPointsTransactions>,
) => {
  return useQuery<PaginatedPointsTransactions, AxiosError<ApiError>>({
    queryKey: computed(() =>
      pointsKeys.myTransactions({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        ordering: toValue(args.ordering) ?? '-created_at',
      }),
    ),
    queryFn: () =>
      $api.points.getMyTransactions({
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        ordering: toValue(args.ordering) ?? '-created_at',
      }),
    ...config,
  })
}

export const useAdminUserPointsBalance = (
  userId: MaybeRefOrGetter<number>,
  config?: QueryConfig<PointsBalance>,
) => {
  return useQuery<PointsBalance, AxiosError<ApiError>>({
    queryKey: computed(() => pointsKeys.userBalance(toValue(userId))),
    queryFn: () => $api.points.getUserBalance(toValue(userId)),
    enabled: computed(() => !!toValue(userId)),
    ...config,
  })
}

export const useAdminUserPointsTransactions = (
  userId: MaybeRefOrGetter<number>,
  args: {
    page?: MaybeRefOrGetter<number>
    pageSize?: MaybeRefOrGetter<number>
    ordering?: MaybeRefOrGetter<PointsOrdering>
  } = {},
  config?: QueryConfig<PaginatedPointsTransactions>,
) => {
  return useQuery<PaginatedPointsTransactions, AxiosError<ApiError>>({
    queryKey: computed(() =>
      pointsKeys.userTransactions(toValue(userId), {
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        ordering: toValue(args.ordering) ?? '-created_at',
      }),
    ),
    queryFn: () =>
      $api.points.getUserTransactions(toValue(userId), {
        page: toValue(args.page) ?? 1,
        pageSize: toValue(args.pageSize) ?? 20,
        ordering: toValue(args.ordering) ?? '-created_at',
      }),
    enabled: computed(() => !!toValue(userId)),
    ...config,
  })
}

export const useAdminModifyUserPoints = () => {
  const queryClient = useQueryClient()

  return useMutation<
    AdminModifyPointsResponse,
    AxiosError<ApiError>,
    { userId: number; body: AdminModifyPointsBody }
  >({
    mutationFn: ({ userId, body }) => $api.points.modifyUserBalance(userId, body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: pointsKeys.myBalance() })
      queryClient.invalidateQueries({ queryKey: pointsKeys.userBalance(variables.userId) })
      queryClient.invalidateQueries({ queryKey: pointsKeys.myTransactionsPrefix() })
      queryClient.invalidateQueries({ queryKey: pointsKeys.userTransactionsPrefix(variables.userId) })
    },
  })
}
