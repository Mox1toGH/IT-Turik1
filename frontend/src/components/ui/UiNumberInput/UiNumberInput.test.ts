import { describe, it, expect, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiNumberInput from './UiNumberInput.vue'

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

  it('clamps typed input to the configured range', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiNumberInput, {
      props: { modelValue: 5, min: 0, max: 10, 'onUpdate:modelValue': onUpdate },
    })

    const input = screen.getByRole('textbox')
    await input.fill('9999')
    expect(onUpdate).toHaveBeenLastCalledWith(10)
  })

  it('steps from the current value on ArrowDown', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiNumberInput, {
      props: { modelValue: 10, min: 0, max: 10, 'onUpdate:modelValue': onUpdate },
    })

    const input = screen.getByRole('textbox')
    await input.click()
    await userEvent.keyboard('{ArrowDown}')
    expect(onUpdate).toHaveBeenLastCalledWith(9)
  })
})
