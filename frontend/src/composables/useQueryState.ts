import { computed, unref, type ComputedRef, type MaybeRef } from 'vue'
import type { ApiErrorResponse } from '@/shared/types/apiError'
import type { ErrorType } from '@/lib/apiClient'

export type QueryErrorCode = number | 'network' | null

/** Structural subset of a Vue Query result accepted by query UI components. */
export interface QueryLike {
  isPending: MaybeRef<boolean>
  isError: MaybeRef<boolean>
  data: MaybeRef<unknown>
  error: MaybeRef<unknown>
  isFetching?: MaybeRef<boolean>
  refetch?: MaybeRef<() => unknown>
}

export interface QueryState {
  data: ComputedRef<unknown>
  isInitialLoading: ComputedRef<boolean>
  isFetching: ComputedRef<boolean>
  isRefetching: ComputedRef<boolean>
  isError: ComputedRef<boolean>
  error: ComputedRef<unknown>
  errorCode: ComputedRef<QueryErrorCode>
  refetch: () => Promise<unknown>
}

export function getErrorCode(error: unknown): QueryErrorCode {
  const err = error as Partial<ErrorType<ApiErrorResponse>> | null | undefined
  const status = err?._axiosError?.response?.status
  if (typeof status === 'number') return status
  return 'network'
}

/** Shared reactive interpretation of the query states used by query UI. */
export function useQueryState(query: MaybeRef<QueryLike>): QueryState {
  const data = computed(() => unref(unref(query).data))
  const isError = computed(() => unref(unref(query).isError))
  const isFetching = computed(() => {
    const currentQuery = unref(query)
    return currentQuery.isFetching === undefined ? false : unref(currentQuery.isFetching)
  })
  const isInitialLoading = computed(() => unref(unref(query).isPending) && data.value === undefined)
  const isRefetching = computed(() => isFetching.value && data.value !== undefined)
  const error = computed(() => unref(unref(query).error))
  const errorCode = computed<QueryErrorCode>(() =>
    isError.value ? getErrorCode(error.value) : null,
  )

  async function refetch() {
    const currentQuery = unref(query)
    if (currentQuery.refetch === undefined) return undefined
    return await unref(currentQuery.refetch)()
  }

  return { data, isInitialLoading, isFetching, isRefetching, isError, error, errorCode, refetch }
}
