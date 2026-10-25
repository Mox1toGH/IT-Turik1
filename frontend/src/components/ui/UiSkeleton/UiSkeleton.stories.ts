import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiSkeleton from './UiSkeleton.vue'

const meta: Meta<typeof UiSkeleton> = {
  title: 'UI/UiSkeleton',
  component: UiSkeleton,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['rect', 'rounded'],
    },
    width: { control: 'text' },
    height: { control: 'text' },
  },
  args: {
    variant: 'rect',
    width: '100%',
    height: '24px',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default rectangle skeleton. */
export const Default: Story = {
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `<ui-skeleton v-bind="args" style="max-width: 320px;" />`,
  }),
}

/** Rounded/circle skeleton. */
export const Rounded: Story = {
  args: { variant: 'rounded', width: '48px', height: '48px' },
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `<ui-skeleton v-bind="args" />`,
  }),
}

/** Custom width and height. */
export const CustomSize: Story = {
  args: { width: '200px', height: '100px' },
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `<ui-skeleton v-bind="args" />`,
  }),
}

/** Small rectangle (like text line). */
export const TextLine: Story = {
  args: { width: '60%', height: '16px' },
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `<ui-skeleton v-bind="args" />`,
  }),
}

/** Card-like skeleton. */
export const CardSkeleton: Story = {
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <div style="max-width: 400px; display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem; border: 1px solid var(--border); border-radius: 12px; background: var(--card);">
        <ui-skeleton variant="rounded" width="48px" height="48px" />
        <ui-skeleton width="40%" height="20px" />
        <ui-skeleton width="60%" height="16px" />
        <ui-skeleton width="100%" height="80px" />
      </div>
    `,
  }),
}

/** Multiple lines skeleton. */
export const MultipleLines: Story = {
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <div style="max-width: 400px; display: flex; flex-direction: column; gap: 0.5rem;">
        <ui-skeleton width="80%" height="24px" />
        <ui-skeleton width="100%" height="16px" />
        <ui-skeleton width="65%" height="16px" />
        <ui-skeleton width="45%" height="16px" />
      </div>
    `,
  }),
}

/** Avatar + text skeleton pattern. */
export const AvatarText: Story = {
  render: (args) => ({
    components: { UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 1rem; max-width: 400px;">
        <ui-skeleton variant="rounded" width="48px" height="48px" />
        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
          <ui-skeleton width="40%" height="20px" />
          <ui-skeleton width="60%" height="14px" />
        </div>
      </div>
    `,
  }),
}

/** All variants side by side. */
export const Variants: Story = {
  render: () => ({
    components: { UiSkeleton },
    setup() {
      return {}
    },
    template: `
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <ui-skeleton variant="rect" width="100px" height="24px" />
        <ui-skeleton variant="rounded" width="48px" height="48px" />
      </div>
    `,
  }),
}
