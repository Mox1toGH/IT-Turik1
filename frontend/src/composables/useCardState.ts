import { computed, unref, type MaybeRef } from 'vue'
import type { ErrorResponse } from '@/api/backendAPINinja.schemas'
import type { ErrorType } from '@/lib/apiClient'

export type CardStatus = 'loading' | 'error' | 'empty' | 'data'
export type CardErrorCode = number | 'network' | null

export interface CardQuery {
  isPending: MaybeRef<boolean>
  isError: MaybeRef<boolean>
  data: MaybeRef<unknown>
  error: MaybeRef<unknown>
  isFetching?: MaybeRef<boolean>
  refetch?: MaybeRef<() => unknown>
}

export function getErrorCode(error: unknown): CardErrorCode {
  const err = error as Partial<ErrorType<ErrorResponse>> | null | undefined
  const status = err?._axiosError?.response?.status
  if (typeof status === 'number') return status
  return 'network'
}

function isEmptyData(data: unknown): boolean {
  if (Array.isArray(data)) return data.length === 0
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>

    // Paginated list shapes: { data, total } (tournaments), { items } (notifications), { results }
    if (obj.total === 0) return true
    if (Array.isArray(obj.items) && obj.items.length === 0) return true
    if (Array.isArray(obj.results) && obj.results.length === 0) return true
  }
  return false
}

export function useCardState(query: MaybeRef<CardQuery>) {
  const status = computed<CardStatus>(() => {
    const s = unref(query)
    if (unref(s.isPending)) return 'loading'
    if (unref(s.isError) && unref(s.data) === undefined) return 'error'
    if (isEmptyData(unref(s.data))) return 'empty'
    return 'data'
  })

  const isStale = computed(() => {
    const s = unref(query)
    return unref(s.isError) && unref(s.data) !== undefined
  })

  const errorCode = computed<CardErrorCode>(() => {
    const s = unref(query)
    if (!unref(s.isError)) return null
    return getErrorCode(unref(s.error))
  })

  const isFetching = computed(() => {
    const s = unref(query)
    if (s.isFetching === undefined) return false
    return unref(s.isFetching)
  })

  const refetch = () => {
    const s = unref(query)
    if (s.refetch === undefined) return undefined
    return unref(s.refetch)()
  }

  return { status, errorCode, isStale, isFetching, refetch }
}
