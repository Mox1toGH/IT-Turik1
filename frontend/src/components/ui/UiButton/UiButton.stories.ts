import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { fn } from 'storybook/test'
import UiButton from './UiButton.vue'

const meta: Meta<typeof UiButton> = {
  title: 'UI/UiButton',
  component: UiButton,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'ghost', 'danger', 'warning', 'link'],
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg'],
    },
    asLink: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
  },
  args: {
    variant: 'default',
    size: 'md',
    asLink: false,
    disabled: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Primary default button. */
export const Default: Story = {
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Default Button</ui-button>`,
  }),
}

/** Secondary variant button. */
export const Secondary: Story = {
  args: { variant: 'secondary' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Secondary</ui-button>`,
  }),
}

/** Ghost variant button. */
export const Ghost: Story = {
  args: { variant: 'ghost' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Ghost</ui-button>`,
  }),
}

/** Danger variant button. */
export const Danger: Story = {
  args: { variant: 'danger' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Danger</ui-button>`,
  }),
}

/** Warning variant button. */
export const Warning: Story = {
  args: { variant: 'warning' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Warning</ui-button>`,
  }),
}

/** Small size button. */
export const Small: Story = {
  args: { size: 'sm' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Small</ui-button>`,
  }),
}

/** Large size button. */
export const Large: Story = {
  args: { size: 'lg' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Large</ui-button>`,
  }),
}

/** Link variant: underlined text, no button chrome. */
export const LinkVariant: Story = {
  args: { variant: 'link', asLink: false },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Link Button</ui-button>`,
  }),
}

/** Link variant combined with asLink, rendering a real router link. */
export const LinkAsRouterLink: Story = {
  args: { variant: 'link', asLink: true, to: '/' },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Navigate home</ui-button>`,
  }),
}

/** Link variant inherits surrounding text styling but keeps the underline. */
export const LinkInSentence: Story = {
  render: () => ({
    components: { UiButton },
    template: `
      <p style="max-width: 420px; color: var(--muted-foreground); font-size: 0.9rem;">
        The update failed.
        <ui-button variant="link" style="color: inherit;">Retry</ui-button>
        to load the latest data.
      </p>
    `,
  }),
}

/** Disabled button. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiButton },
    setup() {
      return { args }
    },
    template: `<ui-button v-bind="args">Disabled</ui-button>`,
  }),
}

/** Button with icon (using slot). */
export const WithIcon: Story = {
  render: () => ({
    components: { UiButton },
    setup() {
      const onClick = fn()
      return { onClick }
    },
    template: `
      <ui-button variant="secondary" size="sm" @click="onClick">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
        Icon Button
      </ui-button>
    `,
  }),
}

/** Full range of variants side by side. */
export const Variants: Story = {
  render: () => ({
    components: { UiButton },
    setup() {
      const variants = ['default', 'secondary', 'ghost', 'danger', 'warning', 'link'] as const
      const sizes = ['xs', 'sm', 'md', 'lg']
      return { variants, sizes }
    },
    template: `
      <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.5rem;">
        <ui-button v-for="variant in variants" :key="variant" :variant="variant">
          {{ variant }}
        </ui-button>
        <ui-button v-for="size in sizes" :key="size" :size="size">
          {{ size }}
        </ui-button>
      </div>
    `,
  }),
}
