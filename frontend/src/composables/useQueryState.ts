import { computed, toValue, unref, type MaybeRef, type MaybeRefOrGetter } from 'vue'
import type { ErrorResponse } from '@/api/backendAPINinja.schemas'
import type { ErrorType } from '@/lib/apiClient'

export type QueryStatus = 'loading' | 'error' | 'empty' | 'data'
export type QueryErrorCode = number | 'network' | null

/** Decides whether resolved query data should render as the empty state. */
export type EmptyPredicate = (data: unknown) => boolean

export interface QueryStateOptions {
  /**
   * Overrides the default emptiness heuristic (`isEmptyData`).
   *
   * - a predicate replaces the heuristic for the resolved `data`;
   * - `true` / `false` forces the empty state on or off;
   * - omitted (default) keeps the built-in shape detection.
   */
  isEmpty?: boolean | EmptyPredicate
}

/**
 * Structural subset of a vue-query result. Any generated query hook satisfies
 * it, so callers can pass the hook object straight through.
 */
export interface QueryLike {
  isPending: MaybeRef<boolean>
  isError: MaybeRef<boolean>
  data: MaybeRef<unknown>
  error: MaybeRef<unknown>
  isFetching?: MaybeRef<boolean>
  refetch?: MaybeRef<() => unknown>
}

export function getErrorCode(error: unknown): QueryErrorCode {
  const err = error as Partial<ErrorType<ErrorResponse>> | null | undefined
  const status = err?._axiosError?.response?.status
  if (typeof status === 'number') return status
  return 'network'
}

/**
 * Default emptiness heuristic, used when no `isEmpty` override is supplied.
 *
 * Recognised shapes:
 *
 * | Payload             | Empty when             |
 * | ------------------- | ---------------------- |
 * | `T[]`               | `length === 0`         |
 * | `{ total: number }` | `total === 0`          |
 * | `{ items: T[] }`    | `items.length === 0`   |
 * | `{ results: T[] }`  | `results.length === 0` |
 *
 * Everything else is treated as data:
 *
 * - `null` / `undefined` / primitives;
 * - other wrappers, e.g. `{ rankings: [] }` or `{ events: [], rounds: [] }`;
 * - `{ data: [] }` without `total: 0`;
 * - `{ total: 5 }` without an `items` / `results` key.
 *
 * A non-zero `total` does not win over an empty `items` / `results` array.
 */
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

function resolveIsEmpty(data: unknown, override: QueryStateOptions['isEmpty']): boolean {
  if (typeof override === 'function') return override(data)
  if (typeof override === 'boolean') return override
  return isEmptyData(data)
}

/**
 * Interprets a query's lifecycle into display state. Presentation of that state
 * belongs to `UiQueryState`, which consumes this composable.
 */
export function useQueryState(
  query: MaybeRef<QueryLike>,
  options: MaybeRefOrGetter<QueryStateOptions> = {},
) {
  const status = computed<QueryStatus>(() => {
    const s = unref(query)
    if (unref(s.isPending)) return 'loading'
    if (unref(s.isError) && unref(s.data) === undefined) return 'error'
    if (resolveIsEmpty(unref(s.data), toValue(options).isEmpty)) return 'empty'
    return 'data'
  })

  const isStale = computed(() => {
    const s = unref(query)
    return unref(s.isError) && unref(s.data) !== undefined
  })

  const errorCode = computed<QueryErrorCode>(() => {
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
