import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiTextArea from '../UiTextArea.vue'

describe('UiTextArea', () => {
  it('renders the provided modelValue', async () => {
    const screen = await render(UiTextArea, {
      props: { modelValue: 'Hello' },
    })

    const input = screen.getByRole('textbox')
    expect(input).toBeVisible()
    expect(input).toHaveValue('Hello')
  })

  it('updates value when the user types', async () => {
    const screen = await render(UiTextArea, {
      props: { modelValue: '' },
    })

    const input = screen.getByRole('textbox')
    await input.fill('New value')

    expect(input).toHaveValue('New value')
  })

  it('applies invalid prop correctly', async () => {
    const screen = await render(UiTextArea, {
      props: { modelValue: '', isInvalid: true },
      attrs: { placeholder: 'Type here', disabled: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('invalid')
  })

  it('forwards native text-area attributes', async () => {
    const screen = await render(UiTextArea, {
      props: { modelValue: '' },
      attrs: { placeholder: 'Type here', rows: '5', disabled: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('placeholder', 'Type here')
    expect(input).toHaveAttribute('rows', '5')
    expect(input).toBeDisabled()
  })
})
