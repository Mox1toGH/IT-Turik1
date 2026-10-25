import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import { defineComponent, h } from 'vue'
import UiErrorBoundary from './UiErrorBoundary.vue'

describe('UiErrorBoundary', () => {
  it('renders slot content when nothing throws', async () => {
    const screen = await render(UiErrorBoundary, {
      slots: { default: 'All good' },
    })

    expect(screen.getByText('All good')).toBeInTheDocument()
  })

  it('shows the fallback when a child throws during render', async () => {
    const Boom = defineComponent({
      setup() {
        throw new Error('boom')
      },
    })
    const screen = await render({
      components: { UiErrorBoundary, Boom },
      template: '<ui-error-boundary><Boom /></ui-error-boundary>',
    })

    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('recovers after retry when the child stops throwing', async () => {
    let shouldThrow = true
    const Flaky = defineComponent({
      setup() {
        if (shouldThrow) throw new Error('boom')
        return () => h('p', 'Recovered')
      },
    })
    const screen = await render({
      components: { UiErrorBoundary, Flaky },
      template: '<ui-error-boundary><Flaky /></ui-error-boundary>',
    })

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    shouldThrow = false
    await screen.getByRole('button', { name: 'Try again' }).click()

    expect(screen.getByText('Recovered')).toBeInTheDocument()
  })
})
