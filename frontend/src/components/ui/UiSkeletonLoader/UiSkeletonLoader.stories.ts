import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiButton from '@/components/ui/UiButton'

const meta: Meta<typeof UiSkeletonLoader> = {
  title: 'UI/UiSkeletonLoader',
  component: UiSkeletonLoader,
  tags: ['autodocs'],
  argTypes: {
    loading: { control: 'boolean' },
    minWidth: { control: 'text' },
  },
  args: {
    loading: true,
    minWidth: undefined,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Loading state with custom skeleton. */
export const Loading: Story = {
  render: (args) => ({
    components: { UiSkeletonLoader, UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <ui-skeleton-loader v-bind="args" style="max-width: 400px;">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem;">
            <ui-skeleton variant="rounded" width="48px" height="48px" />
            <ui-skeleton width="40%" height="20px" />
            <ui-skeleton width="60%" height="16px" />
          </div>
        </template>
      </ui-skeleton-loader>
    `,
  }),
}

/** Loaded state (shows content). */
export const Loaded: Story = {
  args: { loading: false },
  render: (args) => ({
    components: { UiSkeletonLoader, UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <ui-skeleton-loader v-bind="args" style="max-width: 400px;">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem;">
            <ui-skeleton variant="rounded" width="48px" height="48px" />
            <ui-skeleton width="40%" height="20px" />
            <ui-skeleton width="60%" height="16px" />
          </div>
        </template>
        <div style="padding: 1rem;">
          <h3 style="margin: 0 0 0.5rem;">Loaded Content</h3>
          <p class="text-muted">This is the actual content shown after loading.</p>
        </div>
      </ui-skeleton-loader>
    `,
  }),
}

/** Toggle between loading and loaded. */
export const Toggleable: Story = {
  render: () => ({
    components: { UiSkeletonLoader, UiSkeleton, UiButton },
    setup() {
      const loading = ref(true)
      return { loading }
    },
    template: `
      <div style="max-width: 400px;">
        <ui-button @click="loading = !loading" variant="secondary" size="sm">
          Toggle
        </ui-button>
        <ui-skeleton-loader :loading="loading" style="margin-top: 1rem;">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem;">
              <ui-skeleton variant="rounded" width="48px" height="48px" />
              <ui-skeleton width="40%" height="20px" />
              <ui-skeleton width="60%" height="16px" />
            </div>
          </template>
          <div style="padding: 1rem;">
            <h3 style="margin: 0 0 0.5rem;">Loaded Content</h3>
            <p class="text-muted">Content is now visible.</p>
          </div>
        </ui-skeleton-loader>
      </div>
    `,
  }),
}

/** With custom minWidth. */
export const WithMinWidth: Story = {
  args: { loading: true, minWidth: '300px' },
  render: (args) => ({
    components: { UiSkeletonLoader, UiSkeleton },
    setup() {
      return { args }
    },
    template: `
      <ui-skeleton-loader v-bind="args">
        <template #skeleton>
          <div style="padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem;">
            <ui-skeleton width="100%" height="24px" />
            <ui-skeleton width="80%" height="16px" />
          </div>
        </template>
      </ui-skeleton-loader>
    `,
  }),
}
