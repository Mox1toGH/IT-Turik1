import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import UiCard from './UiCard.vue'
import UiButton from '../UiButton'
import UiSkeleton from '../UiSkeleton'
import type { CardQuery } from '@/composables/useCardState'

const meta: Meta<typeof UiCard> = {
  title: 'UI/UiCard',
  component: UiCard,
  tags: ['autodocs'],
  argTypes: {
    status: {
      control: 'select',
      options: ['loading', 'error', 'empty', 'data'],
    },
    variant: {
      control: 'select',
      options: ['default', 'panel', 'stat', 'hero', 'form', 'actions', 'inset'],
    },
    errorCode: {
      control: 'select',
      options: [null, 'network', 403, 404, 500],
    },
    query: { table: { disable: true } },
  },
  args: {
    status: 'data',
    variant: 'default',
    isFetching: false,
    isStale: false,
    errorCode: null,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Card with slotted header, body and footer in the happy-path state. */
export const Data: Story = {
  render: (args) => ({
    components: { UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 480px">
        <template #header>
          <div>
            <p class="section-eyebrow">Overview</p>
            <h2>Tournament info</h2>
          </div>
        </template>
        <p>Core dates, description, and your progress.</p>
        <template #footer>
          <p class="text-muted">Footer content</p>
        </template>
      </ui-card>
    `,
  }),
}

/** Title/subtitle header rendered by the card itself, with controls and badge slots. */
export const WithTitleHeader: Story = {
  args: {
    title: 'Active tournaments',
    subtitle: 'Filter competitions by name or registration status.',
  },
  render: (args) => ({
    components: { UiCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 560px">
        <template #controls>
          <ui-button size="sm" variant="secondary">Filter</ui-button>
        </template>
        <template #badge>
          <span class="count-pill">12 active</span>
        </template>
        <p>Card body. Badge and controls only render in the data state.</p>
      </ui-card>
    `,
  }),
}

/** Loading state with the default skeleton block. */
export const Loading: Story = {
  args: { status: 'loading' },
  render: (args) => ({
    components: { UiCard },
    setup() {
      return { args }
    },
    template: `<ui-card v-bind="args" title="Teams" style="max-width: 480px" />`,
  }),
}

/** Loading state with a custom skeleton. */
export const LoadingCustomSkeleton: Story = {
  args: { status: 'loading' },
  render: (args) => ({
    components: { UiCard, UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 480px">
        <template #skeleton>
          <div style="display: grid; gap: 0.65rem">
            <ui-skeleton variant="rect" width="45%" />
            <ui-skeleton variant="rect" width="70%" height="48px" />
            <ui-skeleton variant="rect" width="55%" />
          </div>
        </template>
      </ui-card>
    `,
  }),
}

/** Default error UI for a lost connection (no retry while offline). */
export const ErrorNetwork: Story = {
  args: { status: 'error', errorCode: 'network', title: 'teams' },
  render: (args) => ({
    components: { UiCard },
    setup() {
      const onRetry = () => console.log('retry')
      return { args, onRetry }
    },
    template: `<ui-card v-bind="args" style="max-width: 480px" @retry="onRetry" />`,
  }),
}

/** Default error UI for a missing resource (no retry button by design). */
export const ErrorNotFound: Story = {
  args: { status: 'error', errorCode: 404, title: 'tournament' },
  render: (args) => ({
    components: { UiCard },
    setup() {
      return { args }
    },
    template: `<ui-card v-bind="args" style="max-width: 480px" />`,
  }),
}

/** Default error UI for a server failure, with retry. */
export const ErrorServer: Story = {
  args: { status: 'error', errorCode: 500, title: 'statistics', isFetching: false },
  render: (args) => ({
    components: { UiCard },
    setup() {
      const onRetry = () => console.log('retry')
      return { args, onRetry }
    },
    template: `<ui-card v-bind="args" style="max-width: 480px" @retry="onRetry" />`,
  }),
}

/** Custom error slot takes over the default error UI. */
export const ErrorCustomSlot: Story = {
  args: { status: 'error' },
  render: (args) => ({
    components: { UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 480px">
        <template #error>
          <p>Error while fetching tournament teams</p>
        </template>
      </ui-card>
    `,
  }),
}

/** Empty state with helper action. */
export const Empty: Story = {
  args: { status: 'empty', emptyText: 'No tournaments found' },
  render: (args) => ({
    components: { UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 480px">
        <template #empty-action>
          <p class="text-muted">Try changing the search text or status filters.</p>
        </template>
      </ui-card>
    `,
  }),
}

/** Stale data with a failed background update and working retry. */
export const Stale: Story = {
  args: { status: 'data', isStale: true, isFetching: false },
  render: (args) => ({
    components: { UiCard },
    setup() {
      const onRetry = () => console.log('retry')
      return { args, onRetry }
    },
    template: `
      <ui-card v-bind="args" style="max-width: 480px" @retry="onRetry">
        <p>Previously loaded data stays visible under the stale banner.</p>
      </ui-card>
    `,
  }),
}

/** Scrollable card: header and footer stay pinned, only the body scrolls. */
export const Scrollable: Story = {
  render: () => ({
    components: { UiCard },
    setup() {
      const rows = Array.from({ length: 30 }, (_, i) => `Row ${i + 1}`)
      return { rows }
    },
    template: `
      <ui-card scrollable style="max-width: 480px; max-height: 320px">
        <template #header><strong>Pinned header</strong></template>
        <p v-for="row in rows" :key="row" class="text-muted">{{ row }}</p>
        <template #footer><span class="text-muted">Pinned footer</span></template>
      </ui-card>
    `,
  }),
}

/** All visual variants side by side. */
export const Variants: Story = {
  render: () => ({
    components: { UiCard },
    setup() {
      const variants = ['default', 'panel', 'stat', 'hero', 'form', 'actions', 'inset'] as const
      return { variants }
    },
    template: `
      <div style="display: grid; gap: 1rem; max-width: 560px">
        <ui-card v-for="variant in variants" :key="variant" :variant="variant">
          <template #header><strong>{{ variant }}</strong></template>
          <p class="text-muted">Variant body</p>
        </ui-card>
      </div>
    `,
  }),
}

function mockQuery(overrides: Partial<CardQuery> = {}): CardQuery {
  return {
    isPending: ref(false),
    isError: ref(false),
    data: ref([{ id: 1 }]),
    error: ref(null),
    isFetching: ref(false),
    refetch: () => undefined,
    ...overrides,
  }
}

/** Query mode: the card derives its state from a vue-query-style object. */
export const QueryData: Story = {
  render: () => ({
    components: { UiCard },
    setup() {
      const query = mockQuery()
      return { query }
    },
    template: `
      <ui-card :query="query" style="max-width: 480px">
        <p>Loaded via <code>:query</code> — no manual status props needed.</p>
      </ui-card>
    `,
  }),
}

/** Query mode: failed query with retry that recovers after a beat. */
export const QueryErrorRecovery: Story = {
  render: () => ({
    components: { UiCard },
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
      const query: CardQuery = { isPending, isError, data, error, isFetching, refetch }
      return { query }
    },
    template: `
      <ui-card :query="query" title="teams" style="max-width: 480px">
        <p>Recovered data after retry.</p>
      </ui-card>
    `,
  }),
}
