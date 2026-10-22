import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiTextArea from '@/components/ui/UiTextArea'

const meta: Meta<typeof UiTextArea> = {
  title: 'UI/UiTextArea',
  component: UiTextArea,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    isInvalid: { control: 'boolean' },
    placeholder: { control: 'text' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    isInvalid: false,
    placeholder: '',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default textarea. */
export const Default: Story = {
  render: (args) => ({
    components: { UiTextArea },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-text-area v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Length: {{ value.length }} characters
        </p>
      </div>
    `,
  }),
}

/** Textarea with initial value. */
export const WithValue: Story = {
  render: (args) => ({
    components: { UiTextArea },
    setup() {
      const value = ref(
        'This is a pre-filled textarea with some content.\nIt can have multiple lines.',
      )
      return { args, value }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-text-area v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Length: {{ value.length }} characters
        </p>
      </div>
    `,
  }),
}

/** Invalid state. */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiTextArea },
    setup() {
      const value = ref('This field has an error')
      return { args, value }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-text-area v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Length: {{ value.length }} characters
        </p>
      </div>
    `,
  }),
}

/** Long text to test resizing. */
export const LongText: Story = {
  render: (args) => ({
    components: { UiTextArea },
    setup() {
      const value = ref(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
      )
      return { args, value }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-text-area v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Length: {{ value.length }} characters
        </p>
      </div>
    `,
  }),
}

/** With placeholder. */
export const WithPlaceholder: Story = {
  args: { placeholder: 'Enter your description here...' },
  render: (args) => ({
    components: { UiTextArea },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-text-area v-bind="args" v-model="value" />
      </div>
    `,
  }),
}
