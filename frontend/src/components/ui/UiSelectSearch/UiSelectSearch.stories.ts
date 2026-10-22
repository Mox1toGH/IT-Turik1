import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiSelectSearch from '@/components/ui/UiSelectSearch'

type SelectOption = {
  value: string | number
  label: string
}

const meta: Meta<typeof UiSelectSearch> = {
  title: 'UI/UiSelectSearch',
  component: UiSelectSearch,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    multiple: { control: 'boolean' },
    placeholder: { control: 'text' },
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
    placeholder: 'Select an option',
    isLoading: false,
    isError: false,
    error: '',
    align: 'end',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default single select with search. */
export const Default: Story = {
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Apple' },
        { value: '2', label: 'Banana' },
        { value: '3', label: 'Cherry' },
        { value: '4', label: 'Date' },
        { value: '5', label: 'Elderberry' },
        { value: '6', label: 'Fig' },
        { value: '7', label: 'Grape' },
        { value: '8', label: 'Honeydew' },
      ])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Multiple select with search. */
export const Multiple: Story = {
  args: { multiple: true },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Apple' },
        { value: '2', label: 'Banana' },
        { value: '3', label: 'Cherry' },
        { value: '4', label: 'Date' },
        { value: '5', label: 'Elderberry' },
        { value: '6', label: 'Fig' },
        { value: '7', label: 'Grape' },
      ])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ Array.isArray(model) ? model.join(', ') : 'none' }}
        </p>
      </div>
    `,
  }),
}

/** With placeholder. */
export const WithPlaceholder: Story = {
  args: { placeholder: 'Search for a fruit...' },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Apple' },
        { value: '2', label: 'Banana' },
        { value: '3', label: 'Cherry' },
      ])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** Loading state. */
export const Loading: Story = {
  args: { isLoading: true },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** Error state. */
export const Error: Story = {
  args: { isError: true, error: 'Failed to load options' },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** With many options (search is useful). */
export const ManyOptions: Story = {
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>(
        Array.from({ length: 50 }, (_, i) => ({
          value: String(i + 1),
          label: `Option ${i + 1}`,
        }))
      )
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Selected: {{ model || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Align start. */
export const AlignStart: Story = {
  args: { align: 'start' },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
      ])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}

/** Align center. */
export const AlignCenter: Story = {
  args: { align: 'center' },
  render: (args) => ({
    components: { UiSelectSearch },
    setup() {
      const options = ref<SelectOption[]>([
        { value: '1', label: 'Option 1' },
        { value: '2', label: 'Option 2' },
      ])
      const model = ref<string | number | null>(null)
      return { args, options, model }
    },
    template: `
      <div style="max-width: 320px;">
        <ui-select-search v-bind="args" v-model="model" :options="options" />
      </div>
    `,
  }),
}
