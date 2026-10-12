import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiBadge from './UiBadge.vue'

const meta: Meta<typeof UiBadge> = {
  title: 'UI/UiBadge',
  component: UiBadge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['green', 'gray', 'red', 'orange', 'primary'],
    },
  },
  args: {
    variant: 'gray',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default gray badge. */
export const Default: Story = {
  render: (args) => ({
    components: { UiBadge },
    setup() {
      return { args }
    },
    template: `<ui-badge v-bind="args">Default badge</ui-badge>`,
  }),
}

/** Green success badge. */
export const Green: Story = {
  args: { variant: 'green' },
  render: (args) => ({
    components: { UiBadge },
    setup() {
      return { args }
    },
    template: `<ui-badge v-bind="args">Success</ui-badge>`,
  }),
}

/** Primary badge. */
export const Primary: Story = {
  args: { variant: 'primary' },
  render: (args) => ({
    components: { UiBadge },
    setup() {
      return { args }
    },
    template: `<ui-badge v-bind="args">Primary</ui-badge>`,
  }),
}

/** Red/destructive badge. */
export const Red: Story = {
  args: { variant: 'red' },
  render: (args) => ({
    components: { UiBadge },
    setup() {
      return { args }
    },
    template: `<ui-badge v-bind="args">Error</ui-badge>`,
  }),
}

/** Orange/warning badge. */
export const Orange: Story = {
  args: { variant: 'orange' },
  render: (args) => ({
    components: { UiBadge },
    setup() {
      return { args }
    },
    template: `<ui-badge v-bind="args">Warning</ui-badge>`,
  }),
}

/** All variants side by side. */
export const Variants: Story = {
  render: () => ({
    components: { UiBadge },
    setup() {
      const variants = ['green', 'gray', 'red', 'orange', 'primary'] as const
      return { variants }
    },
    template: `
      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
        <ui-badge v-for="variant in variants" :key="variant" :variant="variant">
          {{ variant }}
        </ui-badge>
      </div>
    `,
  }),
}

/** Badge with longer text. */
export const LongText: Story = {
  render: () => ({
    components: { UiBadge },
    setup() {
      return {}
    },
    template: `
      <ui-badge variant="primary">This is a badge with longer text</ui-badge>
    `,
  }),
}
