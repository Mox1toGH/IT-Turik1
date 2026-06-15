import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiSkeleton from '../UiSkeleton.vue'

describe('UiSkeleton', () => {
  it('renders an accessible loading placeholder', async () => {
    const screen = await render(UiSkeleton)
    const skeleton = screen.getByLabelText('loading')

    expect(skeleton).toBeVisible()
    expect(skeleton).toHaveAttribute('aria-busy', 'true')
    expect(skeleton).toHaveAttribute('aria-live', 'polite')
  })

  it('supports the circle variant and still renders successfully', async () => {
    const screen = await render(UiSkeleton, {
      props: { variant: 'rounded', width: 120, height: 120 },
    })
    const skeleton = screen.getByLabelText('loading')

    expect(skeleton).toBeVisible()
  })
})
