import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiHoverCard from '@/components/ui/UiHoverCard'
import UiButton from '@/components/ui/UiButton'

const meta: Meta<typeof UiHoverCard> = {
  title: 'UI/UiHoverCard',
  component: UiHoverCard,
  tags: ['autodocs'],
  argTypes: {
    side: {
      control: 'select',
      options: ['top', 'right', 'bottom', 'left'],
    },
    align: {
      control: 'select',
      options: ['start', 'center', 'end'],
    },
  },
  args: {
    side: 'top',
    align: 'center',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default hover card (top). */
export const Default: Story = {
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Hover card content</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card on the right side. */
export const Right: Story = {
  args: { side: 'right' },
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Hover card on the right</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card on the bottom side. */
export const Bottom: Story = {
  args: { side: 'bottom' },
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Hover card on the bottom</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card on the left side. */
export const Left: Story = {
  args: { side: 'left' },
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Hover card on the left</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card with align start. */
export const AlignStart: Story = {
  args: { align: 'start' },
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Aligned to start</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card with align end. */
export const AlignEnd: Story = {
  args: { align: 'end' },
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover me</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Aligned to end</p>
      </ui-hover-card>
    `,
  }),
}

/** Hover card with longer content. */
export const LongContent: Story = {
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">Hover for details</ui-button>
        </template>
        <div style="padding: 0.75rem; min-width: 200px;">
          <p style="font-weight: 600; margin-bottom: 0.5rem;">Tournament Info</p>
          <p class="text-muted" style="margin: 0.25rem 0;">Status: Active</p>
          <p class="text-muted" style="margin: 0.25rem 0;">Teams: 12/16</p>
          <p class="text-muted" style="margin: 0.25rem 0;">Starts: 2024-03-15</p>
        </div>
      </ui-hover-card>
    `,
  }),
}

/** Hover card with interactive content (buttons). */
export const WithActions: Story = {
  render: (args) => ({
    components: { UiHoverCard, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-hover-card v-bind="args">
        <template #trigger>
          <ui-button variant="secondary">User menu</ui-button>
        </template>
        <div style="padding: 0.5rem; display: flex; flex-direction: column; gap: 0.35rem; min-width: 160px;">
          <ui-button size="sm" variant="ghost" style="justify-content: flex-start;">Profile</ui-button>
          <ui-button size="sm" variant="ghost" style="justify-content: flex-start;">Settings</ui-button>
          <ui-button size="sm" variant="ghost" style="justify-content: flex-start;">Logout</ui-button>
        </div>
      </ui-hover-card>
    `,
  }),
}
