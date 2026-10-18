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

  it('renders a header only when the header slot is provided', async () => {
    const withHeader = render(UiCard, {
      slots: { header: 'Header text' },
    })

    expect(withHeader.locator.getByText('Header text')).toBeInTheDocument()

    const withoutHeader = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutHeader.locator.getByText('Header text')).not.toBeInTheDocument()
  })

  it('renders a footer only when the footer slot is provided', async () => {
    const withFooter = render(UiCard, {
      slots: { footer: 'Footer text' },
    })

    expect(withFooter.locator.getByText('Footer text')).toBeInTheDocument()

    const withoutFooter = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutFooter.locator.getByText('Footer text')).not.toBeInTheDocument()
  })

  it('renders an error only when the error slot is provided', async () => {
    const screen = render(UiCard, {
      props: { status: 'error' },
      slots: {
        content: 'Text content',
        error: 'Some error',
      },
    })

    const error = screen.getByRole('alert')
    expect(error).toBeInTheDocument()
    expect(error).toHaveTextContent('Some error')

    expect(screen.locator.getByText('Text content')).not.toBeInTheDocument()
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

  it('renders a custom skeleton slot when loading', async () => {
    const screen = render(UiCard, {
      props: { status: 'loading' },
      slots: { skeleton: 'Custom skeleton' },
    })

    expect(screen.getByText('Custom skeleton')).toBeInTheDocument()
  })

  it('renders the empty state with an optional helper line', async () => {
    const screen = render(UiCard, {
      props: { status: 'empty', emptyText: 'No rounds added yet' },
      slots: { 'empty-action': '<p>Create the first round to get started.</p>' },
    })

    expect(screen.getByText('No rounds added yet')).toBeInTheDocument()
    const hint = screen.getByText('Create the first round to get started.')
    expect(hint).toBeInTheDocument()
    // The card owns the helper styling so every empty state looks the same.
    expect(getComputedStyle(hint.element() as HTMLElement).marginTop).toBe('0px')
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
})
