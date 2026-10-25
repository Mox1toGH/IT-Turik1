import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiSegmentedProgressBar from './UiSegmentedProgressBar.vue'

const segments = [
  { id: 'a', widthPercent: 50, title: 'Alpha' },
  { id: 'b', widthPercent: 50, title: 'Beta', color: '#ff0000' },
]

describe('UiSegmentedProgressBar', () => {
  it('renders one block per segment with the custom color when provided', async () => {
    const screen = await render(UiSegmentedProgressBar, {
      props: { percent: 50, segments },
    })

    const beta = screen.getByTitle('Beta').element() as HTMLElement
    expect(beta.style.width).toBe('50%')
    expect(beta.style.backgroundColor).toBe('rgb(255, 0, 0)')
  })

  it('falls back to the palette when a segment has no color', async () => {
    const screen = await render(UiSegmentedProgressBar, {
      props: { percent: 50, segments },
    })

    const alpha = screen.getByTitle('Alpha').element() as HTMLElement
    expect(alpha.style.backgroundColor).toBe('var(--chart-1)')
  })

  it('uses the default accessible label unless overridden', async () => {
    const screen = await render(UiSegmentedProgressBar, {
      props: { percent: 50, segments },
    })

    expect(screen.getByRole('img', { name: 'Segmented progress' })).toBeInTheDocument()
  })

  it('clamps the used width above 100 and below 0', async () => {
    const over = await render(UiSegmentedProgressBar, {
      props: { percent: 250, segments },
    })
    const overUsed = over.getByRole('img').element().querySelector('.used') as HTMLElement
    expect(overUsed.style.width).toBe('100%')
    over.unmount()

    const under = await render(UiSegmentedProgressBar, {
      props: { percent: -10, segments },
    })
    const underUsed = under.getByRole('img').element().querySelector('.used') as HTMLElement
    expect(underUsed.style.width).toBe('0%')
  })
})
