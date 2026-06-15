import { describe, it, expect } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiPopover from '../UiPopover.vue'

const triggerSlot = '<button data-testid="trigger" @click="toggle">Open</button>'
const contentSlot = '<div data-testid="content">Popover content</div>'

describe('UiPopover', () => {
  describe('display', () => {
    it('renders trigger slot', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot },
      })

      expect(screen.getByTestId('trigger')).toBeInTheDocument()
    })

    it('does not show content by default', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
    })

    it('shows header when header prop is provided', async () => {
      const screen = await render(UiPopover, {
        props: { header: 'My Header' },
        slots: { trigger: triggerSlot },
      })

      await screen.getByTestId('trigger').click()

      expect(screen.getByText('My Header')).toBeInTheDocument()
    })

    it('does not show header when header prop is not provided', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      expect(screen.getByTestId('content')).toBeInTheDocument()
      await expect.poll(() => screen.getByText(/My Header/).query()).not.toBeInTheDocument()
    })
  })

  describe('open / close', () => {
    it('opens when trigger calls toggle', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      expect(screen.getByTestId('content')).toBeInTheDocument()
    })

    it('closes when trigger calls toggle again', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      await screen.getByTestId('trigger').click()

      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
    })

    it('closes on Escape key', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      expect(screen.getByTestId('content')).toBeInTheDocument()

      await userEvent.keyboard('{Escape}')

      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
    })

    it('does not close on Escape when closeOnEsc is false', async () => {
      const screen = await render(UiPopover, {
        props: { closeOnEsc: false },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      await userEvent.keyboard('{Escape}')

      expect(screen.getByTestId('content')).toBeInTheDocument()
    })

    it('closes on click outside', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      expect(screen.getByTestId('content')).toBeInTheDocument()

      await userEvent.click(document.body)

      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
    })

    it('does not close when clicking inside the popover content', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      await screen.getByTestId('content').click()

      expect(screen.getByTestId('content')).toBeInTheDocument()
    })
  })

  describe('slot close function', () => {
    it('closes when close() is called from default slot', async () => {
      const screen = await render(UiPopover, {
        slots: {
          trigger: triggerSlot,
          default: '<button data-testid="close-btn" @click="close">Close</button>',
        },
      })

      await screen.getByTestId('trigger').click()
      expect(screen.getByTestId('close-btn')).toBeInTheDocument()

      await screen.getByTestId('close-btn').click()

      await expect.poll(() => screen.getByTestId('close-btn').query()).not.toBeInTheDocument()
    })
  })

  describe('emits', () => {
    it('emits open when opened', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot },
      })

      await screen.getByTestId('trigger').click()

      expect(screen.emitted('open')).toHaveLength(1)
    })

    it('emits close when closed', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot },
      })

      await screen.getByTestId('trigger').click()
      await screen.getByTestId('trigger').click()

      expect(screen.emitted('close')).toHaveLength(1)
    })
  })

  describe('props', () => {
    it('applies align class to content', async () => {
      const screen = await render(UiPopover, {
        props: { align: 'end' },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      const content = screen.getByTestId('content').element().closest('.popover-content')
      expect(content).toHaveClass('align-end')
    })

    it('applies side class to content', async () => {
      const screen = await render(UiPopover, {
        props: { side: 'top' },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      const content = screen.getByTestId('content').element().closest('.popover-content')
      expect(content).toHaveClass('side-top')
    })

    it('applies width style to content', async () => {
      const screen = await render(UiPopover, {
        props: { width: '300px' },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      const content = screen
        .getByTestId('content')
        .element()
        .closest('.popover-content') as HTMLElement
      expect(content?.style.width).toBe('300px')
    })
  })
})
