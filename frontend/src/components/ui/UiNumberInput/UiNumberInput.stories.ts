import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiNumberInput from '@/components/ui/UiNumberInput'

const meta: Meta<typeof UiNumberInput> = {
  title: 'UI/UiNumberInput',
  component: UiNumberInput,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    isInvalid: { control: 'boolean' },
    min: { control: 'text' },
    max: { control: 'text' },
    step: { control: 'number' },
    disabled: { control: 'boolean' },
    required: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    isInvalid: false,
    min: undefined,
    max: undefined,
    step: 1,
    disabled: false,
    required: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default number input. */
export const Default: Story = {
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('0')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** With initial value. */
export const WithValue: Story = {
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('42')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** With min and max. */
export const WithMinMax: Story = {
  args: { min: '0', max: '100' },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('50')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (min: 0, max: 100)
        </p>
      </div>
    `,
  }),
}

/** With custom step (5). */
export const StepFive: Story = {
  args: { step: 5 },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('10')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (step: 5)
        </p>
      </div>
    `,
  }),
}

/** With step 0.1 for decimals. */
export const DecimalStep: Story = {
  args: { step: 0.1, min: '0', max: '10' },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('3.5')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (step: 0.1)
        </p>
      </div>
    `,
  }),
}

/** Invalid state. */
export const Invalid: Story = {
  args: { isInvalid: true },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('invalid')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }}
        </p>
      </div>
    `,
  }),
}

/** Disabled state. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('42')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (disabled)
        </p>
      </div>
    `,
  }),
}

/** Required field. */
export const Required: Story = {
  args: { required: true },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value || '(empty)' }} (required)
        </p>
      </div>
    `,
  }),
}

/** Negative numbers allowed. */
export const NegativeNumbers: Story = {
  args: { min: '-100', max: '100' },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('-25')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (range: -100 to 100)
        </p>
      </div>
    `,
  }),
}

/** At minimum boundary. */
export const AtMin: Story = {
  args: { min: '0', max: '100' },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('0')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (at min)
        </p>
      </div>
    `,
  }),
}

/** At maximum boundary. */
export const AtMax: Story = {
  args: { min: '0', max: '100' },
  render: (args) => ({
    components: { UiNumberInput },
    setup() {
      const value = ref('100')
      return { args, value }
    },
    template: `
      <div style="max-width: 200px;">
        <ui-number-input v-bind="args" v-model="value" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Value: {{ value }} (at max)
        </p>
      </div>
    `,
  }),
}
