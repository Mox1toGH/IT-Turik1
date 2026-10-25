import { describe, it, expect } from 'vitest'
import UiButton from './UiButton.vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import { render } from 'vitest-browser-vue'

const createTestRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })

describe('UiButton', () => {
  it('renders as a native button by default', () => {
    const screen = render(UiButton, {
      slots: { default: 'Submit' },
    })

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Submit')
    expect(button).toHaveAttribute('type', 'button')
  })

  it('forwards native attributes to the button', () => {
    const screen = render(UiButton, {
      attrs: { disabled: true },
      slots: { default: 'Disabled' },
    })

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('renders the link variant as underlined text with no button chrome', () => {
    const screen = render(UiButton, {
      props: { variant: 'link' },
      slots: { default: 'Retry' },
    })

    const button = screen.getByRole('button', { name: 'Retry' })
    expect(button).toHaveClass('link-btn')

    const style = getComputedStyle(button.element())
    expect(style.textDecorationLine).toContain('underline')
    expect(style.backgroundColor).toBe('rgba(0, 0, 0, 0)')
  })

  it('renders as a link when asLink is true', async () => {
    const router = createTestRouter()

    const screen = render(UiButton, {
      props: { asLink: true, to: '/target' },
      global: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        plugins: [router as any],
      },
      slots: { default: 'Navigate' },
    })

    const link = screen.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent('Navigate')
    expect(link).toHaveAttribute('href', '/target')

    await link.click()
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/target')
  })
})
