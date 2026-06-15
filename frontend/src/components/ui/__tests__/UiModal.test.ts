import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import { userEvent } from 'vitest/browser'
import UiModal from '../UiModal.vue'

describe('UiModal', () => {
  it('does not render when modelValue is false', async () => {
    const screen = await render(UiModal, { props: { modelValue: false } })
    expect(screen.getByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders modal content when modelValue is true', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: { default: 'Hello' },
    })
    const dialog = screen.getByRole('dialog')
    await expect.element(dialog).toBeVisible()
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('renders title slot when provided and hides header otherwise', async () => {
    const screenWithTitle = await render(UiModal, {
      props: { modelValue: true },
      slots: { title: '<h2>Title</h2>' },
    })

    expect(screenWithTitle.getByRole('heading', { level: 2 })).toBeInTheDocument()
    screenWithTitle.unmount()

    const screenWithoutTitle = await render(UiModal, {
      props: { modelValue: true },
    })
    expect(screenWithoutTitle.getByRole('heading')).not.toBeInTheDocument()
  })

  it('renders footer slot only when provided', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: { footer: '<button>Confirm</button>' },
    })
    const button = screen.getByRole('button', { name: 'Confirm' })
    await expect.element(button).toBeVisible()
  })

  it('emits update:modelValue and close when the close button is clicked', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: { title: '<h2>Test</h2>' },
    })

    const closeButton = screen.getByRole('button', { name: 'Close' })
    await closeButton.click()

    expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([false])
  })

  it('closes when the backdrop is clicked', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: {
        default: '<p>Some body</p>',
      },
    })

    const backdrop = screen.getByTestId('modal-backdrop')
    expect(backdrop).toBeVisible()
    await userEvent.click(backdrop, {
      position: { x: 23, y: 23 },
    })

    expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([false])
  })

  it('keeps the modal open when the modal card is clicked', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
    })

    const modalCard = screen.getByRole('dialog')
    await modalCard.click()

    expect(screen.emitted()).not.toHaveProperty('update:modelValue')
  })

  it('closes when Escape is pressed', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
    })

    await userEvent.keyboard('{Escape}')

    expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([false])
  })

  it('exposes accessible dialog attributes', async () => {
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: { title: '<h2>Accessible</h2>' },
    })
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('renders safely with long title content', async () => {
    const longTitle = 'A'.repeat(120)
    const screen = await render(UiModal, {
      props: { modelValue: true },
      slots: { title: `<h2>${longTitle}</h2>` },
    })
    const heading = screen.getByRole('heading', { level: 2 })
    expect(heading).toHaveTextContent(longTitle)
  })
})
