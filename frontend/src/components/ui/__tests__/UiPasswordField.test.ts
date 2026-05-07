import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiPasswordField from '../UiPasswordField.vue'

describe('UiPasswordField', () => {
  it('renders a password input by default', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: '' },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('type', 'password')
  })

  it('toggles visibility when the button is clicked', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: 'secret' },
    })

    const button = screen.getByRole('button')
    await button.click()

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('type', 'text')
    expect(button).toHaveAttribute('aria-label', 'Hide password')
    expect(button).toHaveAttribute('aria-pressed', 'true')

    await button.click()
    expect(input).toHaveAttribute('type', 'password')
    expect(button).toHaveAttribute('aria-label', 'Show password')
    expect(button).toHaveAttribute('aria-pressed', 'false')
  })

  it('updates value when the user types', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: '' },
    })

    const input = screen.getByRole('textbox')
    await input.fill('newpassword')

    await expect.element(input).toHaveValue('newpassword')
  })

  it('correctly applies disabled attribute', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: 'secret', disabled: true },
    })

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()

    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })

  it('passes through placeholder attribute to the input', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: '' },
      attrs: { placeholder: 'Enter password' },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('placeholder', 'Enter password')
  })

  it('passes through invalid prop to the input', async () => {
    const screen = await render(UiPasswordField, {
      props: { modelValue: '', isInvalid: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('invalid')
  })
})
