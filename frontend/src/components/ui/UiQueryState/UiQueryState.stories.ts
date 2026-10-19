import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiQueryState from './UiQueryState.vue'
import UiCard from '../UiCard'
import UiSkeleton from '../UiSkeleton'
import UiButton from '../UiButton'
import type { QueryLike } from '@/composables/useQueryState'

const meta: Meta<typeof UiQueryState> = {
  title: 'UI/UiQueryState',
  component: UiQueryState,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
Renders the lifecycle of a Vue Query result: **loading → error → empty → data**, with stale-data
support and retry.

### Default empty detection

When \`:is-empty\` is omitted, resolved data is treated as empty only for these shapes:

| Payload             | Empty when             |
| ------------------- | ---------------------- |
| \`T[]\`               | \`length === 0\`         |
| \`{ total: number }\` | \`total === 0\`          |
| \`{ items: T[] }\`    | \`items.length === 0\`   |
| \`{ results: T[] }\`  | \`results.length === 0\` |

Everything else renders as data, including \`null\`, \`{ rankings: [] }\`,
\`{ events: [], rounds: [] }\`, \`{ data: [] }\` (without \`total: 0\`) and \`{ total: 5 }\`.
A non-zero \`total\` does not win over an empty \`items\` / \`results\` array.

### Custom emptiness

\`:is-empty\` overrides the heuristic per call site:

- pass a predicate \`(data) => boolean\` to replace it — e.g.
  \`:is-empty="(d) => d.rankings?.length === 0"\`;
- pass \`true\` / \`false\` to force the empty state on or off
  (e.g. \`:is-empty="rankings.length === 0 || isNotReady"\`).

The \`empty\` / \`empty-action\` slots and \`empty-text\` prop are unchanged.
        `,
      },
    },
  },
  argTypes: {
    query: { table: { disable: true } },
    title: { control: 'text' },
    emptyText: { control: 'text' },
    isEmpty: { control: false },
  },
}

export default meta
type Story = StoryObj<typeof meta>

function mockQuery(overrides: Partial<Record<string, unknown>> = {}): QueryLike {
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

/** Loading state with a custom skeleton. */
export const Loading: Story = {
  render: () => ({
    components: { UiQueryState, UiSkeleton },
    setup() {
      const query = mockQuery({ isPending: true, data: ref(undefined) })
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem;">
            <ui-skeleton variant="rounded" width="48px" height="48px" />
            <ui-skeleton width="40%" height="20px" />
            <ui-skeleton width="60%" height="16px" />
          </div>
        </template>
        <div style="padding: 1rem;">Content</div>
      </ui-query-state>
    `,
  }),
}

/** Data state. */
export const Data: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery()
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <p style="padding: 1rem;">Loaded content.</p>
      </ui-query-state>
    `,
  }),
}

/** Default error UI for a lost connection. */
export const ErrorNetwork: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const refetch = fn()
      const query = mockQuery({
        isError: true,
        data: ref(undefined),
        error: ref(new Error('Network Error')),
        refetch,
      })
      return { query }
    },
    template: `<ui-query-state :query="query" title="teams" style="max-width: 400px;" />`,
  }),
}

/** Default error UI for a missing resource — no retry button by design. */
export const ErrorNotFound: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({
        isError: true,
        data: ref(undefined),
        error: ref({ _axiosError: { response: { status: 404 } } }),
      })
      return { query }
    },
    template: `<ui-query-state :query="query" title="tournament" style="max-width: 400px;" />`,
  }),
}

/** Custom error slot takes over the default error UI. */
export const ErrorCustomSlot: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({
        isError: true,
        data: ref(undefined),
        error: ref({ _axiosError: { response: { status: 500 } } }),
      })
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <template #error>
          <p>Error while fetching tournament teams</p>
        </template>
      </ui-query-state>
    `,
  }),
}

/** The error slot also receives the derived state as slot props. */
export const ErrorCustomSlotProps: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({
        isError: true,
        data: ref(undefined),
        error: ref({ _axiosError: { response: { status: 500 } } }),
      })
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <template #error="{ errorCode, retry }">
          <p>Failed to load teams (code: {{ errorCode }})</p>
          <button @click="retry">Retry</button>
        </template>
      </ui-query-state>
    `,
  }),
}

/** Empty state with a helper action. */
export const Empty: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({ data: ref([]) })
      return { query }
    },
    template: `
      <ui-query-state :query="query" empty-text="No tournaments found" style="max-width: 400px;">
        <template #empty-action>
          <p class="text-muted">Try changing the search text or status filters.</p>
        </template>
      </ui-query-state>
    `,
  }),
}

/** `:is-empty` predicate for payloads the default heuristic does not recognise. */
export const CustomEmptyPredicate: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({ data: ref({ rankings: [] }) })
      const isEmpty = (data: unknown) => (data as { rankings?: unknown[] }).rankings?.length === 0
      return { query, isEmpty }
    },
    template: `
      <ui-query-state
        :query="query"
        :is-empty="isEmpty"
        empty-text="No leaderboard data yet"
        style="max-width: 400px;"
      >
        <p>Leaderboard table</p>
      </ui-query-state>
    `,
  }),
}

/** `:is-empty="false"` keeps a default-empty payload rendered as data. */
export const EmptySuppressed: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({ data: ref([]) })
      return { query }
    },
    template: `
      <ui-query-state :query="query" :is-empty="false" style="max-width: 400px;">
        <p>The empty list still renders as content.</p>
      </ui-query-state>
    `,
  }),
}

/** Stale data with a failed background update and a working retry. */
export const Stale: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({
        isError: true,
        data: ref([{ id: 1 }]),
        error: ref({ _axiosError: { response: { status: 500 } } }),
        refetch: fn(),
      })
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <p>Previously loaded data stays visible under the stale banner.</p>
      </ui-query-state>
    `,
  }),
}

/** Background fetching keeps existing data visible, dimmed. */
export const BackgroundFetching: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery({ isFetching: true })
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <p>Data stays mounted while refreshing.</p>
      </ui-query-state>
    `,
  }),
}

/** The state is derived from a vue-query-style object. */
export const QueryData: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const query = mockQuery()
      return { query }
    },
    template: `
      <ui-query-state :query="query" style="max-width: 400px;">
        <p>Loaded via <code>:query</code> — no manual status props needed.</p>
      </ui-query-state>
    `,
  }),
}

/** Failed query with retry that recovers after a beat. */
export const QueryErrorRecovery: Story = {
  render: () => ({
    components: { UiQueryState },
    setup() {
      const isPending = ref(false)
      const isError = ref(true)
      const isFetching = ref(false)
      const data = ref<unknown>(undefined)
      const error = ref<unknown>({ _axiosError: { response: { status: 500 } } })
      const refetch = () => {
        isFetching.value = true
        setTimeout(() => {
          isFetching.value = false
          isError.value = false
          error.value = null
          data.value = [{ id: 1 }]
        }, 800)
      }
      const query: QueryLike = { isPending, isError, data, error, isFetching, refetch }
      return { query }
    },
    template: `
      <ui-query-state :query="query" title="teams" style="max-width: 400px;">
        <p>Recovered data after retry.</p>
      </ui-query-state>
    `,
  }),
}

/** Composed inside a card — the two components stay independent. */
export const ComposedInsideCard: Story = {
  render: () => ({
    components: { UiQueryState, UiCard, UiSkeleton },
    setup() {
      const query = mockQuery({ isPending: true, data: ref(undefined) })
      return { query }
    },
    template: `
      <ui-card title="Tournaments" variant="panel" style="max-width: 480px">
        <ui-query-state :query="query" empty-text="No tournaments yet">
          <template #skeleton>
            <div style="display: grid; gap: 0.65rem">
              <ui-skeleton variant="rect" width="45%" />
              <ui-skeleton variant="rect" width="70%" height="48px" />
            </div>
          </template>
          <p>Tournament list goes here.</p>
        </ui-query-state>
      </ui-card>
    `,
  }),
}

/** Toggle loading and loaded states to inspect the transition. */
export const Toggleable: Story = {
  render: () => ({
    components: { UiQueryState, UiButton },
    setup() {
      const isPending = ref(true)
      const query = mockQuery({ isPending, data: ref(undefined) })
      return { isPending, query }
    },
    template: `
      <div style="max-width: 400px;">
        <ui-button @click="isPending = !isPending" variant="secondary" size="sm">Toggle</ui-button>
        <ui-query-state :query="query" style="margin-top: 1rem;">
          <template #skeleton>
            <div style="padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem;">
              <div class="skeleton" style="width: 100%; height: 24px;"></div>
              <div class="skeleton" style="width: 80%; height: 16px;"></div>
            </div>
          </template>
          <div style="padding: 1rem;">
            <h3 style="margin: 0 0 0.5rem;">Loaded Content</h3>
            <p class="text-muted">Content is now visible.</p>
          </div>
        </ui-query-state>
      </div>
    `,
  }),
}
