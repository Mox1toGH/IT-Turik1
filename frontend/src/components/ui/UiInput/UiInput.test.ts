import { describe, it, expect, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiInput from './UiInput.vue'

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
