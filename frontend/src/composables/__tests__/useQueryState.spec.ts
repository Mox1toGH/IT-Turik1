import { describe, expect, it, vi } from 'vitest'
import { ref, type Ref } from 'vue'
import { getErrorCode, useQueryState, type QueryLike } from '../useQueryState'

function query(overrides: Record<string, unknown> = {}) {
  return {
    isPending: ref(false),
    isError: ref(false),
    data: ref<unknown>([{ id: 1 }]),
    error: ref<unknown>(null),
    isFetching: ref(false),
    refetch: vi.fn(async () => undefined),
    ...overrides,
  } as unknown as QueryLike & {
    data: Ref<unknown>
    isError: Ref<boolean>
    error: Ref<unknown>
  }
}

describe('useQueryState', () => {
  it('distinguishes initial loading from refetching with existing data', () => {
    const initial = query({ isPending: ref(true), data: ref(undefined) })
    const initialState = useQueryState(initial)
    expect(initialState.isInitialLoading.value).toBe(true)
    expect(initialState.isRefetching.value).toBe(false)

    const refetch = query({ isPending: ref(false), isFetching: ref(true) })
    const refetchState = useQueryState(refetch)
    expect(refetchState.isInitialLoading.value).toBe(false)
    expect(refetchState.isRefetching.value).toBe(true)
  })

  it('exposes reactive data and error state', () => {
    const q = query()
    const state = useQueryState(q)
    expect(state.data.value).toEqual([{ id: 1 }])
    expect(state.isError.value).toBe(false)

    q.data.value = undefined
    q.isError.value = true
    q.error.value = { _axiosError: { response: { status: 404 } } }
    expect(state.data.value).toBeUndefined()
    expect(state.isError.value).toBe(true)
    expect(state.errorCode.value).toBe(404)
  })

  it('classifies HTTP and network errors', () => {
    expect(getErrorCode({ _axiosError: { response: { status: 403 } } })).toBe(403)
    expect(getErrorCode(new Error('offline'))).toBe('network')
  })

  it('uses a callable refetch and resolves when one is not available', async () => {
    const refetch = vi.fn(async () => 'updated')
    const state = useQueryState(query({ refetch }))
    await expect(state.refetch()).resolves.toBe('updated')
    expect(refetch).toHaveBeenCalledOnce()

    await expect(useQueryState(query({ refetch: undefined })).refetch()).resolves.toBeUndefined()
  })
})
