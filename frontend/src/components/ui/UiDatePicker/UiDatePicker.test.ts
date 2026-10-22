import { describe, it, expect } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiDatePicker from './UiDatePicker.vue'

const FIXED_DATE = new Date(Date.UTC(2026, 3, 10))

describe('UiDatePicker', () => {
  describe('display', () => {
    it('shows locale placeholder segments when no date is selected', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null },
      })

      const segments = screen.getByRole('spinbutton').all()
      expect(segments.length).toBe(3)
      expect(screen.getByText('дд')).toBeInTheDocument()
      expect(screen.getByText('мм')).toBeInTheDocument()
      expect(screen.getByText('рррр')).toBeInTheDocument()
    })

    it('shows the selected date in segments', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText('04')).toBeInTheDocument()
      expect(screen.getByText('2026')).toBeInTheDocument()
    })

    it('renders a local-midnight Date as the same calendar day', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: new Date(2026, 3, 10) },
      })

      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText('04')).toBeInTheDocument()
      expect(screen.getByText('2026')).toBeInTheDocument()
    })

    it('renders an ISO date string parsed to a Date as the same calendar day', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: new Date('2026-04-10') },
      })

      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText('04')).toBeInTheDocument()
      expect(screen.getByText('2026')).toBeInTheDocument()
    })
  })

  describe('editing', () => {
    it('emits a native Date when the day segment is edited', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: FIXED_DATE },
      })

      await screen.getByText('10').click()
      await userEvent.keyboard('15')

      const emitted = screen.emitted('update:modelValue')
      expect(emitted).toBeTruthy()
      const value = emitted?.[emitted.length - 1]?.[0] as Date
      expect(value).toBeInstanceOf(Date)
      expect(value.getUTCFullYear()).toBe(2026)
      expect(value.getUTCMonth()).toBe(3)
      expect(value.getUTCDate()).toBe(15)
    })
  })

  describe('states', () => {
    it('marks the field invalid when isInvalid is true', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, isInvalid: true },
      })

      expect(screen.getByRole('group')).toBeInTheDocument()
      const field = document.querySelector('.datepicker-field') as HTMLElement
      expect(field.classList.contains('invalid')).toBe(true)
      expect(field).toHaveAttribute('aria-invalid', 'true')
    })

    it('forwards disabled to the field group', async () => {
      const screen = await render(UiDatePicker, {
        props: { modelValue: null, disabled: true },
      })

      expect(screen.getByRole('group').element()).toHaveAttribute('aria-disabled', 'true')
    })
  })
})
