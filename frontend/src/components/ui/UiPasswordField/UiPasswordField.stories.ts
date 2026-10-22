import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiPasswordField from '@/components/ui/UiPasswordField'

const meta: Meta<typeof UiPasswordField> = {
  title: 'UI/UiPasswordField',
  component: UiPasswordField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    isInvalid: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    isInvalid: false,
    disabled: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default password field. */
export const Default: Story = {
  render: (args) => ({
    components: { UiPasswordField },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-password-field v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** Password field with value. */
export const WithValue: Story = {
  render: (args) => ({
    components: { UiPasswordField },
    setup() {
      const value = ref('secretpassword123')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-password-field v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** Invalid state. */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiPasswordField },
    setup() {
      const value = ref('short')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-password-field v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}

/** Disabled state. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiPasswordField },
    setup() {
      const value = ref('password123')
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-password-field v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current value: "{{ value }}"
        </p>
      </div>
    `,
  }),
}
