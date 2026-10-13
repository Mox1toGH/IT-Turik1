import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiProgressBar from './UiProgressBar.vue'

describe('UiProgressBar', () => {
  it('renders the fill width and accessible value', async () => {
    const screen = await render(UiProgressBar, {
      props: { percent: 40 },
    })

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveAttribute('aria-valuenow', '40')
  })

  it('clamps values above 100 and below 0', async () => {
    const over = await render(UiProgressBar, {
      props: { percent: 150 },
    })
    expect(over.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100')
    over.unmount()

    const under = await render(UiProgressBar, {
      props: { percent: -20 },
    })
    expect(under.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')
  })

  it('applies the height prop to the track', async () => {
    const screen = await render(UiProgressBar, {
      props: { percent: 40, height: 20 },
    })

    expect(screen.getByRole('progressbar').element().style.height).toBe('20px')
  })
})
