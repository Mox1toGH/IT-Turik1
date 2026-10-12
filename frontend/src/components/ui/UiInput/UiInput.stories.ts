import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiInput from '@/components/ui/UiInput'

const meta: Meta<typeof UiInput> = {
  title: 'UI/UiInput',
  component: UiInput,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    isInvalid: { control: 'boolean' },
    type: {
      control: 'select',
      options: ['text', 'password', 'email', 'number'],
    },
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    isInvalid: false,
    type: 'text',
    placeholder: '',
    disabled: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default text input. */
export const Default: Story = {
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** Input with error state (invalid). */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('invalid value')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** Password type input. */
export const Password: Story = {
  args: { type: 'password', placeholder: 'Enter password' },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
      </div>
    `,
  }),
}

/** Email type input. */
export const Email: Story = {
  args: { type: 'email', placeholder: 'Enter email' },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
      </div>
    `,
  }),
}

/** Number type input. */
export const NumberInput: Story = {
  args: { type: 'number', placeholder: 'Enter number' },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
      </div>
    `,
  }),
}

/** Input with placeholder. */
export const WithPlaceholder: Story = {
  args: { placeholder: 'Enter your email address' },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
      </div>
    `,
  }),
}

/** Disabled input. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('Cannot edit this')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
      </div>
    `,
  }),
}

/** With initial value. */
export const WithValue: Story = {
  render: (args) => ({
    components: { UiInput },
    setup() {
      const value = ref('Pre-filled value')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** All types side by side. */
export const AllTypes: Story = {
  render: () => ({
    components: { UiInput },
    setup() {
      const types = ['text', 'password', 'email', 'number'] as const
      const values = ref({ text: '', password: '', email: '', number: '' })
      return { types, values }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 0.75rem; max-width: 320px;">
        <ui-input
          v-for="type in types"
          :key="type"
          v-model="values[type]"
          :type="type"
          :placeholder="type"
        />
      </div>
    `,
  }),
}
