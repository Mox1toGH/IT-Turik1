import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiSelect from '@/components/ui/UiSelect'

type SelectOption = {
  value: string | number
  label: string
  disabled?: boolean
}

const meta: Meta<typeof UiSelect> = {
  title: 'UI/UiSelect',
  component: UiSelect,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    multiple: { control: 'boolean' },
    isLoading: { control: 'boolean' },
    isError: { control: 'boolean' },
    error: { control: 'text' },
    align: {
      control: 'select',
      options: ['start', 'end', 'center'],
    },
  },
  args: {
    'onUpdate:modelValue': fn(),
    multiple: false,
    isLoading: false,
    isError: false,
    error: '',
    align: 'end',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default select with single option. */
export const Default: Story = {
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
        { value: '3', label: 'Option 3' },
      ])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Select with placeholder. */
export const WithPlaceholder: Story = {
  args: { placeholder: 'Select an option' },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
      ])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Select with loading state. */
export const Loading: Story = {
  args: { isLoading: true },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** Select with error state. */
export const Error: Story = {
  args: { isError: true, error: 'Failed to load options' },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** Multiple select. */
export const Multiple: Story = {
  args: { multiple: true },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
        { value: '3', label: 'Option 3' },
      ])
      const model = ref<string | number[]>([])
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model.length ? model.join(', ') : 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Select with disabled options. */
export const WithDisabledOptions: Story = {
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2', disabled: true },
        { value: '3', label: 'Option 3' },
      ])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Select with align start. */
export const AlignStart: Story = {
  args: { align: 'start' },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
      ])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Select with align center. */
export const AlignCenter: Story = {
  args: { align: 'center' },
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
      ])
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** With many options. */
export const ManyOptions: Story = {
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>(
        Array.from({ length: 20 }, (_, i) => ({
          value: String(i + 1),
          label: `Option ${i + 1}`,
        }))
      )
      const model = ref<string | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** With preselected value. */
export const WithPreselected: Story = {
  render: (args) => ({
    components: { UiSelect },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
        { value: '3', label: 'Option 3' },
      ])
      const model = ref<string | null>('2')
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}
