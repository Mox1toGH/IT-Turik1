import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiErrorBoundary from './UiErrorBoundary.vue'

const meta: Meta<typeof UiErrorBoundary> = {
  title: 'UI/UiErrorBoundary',
  component: UiErrorBoundary,
  tags: ['autodocs'],
  // No controllable props - it's a wrapper that catches errors
}

export default meta
type Story = StoryObj<typeof meta>

/** Error boundary wrapping working content. */
export const Working: Story = {
  render: () => ({
    components: { UiErrorBoundary },
    setup() {
      return {}
    },
    template: `
      <ui-error-boundary>
        <div style="padding: 1rem; background: var(--muted); border-radius: 8px;">
          <p style="margin: 0;">This content renders successfully.</p>
          <p class="text-muted" style="margin: 0.5rem 0 0;">No error captured.</p>
        </div>
      </ui-error-boundary>
    `,
  }),
}

/** Error boundary catching a render error (simulated via error-throwing component). */
export const WithError: Story = {
  render: () => ({
    components: { UiErrorBoundary },
    setup() {
      // Create a component that throws during render
      const ThrowError = {
        setup() {
          throw new Error('Simulated render error')
        },
        render() {
          return null
        },
      }
      return { ThrowError }
    },
    template: `
      <ui-error-boundary>
        <ThrowError />
      </ui-error-boundary>
    `,
  }),
}

/** Multiple error boundaries - one fails, one works. */
export const MultipleBoundaries: Story = {
  render: () => ({
    components: { UiErrorBoundary },
    setup() {
      const ThrowError = {
        setup() {
          throw new Error('Component A failed')
        },
        render() {
          return null
        },
      }
      return { ThrowError }
    },
    template: `
      <div style="display: grid; gap: 1rem; max-width: 600px;">
        <ui-error-boundary>
          <div style="padding: 1rem; background: var(--muted); border-radius: 8px;">
            <p style="margin: 0;">Component A (works)</p>
          </div>
        </ui-error-boundary>
        <ui-error-boundary>
          <ThrowError />
        </ui-error-boundary>
        <ui-error-boundary>
          <div style="padding: 1rem; background: var(--muted); border-radius: 8px;">
            <p style="margin: 0;">Component C (works)</p>
          </div>
        </ui-error-boundary>
      </div>
    `,
  }),
}
