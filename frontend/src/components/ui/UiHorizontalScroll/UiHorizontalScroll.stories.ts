import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiHorizontalScroll from './UiHorizontalScroll.vue'
import UiCard from '../UiCard'
import UiButton from '../UiButton/index.ts'
import UiBadge from '../UiBadge/index.ts'

const meta: Meta<typeof UiHorizontalScroll> = {
  title: 'UI/UiHorizontalScroll',
  component: UiHorizontalScroll,
  tags: ['autodocs'],
  argTypes: {
    leftLabel: { control: 'text' },
    rightLabel: { control: 'text' },
    role: { control: 'text' },
    contentClass: { control: 'text' },
  },
  args: {
    leftLabel: 'Scroll left',
    rightLabel: 'Scroll right',
    role: undefined,
    contentClass: '',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default horizontal scroll with cards. */
export const Default: Story = {
  render: (args) => ({
    components: { UiHorizontalScroll, UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-card v-for="i in 8" :key="i" variant="stat" style="min-width: 180px;">
          <template #header>Card {{ i }}</template>
          <p class="text-muted">Content for card {{ i }}</p>
        </ui-card>
      </ui-horizontal-scroll>
    `,
  }),
}

/** With buttons. */
export const WithButtons: Story = {
  render: (args) => ({
    components: { UiHorizontalScroll, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-button v-for="i in 10" :key="i" size="sm" variant="secondary" style="white-space: nowrap;">
          Button {{ i }}
        </ui-button>
      </ui-horizontal-scroll>
    `,
  }),
}

/** With badges. */
export const WithBadges: Story = {
  render: (args) => ({
    components: { UiHorizontalScroll, UiBadge },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-badge v-for="i in 15" :key="i" :variant="['green', 'gray', 'red', 'orange', 'primary'][i % 5]">
          Badge {{ i }}
        </ui-badge>
      </ui-horizontal-scroll>
    `,
  }),
}

/** With custom labels. */
export const CustomLabels: Story = {
  args: { leftLabel: 'Previous', rightLabel: 'Next' },
  render: (args) => ({
    components: { UiHorizontalScroll, UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-card v-for="i in 6" :key="i" style="min-width: 200px;">
          <template #header>Item {{ i }}</template>
          <p class="text-muted">Custom navigation labels</p>
        </ui-card>
      </ui-horizontal-scroll>
    `,
  }),
}

/** With many items. */
export const ManyItems: Story = {
  render: (args) => ({
    components: { UiHorizontalScroll, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-button v-for="i in 20" :key="i" size="sm" variant="ghost" style="white-space: nowrap;">
          Item {{ i }}
        </ui-button>
      </ui-horizontal-scroll>
    `,
  }),
}

/** With custom content class. */
export const CustomContentClass: Story = {
  args: { contentClass: 'gap-4' },
  render: (args) => ({
    components: { UiHorizontalScroll, UiCard },
    setup() {
      return { args }
    },
    template: `
      <ui-horizontal-scroll v-bind="args" style="max-width: 600px;">
        <ui-card v-for="i in 5" :key="i" variant="hero" style="min-width: 220px;">
          <template #header>Hero {{ i }}</template>
          <p class="text-muted">With custom gap</p>
        </ui-card>
      </ui-horizontal-scroll>
    `,
  }),
}
