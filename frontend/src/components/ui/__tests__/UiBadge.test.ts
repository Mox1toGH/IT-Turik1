import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiBadge from '../UiBadge.vue'

describe('UiBadge', () => {
  it('renders slot content correctly', () => {
    const screen = render(UiBadge, {
      slots: { default: 'Badge text' },
    })

    expect(screen.getByText('Badge text')).toBeInTheDocument()
  })

  it('supports the variant prop without breaking rendering', () => {
    const screen = render(UiBadge, {
      props: { variant: 'red' },
      slots: { default: 'Badge text' },
    })

    expect(screen.getByText('Badge text')).toBeInTheDocument()
  })
})
