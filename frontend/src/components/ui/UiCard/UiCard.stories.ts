import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiCard from './UiCard.vue'
import UiButton from '../UiButton'
import { UiQueryBlock } from '../../query'

const meta: Meta<typeof UiCard> = {
  title: 'UI/UiCard',
  component: UiCard,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'panel', 'stat', 'hero', 'form', 'inset'],
    },
  },
  args: {
    variant: 'default',
    scrollable: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Card with slotted header, body and footer. */
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

/** Title/subtitle header rendered by the card itself, with a footer action. */
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
        <p>Card body. UiCard is presentational; pair it with UiQueryBlock for query states.</p>
        <template #footer>
          <ui-button size="sm" variant="secondary">Filter</ui-button>
        </template>
      </ui-card>
    `,
  }),
}

/** Every visual variant side by side. */
export const Variants: Story = {
  render: () => ({
    components: { UiCard },
    setup() {
      const variants = ['default', 'panel', 'stat', 'hero', 'form', 'inset'] as const
      return { variants }
    },
    template: `
      <div style="display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); max-width: 720px;">
        <ui-card v-for="variant in variants" :key="variant" :variant="variant" :title="variant">
          <p class="text-muted">Body content.</p>
        </ui-card>
      </div>
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

/** Nested cards are supported — UiCard is a plain layout primitive. */
export const Nested: Story = {
  render: () => ({
    components: { UiCard },
    template: `
      <ui-card title="Team info" style="max-width: 520px">
        <div style="display: grid; gap: 0.75rem; grid-template-columns: repeat(2, minmax(0, 1fr));">
          <ui-card title="Name" variant="inset"><p class="text-muted">Turik FC</p></ui-card>
          <ui-card title="Members" variant="inset"><p class="text-muted">12 people</p></ui-card>
        </div>
      </ui-card>
    `,
  }),
}

/** The header slot replaces the title/subtitle block entirely. */
export const CustomHeaderSlot: Story = {
  render: () => ({
    components: { UiCard, UiButton },
    setup() {
      const onRefresh = fn()
      return { onRefresh }
    },
    template: `
      <ui-card style="max-width: 520px">
        <template #header>
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 1rem;">
            <span class="count-pill">12 active</span>
            <ui-button size="sm" variant="secondary" @click="onRefresh">Refresh</ui-button>
          </div>
        </template>
        <p>Body content.</p>
      </ui-card>
    `,
  }),
}

/** UiCard renders whatever it is given; query states belong to UiQueryBlock. */
export const ComposedWithQueryBlock: Story = {
  render: () => ({
    components: { UiCard, UiQueryBlock },
    setup() {
      const isPending = ref(true)
      const query = {
        isPending,
        isError: ref(false),
        data: ref(undefined),
        error: ref(null),
        isFetching: ref(false),
        refetch: () => undefined,
      }
      return { query }
    },
    template: `
      <ui-card title="Tournaments" variant="panel" style="max-width: 480px">
        <ui-query-block :query="query">
          <template #skeleton>
            <p class="text-muted">Loading tournaments…</p>
          </template>
          <p>12 active tournaments.</p>
        </ui-query-block>
      </ui-card>
    `,
  }),
}
