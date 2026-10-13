import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { fn } from 'storybook/test'
import UiCardError from './UiCardError.vue'

const meta: Meta<typeof UiCardError> = {
  title: 'UI/UiCardError',
  component: UiCardError,
  tags: ['autodocs'],
  argTypes: {
    errorCode: {
      control: 'select',
      options: [null, 'network', 403, 404, 500],
    },
    title: {
      control: 'text',
    },
    isFetching: {
      control: 'boolean',
    },
  },
  args: {
    errorCode: null,
    title: '',
    isFetching: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Network error (offline). */
export const NetworkError: Story = {
  args: { errorCode: 'network', title: 'teams' },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      const onRetry = fn()
      return { args, onRetry }
    },
    template: `<ui-card-error v-bind="args" @retry="onRetry" style="max-width: 480px" />`,
  }),
}

/** 403 Forbidden - no retry button. */
export const Forbidden: Story = {
  args: { errorCode: 403, title: 'admin panel' },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      return { args }
    },
    template: `<ui-card-error v-bind="args" style="max-width: 480px" />`,
  }),
}

/** 404 Not Found - no retry button. */
export const NotFound: Story = {
  args: { errorCode: 404, title: 'tournament' },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      return { args }
    },
    template: `<ui-card-error v-bind="args" style="max-width: 480px" />`,
  }),
}

/** 500 Server error - with retry button. */
export const ServerError: Story = {
  args: { errorCode: 500, title: 'statistics', isFetching: false },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      const onRetry = fn()
      return { args, onRetry }
    },
    template: `<ui-card-error v-bind="args" style="max-width: 480px" @retry="onRetry" />`,
  }),
}

/** Server error with loading state. */
export const ServerErrorLoading: Story = {
  args: { errorCode: 500, title: 'statistics', isFetching: true },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      const onRetry = fn()
      return { args, onRetry }
    },
    template: `<ui-card-error v-bind="args" style="max-width: 480px" @retry="onRetry" />`,
  }),
}

/** Custom title override. */
export const CustomTitle: Story = {
  args: { errorCode: 500, title: 'Custom error title', isFetching: false },
  render: (args) => ({
    components: { UiCardError },
    setup() {
      const onRetry = fn()
      return { args, onRetry }
    },
    template: `<ui-card-error v-bind="args" style="max-width: 480px" @retry="onRetry" />`,
  }),
}

/** All error codes side by side. */
export const AllErrorCodes: Story = {
  render: () => ({
    components: { UiCardError },
    setup() {
      const codes = [null, 'network', 403, 404, 500] as const
      return { codes }
    },
    template: `
      <div style="display: grid; gap: 1rem; max-width: 600px">
        <ui-card-error v-for="code in codes" :key="code" :error-code="code" :title="code ? 'data' : ''" style="max-width: 280px" />
      </div>
    `,
  }),
}
