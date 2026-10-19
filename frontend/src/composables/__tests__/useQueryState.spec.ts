import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'
import { getErrorCode, useQueryState } from '../useQueryState'

function query(overrides: Record<string, unknown> = {}) {
  return {
    isPending: ref(false),
    isError: ref(false),
    data: ref<unknown>([{ id: 1 }]),
    error: ref<unknown>(null),
    isFetching: ref(false),
    refetch: ref(() => undefined),
    ...overrides,
  }
}

describe('getErrorCode', () => {
  it('returns the HTTP status from an axios error', () => {
    expect(getErrorCode({ _axiosError: { response: { status: 500 } } })).toBe(500)
  })

  it('falls back to network when there is no HTTP status', () => {
    expect(getErrorCode(new Error('boom'))).toBe('network')
    expect(getErrorCode(null)).toBe('network')
    expect(getErrorCode(undefined)).toBe('network')
  })
})

describe('useQueryState', () => {
  it('is loading while the query is pending', () => {
    const { status } = useQueryState(query({ isPending: ref(true), data: ref(undefined) }))
    expect(status.value).toBe('loading')
  })

  it('is an error when the query failed and has no data', () => {
    const { status } = useQueryState(query({ isError: ref(true), data: ref(undefined) }))
    expect(status.value).toBe('error')
  })

  it('is stale, not error, when the query failed but still has data', () => {
    const q = query({ isError: ref(true), data: ref([{ id: 1 }]) })
    const { status, isStale } = useQueryState(q)

    expect(status.value).toBe('data')
    expect(isStale.value).toBe(true)
  })

  it('detects empty arrays and known paginated shapes', () => {
    expect(useQueryState(query({ data: ref([]) })).status.value).toBe('empty')
    expect(useQueryState(query({ data: ref({ total: 0 }) })).status.value).toBe('empty')
    expect(useQueryState(query({ data: ref({ items: [] }) })).status.value).toBe('empty')
    expect(useQueryState(query({ data: ref({ results: [] }) })).status.value).toBe('empty')
  })

  it('does not treat null or an unrecognised shape as empty', () => {
    expect(useQueryState(query({ data: ref(null) })).status.value).toBe('data')
    expect(useQueryState(query({ data: ref({ total: 5 }) })).status.value).toBe('data')
    expect(useQueryState(query({ data: ref({ rankings: [] }) })).status.value).toBe('data')
  })

  it('uses a custom isEmpty predicate instead of the default heuristic', () => {
    const q = query({ data: ref({ rankings: [] }) })
    const isEmpty = (value: unknown) => (value as { rankings: unknown[] }).rankings.length === 0

    expect(useQueryState(q).status.value).toBe('data')
    expect(useQueryState(q, { isEmpty }).status.value).toBe('empty')
  })

  it('allows forcing the empty state on or off', () => {
    expect(useQueryState(query({ data: ref([]) }), { isEmpty: false }).status.value).toBe('data')
    expect(useQueryState(query({ data: ref([{ id: 1 }]) }), { isEmpty: true }).status.value).toBe(
      'empty',
    )
  })

  it('reacts to a reactive isEmpty override', () => {
    const override = ref<boolean | undefined>(undefined)
    const state = useQueryState(query({ data: ref({ rankings: [] }) }), () => ({
      isEmpty: override.value,
    }))

    expect(state.status.value).toBe('data')
    override.value = true
    expect(state.status.value).toBe('empty')
  })

  it('exposes the error code only while errored', () => {
    const errored = query({
      isError: ref(true),
      data: ref(undefined),
      error: ref({ _axiosError: { response: { status: 404 } } }),
    })
    expect(useQueryState(errored).errorCode.value).toBe(404)

    expect(useQueryState(query()).errorCode.value).toBeNull()
  })

  it('treats a missing isFetching as not fetching', () => {
    const q = query()
    delete (q as Record<string, unknown>).isFetching

    expect(useQueryState(q).isFetching.value).toBe(false)
  })

  it('defaults isFetching to false and calls refetch when present', () => {
    const refetch = vi.fn()
    const state = useQueryState(query({ isFetching: ref(true), refetch }))

    expect(state.isFetching.value).toBe(true)
    state.refetch()
    expect(refetch).toHaveBeenCalledOnce()
  })

  it('returns undefined from refetch when the query exposes none', () => {
    const q = query()
    delete (q as Record<string, unknown>).refetch

    expect(useQueryState(q).refetch()).toBeUndefined()
  })
})
