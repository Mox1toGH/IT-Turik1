import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiSwitch from '@/components/ui/UiSwitch'

const meta: Meta<typeof UiSwitch> = {
  title: 'UI/UiSwitch',
  component: UiSwitch,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    disabled: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    disabled: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default unchecked switch. */
export const Unchecked: Story = {
  render: (args) => ({
    components: { UiSwitch },
    setup() {
      const value = ref(false)
      return { args, value }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 1rem;">
        <ui-switch v-bind="args" v-model="value" />
        <span class="text-muted">Value: {{ value }}</span>
      </div>
    `,
  }),
}

/** Checked switch. */
export const Checked: Story = {
  render: (args) => ({
    components: { UiSwitch },
    setup() {
      const value = ref(true)
      return { args, value }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 1rem;">
        <ui-switch v-bind="args" v-model="value" />
        <span class="text-muted">Value: {{ value }}</span>
      </div>
    `,
  }),
}

/** Disabled switch. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiSwitch },
    setup() {
      const value = ref(true)
      return { args, value }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 1rem;">
        <ui-switch v-bind="args" v-model="value" />
        <span class="text-muted">Value: {{ value }} (disabled)</span>
      </div>
    `,
  }),
}

/** Interactive toggle. */
export const Interactive: Story = {
  render: () => ({
    components: { UiSwitch },
    setup() {
      const value = ref(false)
      return { value }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 1rem;">
        <ui-switch v-model="value" />
        <span class="text-muted">Value: {{ value }}</span>
      </div>
    `,
  }),
}

/** Both states side by side. */
export const BothStates: Story = {
  render: () => ({
    components: { UiSwitch },
    setup() {
      const unchecked = ref(false)
      const checked = ref(true)
      return { unchecked, checked }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 1rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <ui-switch v-model="unchecked" />
          <span class="text-muted">Unchecked: {{ unchecked }}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
          <ui-switch v-model="checked" />
          <span class="text-muted">Checked: {{ checked }}</span>
        </div>
      </div>
    `,
  }),
}
