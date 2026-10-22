import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiTimePicker from '@/components/ui/UiTimePicker'

const meta: Meta<typeof UiTimePicker> = {
  title: 'UI/UiTimePicker',
  component: UiTimePicker,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    isInvalid: { control: 'boolean' },
    disabled: { control: 'boolean' },
    required: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    isInvalid: false,
    disabled: false,
    required: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default time picker. */
export const Default: Story = {
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('14:30')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** Time picker with different time. */
export const Morning: Story = {
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('09:00')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** Time picker with evening time. */
export const Evening: Story = {
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('18:45')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** Invalid time picker. */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('invalid')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** Disabled time picker. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('12:00')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (disabled)
        </p>
      </div>
    `,
  }),
}

/** Required time picker. */
export const Required: Story = {
  args: { required: true },
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value || '(empty)' }} (required)
        </p>
      </div>
    `,
  }),
}

/** Empty time picker. */
export const Empty: Story = {
  render: (args) => ({
    components: { UiTimePicker },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-time-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value || '(empty)' }}
        </p>
      </div>
    `,
  }),
}
