import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiHorizontalScroll from './UiHorizontalScroll.vue'

const wideContent = Array.from({ length: 20 }, (_, i) => `<div style="flex: 0 0 200px">Item ${i + 1}</div>`).join('')

describe('UiHorizontalScroll', () => {
  it('renders slot content', async () => {
    const screen = await render(UiHorizontalScroll, {
      slots: { default: '<span>Inner</span>' },
    })

    expect(screen.getByText('Inner')).toBeInTheDocument()
  })

  it('shows the right scroll control when content overflows', async () => {
    const screen = await render(UiHorizontalScroll, {
      slots: { default: wideContent },
    })

    await expect
      .poll(() => screen.getByRole('button', { name: 'Scroll right' }).query())
      .not.toBeNull()
  })

  it('scrolls right when the right control is clicked', async () => {
    const screen = await render(UiHorizontalScroll, {
      slots: { default: wideContent },
    })

    const viewport = () =>
      screen.getByText('Item 20').element().closest('.horizontal-scroll-viewport') as HTMLElement

    await screen.getByRole('button', { name: 'Scroll right' }).click()

    await expect.poll(() => viewport().scrollLeft).toBeGreaterThan(0)
  })

  it('shows the left control after scrolling and scrolls back on click', async () => {
    const screen = await render(UiHorizontalScroll, {
      slots: { default: wideContent },
    })

    await screen.getByRole('button', { name: 'Scroll right' }).click()

    const viewport = () =>
      screen.getByText('Item 20').element().closest('.horizontal-scroll-viewport') as HTMLElement
    await expect.poll(() => viewport().scrollLeft).toBeGreaterThan(0)

    const left = screen.getByRole('button', { name: 'Scroll left' })
    expect(left).toBeInTheDocument()

    const scrolled = viewport().scrollLeft
    expect(scrolled).toBeGreaterThan(0)

    await left.click()
    await expect.poll(() => viewport().scrollLeft).toBeLessThan(scrolled)
  })
})
