import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiCard from './UiCard.vue'

describe('UiCard', () => {
  it('renders default slot content', async () => {
    const screen = render(UiCard, {
      slots: { default: 'Card content' },
    })

    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders title and subtitle in the default header', async () => {
    const screen = render(UiCard, {
      props: { title: 'Tournaments', subtitle: 'Active competitions' },
    })

    expect(screen.getByText('Tournaments')).toBeInTheDocument()
    expect(screen.getByText('Active competitions')).toBeInTheDocument()
  })

  it('omits the subtitle element when no subtitle is provided', async () => {
    const screen = render(UiCard, {
      props: { title: 'Tournaments' },
    })

    expect(screen.container.querySelector('.card-subtitle')).toBeNull()
  })

  it('renders a header only when the header slot is provided', async () => {
    const withHeader = render(UiCard, {
      slots: { header: 'Header text' },
    })

    expect(withHeader.getByText('Header text')).toBeInTheDocument()

    const withoutHeader = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutHeader.container.querySelector('.card-header')).toBeNull()
    expect(withoutHeader.getByText('Body content')).toBeInTheDocument()
  })

  it('renders a footer only when the footer slot is provided', async () => {
    const withFooter = render(UiCard, {
      slots: { footer: 'Footer text' },
    })

    expect(withFooter.getByText('Footer text')).toBeInTheDocument()

    const withoutFooter = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutFooter.container.querySelector('.card-footer')).toBeNull()
  })

  it('renders all slots together', async () => {
    const screen = render(UiCard, {
      slots: {
        header: 'Header',
        default: 'Body',
        footer: 'Footer',
      },
    })

    expect(screen.getByText('Header')).toBeInTheDocument()
    expect(screen.getByText('Body')).toBeInTheDocument()
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })

  it('exposes every variant as a modifier class', async () => {
    for (const variant of ['default', 'panel', 'stat', 'hero', 'form', 'inset'] as const) {
      const screen = render(UiCard, {
        props: { variant },
        slots: { default: 'Body' },
      })

      expect(screen.container.querySelector(`.card-${variant}`)).toBeInTheDocument()
    }
  })

  it('applies the scrollable class only when scrollable is true', async () => {
    const scrollable = render(UiCard, {
      props: { scrollable: true },
      slots: { default: 'Body' },
    })
    expect(scrollable.container.querySelector('.card.scrollable')).toBeInTheDocument()

    const fixed = render(UiCard, {
      slots: { default: 'Body' },
    })
    expect(fixed.container.querySelector('.card.scrollable')).toBeNull()
  })

  it('leaves empty-state rendering to UiQueryState', async () => {
    const screen = render(UiCard, {
      props: { status: 'empty', emptyText: 'No rounds added yet' },
      slots: { 'empty-action': '<p>Create the first round to get started.</p>' },
    })

    const card = screen.container.querySelector('.card')
    expect(card).toBeInTheDocument()
    expect(card?.textContent).not.toContain('No rounds added yet')
    expect(card?.textContent).not.toContain('Create the first round to get started.')
  })

  it('keeps base card styling (background, border, radius)', async () => {
    render(UiCard, {
      slots: { default: 'Body' },
    })

    const card = document.querySelector('.card') as HTMLElement
    expect(card).toBeInTheDocument()
    const style = getComputedStyle(card)
    expect(style.backgroundColor).not.toBe('rgba(0, 0, 0, 0)')
    expect(style.borderStyle).not.toBe('none')
  })

  it('scrolls only the body while header and footer stay pinned', async () => {
    render(UiCard, {
      props: { scrollable: true },
      slots: {
        header: 'Header',
        default: 'Body',
        footer: 'Footer',
      },
    })

    const body = document.querySelector('.card > .card-body') as HTMLElement
    expect(body).toBeInTheDocument()
    expect(getComputedStyle(body).overflowY).toBe('auto')
  })

  it('always renders its children and ignores legacy query props', async () => {
    const screen = render(UiCard, {
      props: {
        title: 'Users',
        // Legacy query props must no longer affect rendering.
        status: 'error',
        isFetching: true,
        isStale: true,
        errorCode: 500,
        emptyText: 'Nothing here',
      } as Record<string, unknown>,
      slots: { default: 'Body' },
    })

    expect(screen.getByText('Body')).toBeInTheDocument()
    expect(screen.container.querySelector('[role="alert"]')).toBeNull()
    expect(screen.container.querySelector('.stale-banner')).toBeNull()
  })
})
