import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiProgressBar from './UiProgressBar.vue'
import UiButton from '../UiButton'

const meta: Meta<typeof UiProgressBar> = {
  title: 'UI/UiProgressBar',
  component: UiProgressBar,
  tags: ['autodocs'],
  argTypes: {
    percent: { control: 'number', min: 0, max: 100 },
    height: { control: 'number', min: 4 },
    fillColor: { control: 'text' },
  },
  args: {
    percent: 50,
    height: 12,
    fillColor: 'var(--muted-foreground)',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default progress bar at 50%. */
export const Default: Story = {
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** 0% progress. */
export const Zero: Story = {
  args: { percent: 0 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** 25% progress. */
export const TwentyFive: Story = {
  args: { percent: 25 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** 75% progress. */
export const SeventyFive: Story = {
  args: { percent: 75 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** 100% progress (complete). */
export const Complete: Story = {
  args: { percent: 100 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Custom fill color (green). */
export const GreenFill: Story = {
  args: { percent: 60, fillColor: 'var(--chart-2)' },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Custom fill color (red). */
export const RedFill: Story = {
  args: { percent: 80, fillColor: 'var(--chart-4)' },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Custom fill color (blue). */
export const BlueFill: Story = {
  args: { percent: 40, fillColor: 'var(--chart-1)' },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Thin progress bar. */
export const Thin: Story = {
  args: { percent: 50, height: 6 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Thick progress bar. */
export const Thick: Story = {
  args: { percent: 50, height: 20 },
  render: (args) => ({
    components: { UiProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Interactive demo with controls. */
export const Interactive: Story = {
  render: () => ({
    components: { UiProgressBar, UiButton },
    setup() {
      const percent = ref(30)
      const increment = fn()
      const decrement = fn()
      const reset = fn()
      return { percent, increment, decrement, reset }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-progress-bar :percent="percent" style="margin-bottom: 1rem;" />
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <ui-button size="sm" variant="secondary" @click="decrement; percent = Math.max(0, percent - 10)">
            -10%
          </ui-button>
          <ui-button size="sm" variant="secondary" @click="increment; percent = Math.min(100, percent + 10)">
            +10%
          </ui-button>
          <ui-button size="sm" variant="ghost" @click="reset; percent = 0">
            Reset
          </ui-button>
        </div>
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current: {{ percent }}%
        </p>
      </div>
    `,
  }),
}

/** All percentages side by side. */
export const AllPercentages: Story = {
  render: () => ({
    components: { UiProgressBar },
    setup() {
      const percentages = [0, 10, 25, 50, 75, 90, 100]
      return { percentages }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 0.75rem; max-width: 480px;">
        <ui-progress-bar v-for="p in percentages" :key="p" :percent="p" :height="8" />
      </div>
    `,
  }),
}
