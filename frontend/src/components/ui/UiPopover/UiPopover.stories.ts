import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiPopover from '@/components/ui/UiPopover'
import UiButton from '@/components/ui/UiButton'

const meta: Meta<typeof UiPopover> = {
  title: 'UI/UiPopover',
  component: UiPopover,
  tags: ['autodocs'],
  argTypes: {
    align: {
      control: 'select',
      options: ['start', 'center', 'end'],
    },
    side: {
      control: 'select',
      options: ['bottom', 'top'],
    },
    sideOffset: { control: 'number' },
    width: { control: 'text' },
    minWidth: { control: 'text' },
    maxWidth: { control: 'text' },
    inline: { control: 'boolean' },
    header: { control: 'text' },
    closeOnEsc: { control: 'boolean' },
  },
  args: {
    align: 'start',
    side: 'bottom',
    sideOffset: 6,
    width: undefined,
    minWidth: undefined,
    maxWidth: undefined,
    inline: true,
    header: undefined,
    closeOnEsc: true,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default popover - closed by default, click button to toggle. */
export const Closed: Story = {
  render: (args) => ({
    components: { UiPopover, UiButton },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <ui-button variant="secondary">Toggle Popover</ui-button>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Popover content goes here</p>
      </ui-popover>
    `,
  }),
}

/** Open popover using defaultOpen (for documentation/screenshots). */
export const Open: Story = {
  args: { defaultOpen: true },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      return { args }
    },
    template: `
      <ui-popover v-bind="args">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">Hover or focus me</span>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">This popover is open by default</p>
      </ui-popover>
    `,
  }),
}

/** Popover with header. */
export const WithHeader: Story = {
  args: { header: 'Popover Title' },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">Hover for info</span>
        </template>
        <p style="padding: 0.5rem; min-width: 200px;">Content with a header above.</p>
      </ui-popover>
    `,
  }),
}

/** Popover on the top side. */
export const Top: Story = {
  args: { side: 'top' },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">Hover me (top)</span>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Popover on top</p>
      </ui-popover>
    `,
  }),
}

/** Popover with align center. */
export const AlignCenter: Story = {
  args: { align: 'center' },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">Center aligned</span>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">Center aligned content</p>
      </ui-popover>
    `,
  }),
}

/** Popover with align end. */
export const AlignEnd: Story = {
  args: { align: 'end' },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">End aligned</span>
        </template>
        <p style="padding: 0.5rem; white-space: nowrap;">End aligned content</p>
      </ui-popover>
    `,
  }),
}

/** Popover with custom width. */
export const CustomWidth: Story = {
  args: { width: '300px' },
  render: (args) => ({
    components: { UiPopover },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <span style="border-bottom: 1px dashed var(--muted-foreground); cursor: help;">Wide popover</span>
        </template>
        <div style="padding: 0.5rem;">
          <p style="margin: 0 0 0.5rem; font-weight: 600;">Wide Popover Content</p>
          <p class="text-muted" style="margin: 0;">This popover has a fixed width of 300px, allowing for more content.</p>
        </div>
      </ui-popover>
    `,
  }),
}

/** Popover with interactive content (buttons). */
export const WithActions: Story = {
  render: (args) => ({
    components: { UiPopover, UiButton },
    setup() {
      const isOpen = ref(false)
      const onAction = fn()
      return { args, isOpen, onAction }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <ui-button variant="secondary">User Menu</ui-button>
        </template>
        <div style="padding: 0.5rem; display: flex; flex-direction: column; gap: 0.35rem; min-width: 180px;">
          <ui-button size="sm" variant="ghost" @click="onAction" style="justify-content: flex-start;">Profile</ui-button>
          <ui-button size="sm" variant="ghost" @click="onAction" style="justify-content: flex-start;">Settings</ui-button>
          <ui-button size="sm" variant="danger" @click="onAction" style="justify-content: flex-start;">Logout</ui-button>
        </div>
      </ui-popover>
    `,
  }),
}

/** Controlled popover with v-model - click button to toggle. */
export const Controlled: Story = {
  render: () => ({
    components: { UiPopover, UiButton },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <ui-popover v-model="isOpen" header="Controlled Popover">
        <template #trigger>
          <ui-button>{{ isOpen ? 'Close' : 'Open' }} Popover</ui-button>
        </template>
        <p style="padding: 0.5rem;">This popover is controlled via v-model.</p>
      </ui-popover>
    `,
  }),
}

/** Non-inline (block) popover trigger. */
export const BlockTrigger: Story = {
  args: { inline: false },
  render: (args) => ({
    components: { UiPopover, UiButton },
    setup() {
      const isOpen = ref(false)
      return { args, isOpen }
    },
    template: `
      <ui-popover v-bind="args" v-model="isOpen">
        <template #trigger>
          <ui-button variant="secondary" style="width: 100%;">Block trigger (full width)</ui-button>
        </template>
        <p style="padding: 0.5rem;">Popover with block-level trigger.</p>
      </ui-popover>
    `,
  }),
}
