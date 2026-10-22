import { describe, expect, it, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import { defineComponent, h, ref } from 'vue'
import type { QueryLike } from '@/composables/useQueryState'
import UiQueryBlock from './UiQueryBlock.vue'
import UiQueryField from './UiQueryField.vue'

vi.mock('@/composables/useConnection', async () => {
  const { ref } = await import('vue')
  return { useConnection: () => ({ isOnline: ref(false) }) }
})

function makeQuery(overrides: Partial<Record<string, unknown>> = {}) {
  const state = {
    isPending: ref(false),
    isError: ref(false),
    data: ref<unknown>([{ id: 1 }]),
    error: ref<unknown>(null),
    isFetching: ref(false),
    refetch: vi.fn(async () => undefined),
    ...overrides,
  }
  return { state, query: state as unknown as QueryLike }
}

function wrapper(query: QueryLike, defaultSlot?: () => unknown) {
  return defineComponent({
    setup: () => () =>
      h(
        UiQueryBlock,
        { query, title: 'records' },
        {
          skeleton: () => h('i', { 'data-testid': 'obsolete-block-skeleton' }, 'Wrong skeleton'),
          error: ({ retry }: { retry: () => void }) =>
            h('button', { onClick: retry }, 'Custom retry'),
          default:
            defaultSlot ??
            (() => [
              h('h2', { 'data-testid': 'static' }, 'Static heading'),
              h(
                UiQueryField,
                {},
                {
                  skeleton: () => h('i', { 'data-testid': 'field-skeleton' }, 'Field skeleton'),
                  default: () => h('span', { 'data-testid': 'field-content' }, 'Loaded value'),
                },
              ),
            ]),
        },
      ),
  })
}

describe('UiQueryBlock', () => {
  it('renders static content during initial loading and ignores a block skeleton slot', () => {
    const query = makeQuery({ isPending: ref(true), data: ref(undefined) }).query
    const screen = render(wrapper(query))

    expect(screen.getByTestId('static')).toBeInTheDocument()
    expect(screen.getByTestId('field-skeleton')).toBeInTheDocument()
    expect(screen.getByTestId('obsolete-block-skeleton').query()).toBeNull()
  })

  it('allows fields in one block to override inherited loading independently', () => {
    const query = makeQuery({ isPending: ref(true), data: ref(undefined) }).query
    const screen = render(
      wrapper(query, () => [
        h(
          UiQueryField,
          {},
          {
            skeleton: () => h('i', { 'data-testid': 'first-skeleton' }, 'Loading'),
            default: () => h('span', 'First value'),
          },
        ),
        h(
          UiQueryField,
          { loading: false },
          {
            skeleton: () => h('i', { 'data-testid': 'second-skeleton' }, 'Loading'),
            default: () => h('span', { 'data-testid': 'second-value' }, 'Static fallback'),
          },
        ),
      ]),
    )

    expect(screen.getByTestId('first-skeleton')).toBeInTheDocument()
    expect(screen.getByTestId('second-value')).toBeInTheDocument()
    expect(screen.getByTestId('second-skeleton').query()).toBeNull()
  })

  it('renders default content on success', () => {
    const screen = render(wrapper(makeQuery().query))
    expect(screen.getByTestId('static')).toBeInTheDocument()
    expect(screen.getByTestId('field-content')).toBeInTheDocument()
  })

  it('renders custom initial errors and retries', async () => {
    const { query, state } = makeQuery({
      isError: ref(true),
      data: ref(undefined),
      error: ref({ _axiosError: { response: { status: 500 } } }),
    })
    const screen = render(wrapper(query))

    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Custom retry' })).toBeInTheDocument()
    expect(screen.getByTestId('static').query()).toBeNull()
    await screen.getByRole('button', { name: 'Custom retry' }).click()
    expect(state.refetch).toHaveBeenCalledOnce()
  })

  it('renders default error UI and retains offline messaging', () => {
    const query = makeQuery({
      isError: ref(true),
      data: ref(undefined),
      error: ref({ _axiosError: { response: { status: 500 } } }),
    }).query
    const screen = render(
      defineComponent({ setup: () => () => h(UiQueryBlock, { query, title: 'records' }) }),
    )
    expect(screen.getByText('Server unavailable')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()

    const offlineQuery = makeQuery({
      isError: ref(true),
      data: ref(undefined),
      error: ref(new Error('offline')),
    }).query
    const offline = render(
      defineComponent({ setup: () => () => h(UiQueryBlock, { query: offlineQuery }) }),
    )
    expect(offline.getByText('Waiting for connection…')).toBeInTheDocument()
  })

  it('preserves content during background fetching and refetch errors', async () => {
    const { query, state } = makeQuery()
    const screen = render(wrapper(query))

    state.isFetching.value = true
    await expect.poll(() => screen.getByTestId('field-content').query()).toBeInTheDocument()
    expect(screen.getByTestId('static')).toBeInTheDocument()

    state.isFetching.value = false
    state.isError.value = true
    await expect.poll(() => screen.getByText('Update failed').query()).toBeInTheDocument()
    expect(screen.getByTestId('field-content')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('provides reactive query state and nested blocks isolate fields', async () => {
    const outer = makeQuery({ isPending: ref(true), data: ref(undefined) })
    const inner = makeQuery()
    const screen = render(
      defineComponent({
        setup: () => () =>
          h(
            UiQueryBlock,
            { query: outer.query },
            {
              default: () => [
                h(
                  UiQueryField,
                  {},
                  {
                    skeleton: () => h('i', { 'data-testid': 'outer-skeleton' }),
                    default: () => h('span', 'Outer data'),
                  },
                ),
                h(
                  UiQueryBlock,
                  { query: inner.query },
                  {
                    default: () =>
                      h(
                        UiQueryField,
                        {},
                        {
                          skeleton: () => h('i', { 'data-testid': 'inner-skeleton' }),
                          default: () =>
                            h('span', { 'data-testid': 'inner-content' }, 'Inner data'),
                        },
                      ),
                  },
                ),
              ],
            },
          ),
      }),
    )

    expect(screen.getByTestId('outer-skeleton')).toBeInTheDocument()
    expect(screen.getByTestId('inner-content')).toBeInTheDocument()
    expect(screen.getByTestId('inner-skeleton').query()).toBeNull()

    outer.state.isPending.value = false
    outer.state.data.value = [{ id: 2 }]
    await expect.poll(() => screen.getByText('Outer data').query()).toBeInTheDocument()
  })

  it('leaves empty-state decisions to the consumer', () => {
    const query = makeQuery({ data: ref([]) }).query
    const screen = render(
      wrapper(query, () => [h('p', { 'data-testid': 'consumer-empty' }, 'No teams; join one.')]),
    )
    expect(screen.getByTestId('consumer-empty')).toBeInTheDocument()
  })
})
