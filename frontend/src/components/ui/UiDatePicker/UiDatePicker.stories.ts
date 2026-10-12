import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiDatePicker from '@/components/ui/UiDatePicker'

const meta: Meta<typeof UiDatePicker> = {
  title: 'UI/UiDatePicker',
  component: UiDatePicker,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
    isInvalid: { control: 'boolean' },
    minDate: { control: 'date' },
    maxDate: { control: 'date' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    placeholder: 'Pick a date',
    disabled: false,
    isInvalid: false,
    minDate: undefined,
    maxDate: undefined,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Fixed date for consistent stories. */
const FIXED_DATE = new Date('2024-06-15')

/** Default date picker. */
export const Default: Story = {
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(FIXED_DATE)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }}
        </p>
      </div>
    `,
  }),
}

/** Date picker with placeholder. */
export const WithPlaceholder: Story = {
  args: { placeholder: 'Select date' },
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(FIXED_DATE)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }}
        </p>
      </div>
    `,
  }),
}

/** Disabled date picker. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(FIXED_DATE)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }} (disabled)
        </p>
      </div>
    `,
  }),
}

/** Invalid date picker. */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(FIXED_DATE)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }}
        </p>
      </div>
    `,
  }),
}

/** Date picker with min/max dates. */
export const WithMinMax: Story = {
  args: {
    minDate: new Date('2024-01-01'),
    maxDate: new Date('2024-12-31'),
  },
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(FIXED_DATE)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }}
        </p>
      </div>
    `,
  }),
}

/** Empty date picker (no value selected). */
export const Empty: Story = {
  render: (args) => ({
    components: { UiDatePicker },
    setup() {
      const value = ref<Date | null>(null)
      return { args, value }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-date-picker v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value ? value.getFullYear() + '-' + String(value.getMonth() + 1).padStart(2, '0') + '-' + String(value.getDate()).padStart(2, '0') : 'null' }}
        </p>
      </div>
    `,
  }),
}
