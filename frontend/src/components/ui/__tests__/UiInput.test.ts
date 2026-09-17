import { describe, it, expect, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiInput from '../UiInput.vue'
import UiNumberInput from '../UiNumberInput.vue'

describe('UiInput', () => {
  it('renders and updates a text value', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiInput, {
      props: { modelValue: '', 'onUpdate:modelValue': onUpdate },
    })

    const input = screen.getByRole('textbox')
    await input.fill('New value')

    expect(input).toHaveValue('New value')
    expect(onUpdate).toHaveBeenCalledWith('New value')
  })

  it('applies invalid state and forwards native attributes', async () => {
    const screen = await render(UiInput, {
      props: { modelValue: '', isInvalid: true },
      attrs: { placeholder: 'Type here', disabled: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('invalid')
    expect(input).toHaveAttribute('placeholder', 'Type here')
    expect(input).toBeDisabled()
  })
})

describe('UiNumberInput', () => {
  it('increments and decrements with steppers', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiNumberInput, {
      props: { modelValue: 5, 'onUpdate:modelValue': onUpdate },
    })

    await screen.getByRole('button', { name: 'Increment' }).click()
    expect(onUpdate).toHaveBeenCalledWith(6)

    await screen.getByRole('button', { name: 'Decrement' }).click()
    expect(onUpdate).toHaveBeenCalledWith(4)
  })

  it('clamps input and keyboard changes to the configured range', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiNumberInput, {
      props: { modelValue: 5, min: 0, max: 10, 'onUpdate:modelValue': onUpdate },
    })

    const input = screen.getByRole('textbox')
    await input.fill('9999')
    expect(onUpdate).toHaveBeenLastCalledWith(10)

    await input.click()
    await userEvent.keyboard('{ArrowDown}')
    expect(onUpdate).toHaveBeenLastCalledWith(9)
  })
})
