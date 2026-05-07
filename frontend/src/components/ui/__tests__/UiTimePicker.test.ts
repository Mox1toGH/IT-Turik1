import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import { userEvent } from 'vitest/browser'
import TimePicker from '../UiTimePicker.vue'

describe('TimePicker', () => {
  it('renders correctly with initial value', async () => {
    const screen = await render(TimePicker, {
      props: { modelValue: '12:30' },
    })

    const input = screen.getByPlaceholder('00:00')
    await expect.element(input).toHaveValue('12:30')
  })

  it('opens dropdown on click', async () => {
    const screen = await render(TimePicker, {
      props: { modelValue: '10:00' },
    })

    const input = screen.getByPlaceholder('00:00')
    await input.click()

    const dropdown = screen.getByRole('dialog')
    await expect.element(dropdown).toBeVisible()
  })

  it('updates value when a time option is clicked', async () => {
    const screen = await render(TimePicker, {
      props: {
        modelValue: '08:00',
        'onUpdate:modelValue': (e) => screen.rerender({ modelValue: e }),
      },
    })

    await screen.getByPlaceholder('00:00').click()

    const hour10 = screen.getByText('10').first()
    await hour10.click()

    const minute45 = screen.getByText('45')
    await minute45.click()

    const input = screen.getByPlaceholder('00:00')
    expect(input).toHaveValue('10:45')
  })

  it('formats input value correctly while typing', async () => {
    const screen = await render(TimePicker, {
      props: {
        modelValue: '',
        'onUpdate:modelValue': (e) => screen.rerender({ modelValue: e }),
      },
    })

    const input = screen.getByPlaceholder('00:00')
    await userEvent.type(input, '1234')

    expect(input).toHaveValue('12:34')
  })

  it('navigates through time using arrow keys', async () => {
    const screen = await render(TimePicker, {
      props: {
        modelValue: '12:00',
        'onUpdate:modelValue': (e) => screen.rerender({ modelValue: e }),
      },
    })

    const input = screen.getByPlaceholder('00:00')
    await input.click()

    await userEvent.keyboard('{ArrowDown}')
    expect(input).toHaveValue('13:00')

    await userEvent.keyboard('{ArrowRight}')
    await userEvent.keyboard('{ArrowUp}')
    expect(input).toHaveValue('13:59')
  })

  it('closes dropdown on Escape key', async () => {
    const screen = await render(TimePicker, {
      props: { modelValue: '12:00' },
    })

    const input = screen.getByPlaceholder('00:00')
    await input.click()

    expect(screen.getByRole('dialog')).toBeVisible()

    await userEvent.keyboard('{Escape}')
    await expect.poll(() => screen.getByRole('dialog')).not.toBeInTheDocument()
  })

  it('shows invalid state when prop is passed', async () => {
    const screen = await render(TimePicker, {
      props: { modelValue: '12:00', isInvalid: true },
    })

    const input = screen.getByPlaceholder('00:00')
    expect(input).toHaveClass('invalid')
  })

  it('prevents entering values greater than 23:59', async () => {
    const screen = await render(TimePicker, {
      props: {
        modelValue: '',
        'onUpdate:modelValue': (e) => screen.rerender({ modelValue: e }),
      },
    })

    const input = screen.getByPlaceholder('00:00')

    await userEvent.type(input, '9999')
    expect(input).toHaveValue('23:59')
  })
})
