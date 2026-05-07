import { describe, it, expect, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiDatePicker from '../UiDatePicker.vue'
import { formatDate } from '../../../lib/date'

const FIXED_DATE = new Date(2026, 3, 10)
const FIXED_DATE_2 = new Date(2026, 3, 20)

const monthNames = Array.from({ length: 12 }, (_, i) =>
  new Intl.DateTimeFormat('uk-UA', { month: 'long' }).format(new Date(2026, i, 1)),
)

describe('UiDatePicker', () => {
  describe('display', () => {
    it('shows placeholder when no date is selected', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, placeholder: 'Pick a date' },
      })

      expect(screen.getByText('Pick a date')).toBeInTheDocument()
    })

    it('shows formatted date when a value is provided', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      expect(screen.getByText(formatDate(FIXED_DATE))).toBeInTheDocument()
    })

    it('shows range placeholder when range mode has no value', async () => {
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: null, placeholder: 'Select range' },
      })

      expect(screen.getByText('Select range')).toBeInTheDocument()
    })

    it('shows formatted range when both start and end are provided', async () => {
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: { start: FIXED_DATE, end: FIXED_DATE_2 } },
      })

      expect(
        screen.getByText(`${formatDate(FIXED_DATE)} – ${formatDate(FIXED_DATE_2)}`),
      ).toBeInTheDocument()
    })

    it('shows open-ended range when only start is selected', async () => {
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: { start: FIXED_DATE, end: null } },
      })

      expect(screen.getByText(`${formatDate(FIXED_DATE)} – ...`)).toBeInTheDocument()
    })
  })

  describe('open / close', () => {
    it('opens the dropdown on trigger click', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await screen.getByRole('button').click()

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('closes the dropdown when clicking outside', async () => {
      const onBlur = vi.fn()
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, onBlur },
      })

      await screen.getByRole('button').click()
      expect(screen.getByRole('dialog').element()).toBeInTheDocument()

      await userEvent.click(document.documentElement)

      await expect.poll(() => screen.getByRole('dialog').query()).not.toBeInTheDocument()
    })

    it('does not open when disabled', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, disabled: true },
      })

      const trigger = screen.getByRole('button')

      expect(trigger).toBeDisabled()
      expect(trigger).toHaveAttribute('aria-expanded', 'false')
      expect(screen.getByRole('dialog').query()).not.toBeInTheDocument()
    })

    it('opens dropdown on Enter key', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await userEvent.keyboard('{Tab}{Enter}')
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('opens dropdown on ArrowDown key', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await userEvent.keyboard('{Tab}{ArrowDown}')

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('closes dropdown on Escape key', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await screen.getByRole('button').click()
      await userEvent.keyboard('{Escape}')

      const blurEmitted = screen.emitted('blur')
      expect(blurEmitted).toBeTruthy()

      await expect.poll(() => screen.getByRole('dialog').query()).not.toBeInTheDocument()
    })
  })

  describe('day selection', () => {
    it('emits selected date and closes dropdown on day click', async () => {
      const onUpdate = vi.fn()
      const onBlur = vi.fn()
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, 'onUpdate:modelValue': onUpdate, onBlur: onBlur },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const dayBtn = days.find(
        (day) => day.element().textContent?.trim() === String(FIXED_DATE.getDate()),
      )
      await dayBtn!.click()

      expect(onUpdate).toHaveBeenLastCalledWith(FIXED_DATE)
      expect(onBlur).toHaveBeenCalled()

      await expect.poll(() => screen.getByRole('dialog').query()).not.toBeInTheDocument()
    })

    it('disables days before minDate', async () => {
      const minDate = new Date(2026, 3, 15)

      const screen = await render(UiDatePicker, {
        props: { modelValue: null, minDate },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const disabledDay = days.find((day) => day.element().textContent?.trim() === '10')
      expect(disabledDay!.element()).toHaveAttribute('disabled')
    })

    it('disables days after maxDate', async () => {
      const maxDate = new Date(2026, 3, 15)

      const screen = await render(UiDatePicker, {
        props: { modelValue: null, maxDate },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const disabledDay = days.find((day) => day.element().textContent?.trim() === '20')
      expect(disabledDay!.element()).toHaveAttribute('disabled')
    })
  })

  describe('navigation', () => {
    it('navigates to next month on arrow click', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByRole('button').click()
      await screen.getByLabelText('Next').click()

      const expectedMonth = monthNames[FIXED_DATE.getMonth() + 1]

      expect(screen.getByText(expectedMonth)).toBeInTheDocument()
    })

    it('navigates to previous month on arrow click', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByRole('button').click()
      await screen.getByLabelText('Previous').click()

      const expectedMonth = monthNames[FIXED_DATE.getMonth() - 1]

      expect(screen.getByText(expectedMonth)).toBeInTheDocument()
    })

    it('switches to month picker view when month button is clicked', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByRole('button').click()

      const currentMonth = monthNames[FIXED_DATE.getMonth()]
      await screen.getByText(currentMonth).click()

      const monthGrid = screen.getByTestId('month-pick-grid')
      expect(monthGrid).toBeInTheDocument()
    })

    it('selects month from month picker and returns to days view', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByRole('button').click()

      const currentMonth = monthNames[FIXED_DATE.getMonth()]
      const btn = screen.getByText(currentMonth)
      await btn.click()

      const monthGrid = screen.getByTestId('month-pick-grid')
      expect(monthGrid).toBeInTheDocument()

      const nextMonth = monthNames[FIXED_DATE.getMonth() + 1].slice(0, 3)
      await screen.getByText(nextMonth).click()

      const daysGrid = screen.getByTestId('day-pick-grid')
      expect(daysGrid).toBeInTheDocument()

      expect(screen.getByText(nextMonth)).toBeInTheDocument()
    })

    it('switches to year picker view when year button is clicked', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByRole('button').click()

      const btn = screen.getByTestId('year-pick-btn')
      await btn.click()

      const yearGrid = screen.getByTestId('year-pick-grid')
      expect(yearGrid).toBeInTheDocument()
    })
  })

  describe('range mode', () => {
    it('selects range start on first click without emitting', async () => {
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: null },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const startBtn = days.find((d) => d.element().textContent?.trim() === '10')
      await startBtn!.click()

      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.emitted('update:modelValue')).toBeFalsy()
    })

    it('emits range and closes dropdown after selecting start and end', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: null, 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const startBtn = days.find((day) => day.element().textContent?.trim() === '10')
      const endBtn = days.find((day) => day.element().textContent?.trim() === '20')

      await startBtn!.click()
      await endBtn!.click()

      expect(onUpdate).toHaveBeenLastCalledWith({ start: expect.any(Date), end: expect.any(Date) })

      const blurEmitted = screen.emitted('blur')
      expect(blurEmitted).toBeTruthy()

      await expect.poll(() => screen.getByRole('dialog').query()).not.toBeInTheDocument()
    })

    it('normalizes range order when end is picked before start chronologically', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiDatePicker, {
        props: { range: true, modelValue: null, 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('button').click()

      const days = screen.getByRole('dialog').getByRole('button').all()
      const laterBtn = days.find((day) => day.element().textContent?.trim() === '20')
      const earlierBtn = days.find((day) => day.element().textContent?.trim() === '10')

      await laterBtn!.click()
      await earlierBtn!.click()

      const { start, end } = onUpdate.mock.lastCall?.[0]
      expect(new Date(start).getTime()).toBeLessThan(new Date(end).getTime())
    })
  })

  describe('invalid state', () => {
    it('indicates invalid state when isInvalid is true', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, isInvalid: true },
      })

      const trigger = screen.getByRole('button').first()
      expect(trigger.element()).toHaveClass('invalid')
      expect(trigger.element()).toHaveAttribute('aria-invalid', 'true')
    })
  })

  describe('accessibility', () => {
    it('sets aria-expanded false on trigger when closed', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      expect(screen.getByRole('button').element()).toHaveAttribute('aria-expanded', 'false')
    })

    it('sets aria-expanded true on trigger when open', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await screen.getByRole('button').click()

      expect(screen.getByRole('button').first().element()).toHaveAttribute('aria-expanded', 'true')
    })

    it('sets aria-haspopup="dialog" on the trigger', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      expect(screen.getByRole('button').element()).toHaveAttribute('aria-haspopup', 'dialog')
    })

    it('renders dialog with aria-label when open', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      await screen.getByRole('button').click()

      expect(screen.getByRole('dialog').element()).toHaveAttribute('aria-label', 'Date picker')
    })
  })
})
