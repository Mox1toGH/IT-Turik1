import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiOfflineBanner from './UiOfflineBanner.vue'

const meta: Meta<typeof UiOfflineBanner> = {
  title: 'UI/UiOfflineBanner',
  component: UiOfflineBanner,
  tags: ['autodocs'],
  // Uses useConnection composable internally - not directly controllable
}

export default meta
type Story = StoryObj<typeof meta>

/** Default state (shows when online - actually hidden). */
export const Online: Story = {
  render: () => ({
    components: { UiOfflineBanner },
    setup() {
      return {}
    },
    template: `
      <div style="max-width: 600px;">
        <p class="text-muted" style="margin-bottom: 0.5rem;">When online, the banner is hidden.</p>
        <ui-offline-banner />
      </div>
    `,
  }),
}

/** Simulated offline state. */
export const Offline: Story = {
  render: () => ({
    components: { UiOfflineBanner },
    setup() {
      // We can't easily mock useConnection in stories,
      // so this shows the component structure
      return {}
    },
    template: `
      <div style="max-width: 600px;">
        <p class="text-muted" style="margin-bottom: 0.5rem;">Simulated offline state (requires mocked useConnection).</p>
        <div class="offline-banner" role="alert" style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          border: 1px solid var(--border);
          border-radius: 12px;
          background: var(--muted);
          color: var(--foreground);
          font-size: 0.9rem;
          font-weight: 600;
          padding: 0.6rem 0.9rem;
          margin-bottom: 1rem;
        ">
          <span>No connection</span>
          <button class="secondary-btn" style="
            padding: 0.35rem 0.65rem;
            font-size: 0.78rem;
            border-radius: 8px;
            background: var(--secondary);
            color: var(--secondary-foreground);
            border: none;
            cursor: pointer;
          ">
            Try again
          </button>
        </div>
      </div>
    `,
  }),
}
