import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import UiButton from '@/components/ui/UiButton'

const meta: Meta<typeof UiConfirmModal> = {
  title: 'UI/UiConfirmModal',
  component: UiConfirmModal,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text' },
    message: { control: 'text' },
    confirmText: { control: 'text' },
    cancelText: { control: 'text' },
    confirmVariant: {
      control: 'select',
      options: ['default', 'danger', 'secondary'],
    },
    loading: { control: 'boolean' },
    maxWidth: { control: 'text' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    title: 'Confirm Action',
    message: 'Are you sure you want to continue? This action cannot be undone.',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmVariant: 'default',
    loading: false,
    maxWidth: '400px',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Closed confirm modal - click button to open. */
export const Closed: Story = {
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Confirm Modal</ui-button>
        <ui-confirm-modal
          v-bind="args"
          v-model="isOpen"
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}

/** Default confirm modal with trigger button. */
export const Default: Story = {
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true" variant="secondary">Open Confirm Dialog</ui-button>
        <ui-confirm-modal
          v-bind="args"
          v-model="isOpen"
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}

/** Danger variant for destructive actions. */
export const Danger: Story = {
  args: {
    title: 'Delete Tournament',
    message:
      'This will permanently delete the tournament and all its data. This action cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    confirmVariant: 'danger',
  },
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true" variant="danger">Delete Tournament</ui-button>
        <ui-confirm-modal
          v-bind="args"
          v-model="isOpen"
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}

/** Secondary variant. */
export const Secondary: Story = {
  args: {
    confirmVariant: 'secondary',
  },
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true" variant="secondary">Open Secondary</ui-button>
        <ui-confirm-modal
          v-bind="args"
          v-model="isOpen"
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}

/** With custom button labels. */
export const CustomLabels: Story = {
  args: {
    confirmText: 'Yes, do it',
    cancelText: 'No, go back',
  },
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open with Custom Labels</ui-button>
        <ui-confirm-modal
          v-bind="args"
          v-model="isOpen"
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}

/** With custom slot content. */
export const WithSlotContent: Story = {
  render: (args) => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { args, isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open with Custom Content</ui-button>
        <ui-confirm-modal v-bind="args" v-model="isOpen" @confirm="onConfirm" @cancel="onCancel">
          <p style="color: var(--muted-foreground); margin: 0.5rem 0;">
            Additional custom content can go here via the default slot.
          </p>
          <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
          </ul>
        </ui-confirm-modal>
      </div>
    `,
  }),
}

/** Controlled modal with v-model. */
export const Controlled: Story = {
  render: () => ({
    components: { UiConfirmModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onConfirm = fn()
      const onCancel = fn()
      return { isOpen, onConfirm, onCancel }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Controlled Modal</ui-button>
        <ui-confirm-modal
          v-model="isOpen"
          title="Controlled Modal"
          message="This modal is controlled via v-model."
          @confirm="onConfirm"
          @cancel="onCancel"
        />
      </div>
    `,
  }),
}
