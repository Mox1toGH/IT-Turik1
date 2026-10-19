import { describe, it, expect, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import { ref, defineComponent, h, type Ref } from 'vue'
import UiQueryState from './UiQueryState.vue'
import type { QueryLike } from '@/composables/useQueryState'

function query(overrides: Partial<Record<string, unknown>> = {}): QueryLike {
  return {
    isPending: ref(false),
    isError: ref(false),
    data: ref([{ id: 1 }]),
    error: ref(null),
    isFetching: ref(false),
    refetch: () => undefined,
    ...overrides,
  } as unknown as QueryLike
}

/** Hosts a reactive query so tests can flip state and rerender. */
function host(initial: QueryLike) {
  const state: { query: Ref<QueryLike>; calls: number } = {
    query: ref(initial),
    calls: 0,
  }

  const Wrapper = defineComponent({
    setup() {
      return () =>
        h(
          UiQueryState,
          { query: state.query.value },
          {
            default: () => 'Content loaded',
            skeleton: () => 'Skeleton block',
            error: () => 'Custom error',
            empty: () => 'Custom empty',
          },
        )
    },
  })

  return { state, Wrapper }
}

describe('UiQueryState', () => {
  it('renders the skeleton slot while the query is pending', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ isPending: true, data: ref(undefined) }) },
      slots: { skeleton: 'Skeleton block', default: 'Content loaded' },
    })

    expect(screen.getByText('Skeleton block')).toBeInTheDocument()
    expect(screen.locator.getByText('Content loaded').query()).toBeNull()
  })

  it('falls back to default skeleton rows when no skeleton slot is given', async () => {
    render(UiQueryState, {
      props: { query: query({ isPending: true, data: ref(undefined) }) },
      slots: { default: 'Content loaded' },
    })

    expect(document.querySelectorAll('.skeleton').length).toBeGreaterThan(0)
  })

  it('renders the default slot when the query has data', async () => {
    const screen = render(UiQueryState, {
      props: { query: query() },
      slots: { skeleton: 'Skeleton block', default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
    expect(screen.locator.getByText('Skeleton block').query()).toBeNull()
  })

  it('renders the empty slot when the query resolves to an empty list', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ data: ref([]) }) },
      slots: { empty: 'Custom empty', default: 'Content loaded' },
    })

    expect(screen.getByText('Custom empty')).toBeInTheDocument()
    expect(screen.locator.getByText('Content loaded').query()).toBeNull()
  })

  it('accepts a custom emptiness predicate', async () => {
    const screen = render(UiQueryState, {
      props: {
        query: query({ data: ref({ rankings: [] }) }),
        isEmpty: (data: unknown) => (data as { rankings: unknown[] }).rankings.length === 0,
      },
      slots: { empty: 'Custom empty', default: 'Content loaded' },
    })

    expect(screen.getByText('Custom empty')).toBeInTheDocument()
    expect(screen.locator.getByText('Content loaded').query()).toBeNull()
  })

  it('can suppress the default emptiness detection', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ data: ref([]) }), isEmpty: false },
      slots: { empty: 'Custom empty', default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
  })

  it('does not treat a null payload as an empty state', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ data: ref(null) }) },
      slots: { empty: 'Custom empty', default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
    expect(screen.locator.getByText('Custom empty').query()).toBeNull()
  })

  it('renders the error slot when the query fails without data', async () => {
    const screen = render(UiQueryState, {
      props: {
        query: query({
          isError: true,
          data: ref(undefined),
          error: ref({ _axiosError: { response: { status: 500 } } }),
        }),
      },
      slots: { error: 'Custom error', default: 'Content loaded' },
    })

    expect(screen.getByText('Custom error')).toBeInTheDocument()
    expect(screen.locator.getByText('Content loaded').query()).toBeNull()
  })

  it('passes the derived error code and retry handler to the error slot', async () => {
    const refetch = vi.fn()
    const screen = render(UiQueryState, {
      props: {
        query: query({
          isError: true,
          data: ref(undefined),
          error: ref({ _axiosError: { response: { status: 503 } } }),
          refetch,
        }),
      },
      slots: {
        error: (slotProps: { errorCode?: unknown; retry?: () => void }) =>
          h('button', { onClick: slotProps.retry }, `code: ${String(slotProps.errorCode)}`),
      },
    })

    await screen.getByRole('button', { name: 'code: 503' }).click()

    expect(refetch).toHaveBeenCalledOnce()
  })

  it('renders the default error UI and retries through the query refetch', async () => {
    const refetch = vi.fn()
    const screen = render(UiQueryState, {
      props: {
        query: query({
          isError: true,
          data: ref(undefined),
          error: ref({ _axiosError: { response: { status: 500 } } }),
          refetch,
        }),
      },
    })

    expect(screen.getByText('Server unavailable')).toBeInTheDocument()

    await screen.getByRole('button', { name: /try again/i }).click()

    expect(refetch).toHaveBeenCalledOnce()
  })

  it('keeps stale content visible and offers a retry when a refetch fails', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ isError: true, data: ref([{ id: 1 }]) }) },
      slots: { default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
    expect(screen.getByText('Update failed')).toBeInTheDocument()
  })

  it('disables the stale retry button while a refetch is in flight', async () => {
    const screen = render(UiQueryState, {
      props: {
        query: query({ isError: true, isFetching: true, data: ref([{ id: 1 }]) }),
      },
      slots: { default: 'Content loaded' },
    })

    const retry = screen.getByRole('button', { name: /retrying/i })
    expect(retry.element()).toHaveProperty('disabled', true)
  })

  it('dims the content while background fetching keeps existing data visible', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ isFetching: true, data: ref([{ id: 1 }]) }) },
      slots: { skeleton: 'Skeleton block', default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
    expect(document.querySelector('.dimmed')).toBeInTheDocument()
    expect(document.querySelector('.is-fetching')).toBeInTheDocument()
  })

  it('shows the empty text fallback when no empty slot is provided', async () => {
    const screen = render(UiQueryState, {
      props: { query: query({ data: ref([]) }), emptyText: 'No teams yet' },
      slots: { default: 'Content loaded' },
    })

    expect(screen.getByText('No teams yet')).toBeInTheDocument()
    expect(screen.locator.getByText('Content loaded').query()).toBeNull()
  })

  it('swaps between skeleton and content without rendering both', async () => {
    const { state, Wrapper } = host(query({ isPending: true, data: ref(undefined) }))
    const screen = render(Wrapper)

    expect(screen.getByText('Skeleton block')).toBeInTheDocument()

    state.query.value = query()

    await expect.poll(() => screen.getByText('Content loaded').query()).toBeInTheDocument()
    await expect.poll(() => screen.getByText('Skeleton block').query()).not.toBeInTheDocument()
  })
})
