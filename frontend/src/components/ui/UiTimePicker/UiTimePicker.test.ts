import { describe, it, expect } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import TimePicker from './UiTimePicker.vue'

describe('TimePicker', () => {
  describe('display', () => {
    it('shows the model value in hour and minute segments', async () => {
      const screen = await render(TimePicker, {
        props: { modelValue: '12:30' },
      })

      const segments = screen.getByRole('spinbutton').all()
      expect(segments.length).toBe(2)
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText('30')).toBeInTheDocument()
    })
  })

  describe('editing', () => {
    it('emits the edited time formatted as HH:MM', async () => {
      const screen = await render(TimePicker, {
        props: { modelValue: '12:30' },
      })

      await screen.getByText('12').click()
      await userEvent.keyboard('09')

      const emitted = screen.emitted('update:modelValue')
      expect(emitted).toBeTruthy()
      expect(emitted?.[emitted.length - 1]).toStrictEqual(['09:30'])
    })
  })

  describe('states', () => {
    it('marks the field invalid when isInvalid is true', async () => {
      const screen = await render(TimePicker, {
        props: { modelValue: '12:00', isInvalid: true },
      })

      expect(screen.getByRole('group')).toBeInTheDocument()
      const field = document.querySelector('.time-field') as HTMLElement
      expect(field.classList.contains('invalid')).toBe(true)
      expect(field).toHaveAttribute('aria-invalid', 'true')
    })

    it('forwards disabled to the field group', async () => {
      const screen = await render(TimePicker, {
        props: { modelValue: '12:00', disabled: true },
      })

      expect(screen.getByRole('group').element()).toHaveAttribute('aria-disabled', 'true')
    })
  })
})
