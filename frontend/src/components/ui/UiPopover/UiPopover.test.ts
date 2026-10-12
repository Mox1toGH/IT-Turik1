import { describe, it, expect } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiPopover from './UiPopover.vue'

// NOTE: the trigger slot relies on Reka's native toggle (like production
// callers do). Wiring @click="toggle" on trigger content fights Reka's own
// toggle and produces double emits, so trigger slots here stay plain.
const triggerSlot = '<button data-testid="trigger">Open</button>'
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

    it('shows default slot content when opened', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      expect(screen.getByTestId('content')).toBeInTheDocument()
    })
  })

  describe('open / close', () => {
    it('opens the content in a portal on trigger click', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      await expect.poll(() =>
        document.body.querySelector('[data-testid="content"]'),
      ).not.toBeNull()
    })

    it('closes when trigger is clicked again', async () => {
      const screen = await render(UiPopover, {
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      await screen.getByTestId('trigger').click()

      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
    })

    it('stays open on Escape when closeOnEsc is false', async () => {
      const screen = await render(UiPopover, {
        props: { closeOnEsc: false },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()
      await userEvent.keyboard('{Escape}')

      expect(screen.getByTestId('content')).toBeInTheDocument()
    })

    it('follows the external v-model', async () => {
      const screen = await render(UiPopover, {
        props: { modelValue: false },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.rerender({ modelValue: true })
      expect(screen.getByTestId('content')).toBeInTheDocument()

      await screen.rerender({ modelValue: false })
      await expect.poll(() => screen.getByTestId('content').query()).not.toBeInTheDocument()
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
      expect(screen.emitted('close')).toHaveLength(1)
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
  })

  describe('props', () => {
    it('applies width style to content', async () => {
      const screen = await render(UiPopover, {
        props: { width: '300px' },
        slots: { trigger: triggerSlot, default: contentSlot },
      })

      await screen.getByTestId('trigger').click()

      const content = screen.getByTestId('content').element().closest('.popover-content') as HTMLElement
      expect(content?.style.width).toBe('300px')
    })
  })
})
