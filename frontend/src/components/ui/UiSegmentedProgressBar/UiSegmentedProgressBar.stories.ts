import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiSegmentedProgressBar from './UiSegmentedProgressBar.vue'

const meta: Meta<typeof UiSegmentedProgressBar> = {
  title: 'UI/UiSegmentedProgressBar',
  component: UiSegmentedProgressBar,
  tags: ['autodocs'],
  argTypes: {
    percent: { control: 'number', min: 0, max: 100 },
    height: { control: 'number', min: 4 },
    ariaLabel: { control: 'text' },
  },
  args: {
    percent: 75,
    height: 12,
    ariaLabel: 'Segmented progress',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default segmented progress bar. */
export const Default: Story = {
  args: {
    segments: [
      { id: 1, widthPercent: 30, title: 'Segment A (30%)', color: '#3b82f6' },
      { id: 2, widthPercent: 25, title: 'Segment B (25%)', color: '#22c55e' },
      { id: 3, widthPercent: 20, title: 'Segment C (20%)', color: '#f59e0b' },
      { id: 4, widthPercent: 25, title: 'Segment D (25%)', color: '#ef4444' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Equal segments. */
export const EqualSegments: Story = {
  args: {
    percent: 100,
    segments: [
      { id: 1, widthPercent: 25, title: 'Q1' },
      { id: 2, widthPercent: 25, title: 'Q2' },
      { id: 3, widthPercent: 25, title: 'Q3' },
      { id: 4, widthPercent: 25, title: 'Q4' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Two segments. */
export const TwoSegments: Story = {
  args: {
    percent: 60,
    segments: [
      { id: 1, widthPercent: 40, title: 'Completed (40%)', color: '#22c55e' },
      { id: 2, widthPercent: 60, title: 'Remaining (60%)', color: '#e5e7eb' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Five segments with custom colors. */
export const FiveSegments: Story = {
  args: {
    percent: 85,
    segments: [
      { id: 1, widthPercent: 20, title: 'Design', color: '#8b5cf6' },
      { id: 2, widthPercent: 20, title: 'Development', color: '#3b82f6' },
      { id: 3, widthPercent: 20, title: 'Testing', color: '#f59e0b' },
      { id: 4, widthPercent: 20, title: 'Deploy', color: '#22c55e' },
      { id: 5, widthPercent: 20, title: 'Review', color: '#ef4444' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Partial progress (percent < 100). */
export const PartialProgress: Story = {
  args: {
    percent: 45,
    segments: [
      { id: 1, widthPercent: 50, title: 'Phase 1', color: '#3b82f6' },
      { id: 2, widthPercent: 50, title: 'Phase 2', color: '#22c55e' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Thin height. */
export const Thin: Story = {
  args: {
    height: 6,
    percent: 70,
    segments: [
      { id: 1, widthPercent: 30, title: 'A', color: '#3b82f6' },
      { id: 2, widthPercent: 40, title: 'B', color: '#22c55e' },
      { id: 3, widthPercent: 30, title: 'C', color: '#f59e0b' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Thick height. */
export const Thick: Story = {
  args: {
    height: 24,
    percent: 80,
    segments: [
      { id: 1, widthPercent: 25, title: 'Step 1', color: '#8b5cf6' },
      { id: 2, widthPercent: 35, title: 'Step 2', color: '#3b82f6' },
      { id: 3, widthPercent: 40, title: 'Step 3', color: '#22c55e' },
    ],
  },
  render: (args) => ({
    components: { UiSegmentedProgressBar },
    setup() {
      return { args }
    },
    template: `<ui-segmented-progress-bar v-bind="args" style="max-width: 480px;" />`,
  }),
}
