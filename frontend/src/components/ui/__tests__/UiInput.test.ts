import { describe, it, expect, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiInput from '../UiInput.vue'

describe('UiInput', () => {
  describe('type: text (default)', () => {
    it('renders the provided modelValue', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: 'Hello' },
      })

      const input = screen.getByRole('textbox')
      expect(input).toBeVisible()
      expect(input).toHaveValue('Hello')
    })

    it('updates value when the user types', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: '' },
      })

      const input = screen.getByRole('textbox')
      await input.fill('New value')
      expect(input).toHaveValue('New value')
    })

    it('applies invalid class when isInvalid is true', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: '', isInvalid: true },
      })

      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('invalid')
    })

    it('does not apply invalid class when isInvalid is false', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: '', isInvalid: false },
      })

      const input = screen.getByRole('textbox')
      expect(input).not.toHaveClass('invalid')
    })

    it('forwards native input attributes', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: '' },
        attrs: { placeholder: 'Type here', disabled: true },
      })

      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('placeholder', 'Type here')
      expect(input).toBeDisabled()
    })

    it('emits update:modelValue when user types', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: '', 'onUpdate:modelValue': onUpdate },
      })

      const input = screen.getByRole('textbox')
      await input.fill('abc')
      expect(onUpdate).toHaveBeenCalled()
    })
  })

  describe('type: number', () => {
    it('renders increment and decrement buttons', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number' },
      })

      expect(screen.getByRole('button', { name: 'Increment' })).toBeVisible()
      expect(screen.getByRole('button', { name: 'Decrement' })).toBeVisible()
    })

    it('increment button emits increased value', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('button', { name: 'Increment' }).click()
      expect(onUpdate).toHaveBeenCalledWith(6)
    })

    it('decrement button emits decreased value', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('button', { name: 'Decrement' }).click()
      expect(onUpdate).toHaveBeenCalledWith(4)
    })

    it('respects step prop', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 0, type: 'number', step: 5, 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('button', { name: 'Increment' }).click()
      expect(onUpdate).toHaveBeenCalledWith(5)
    })

    it('disables increment button at max', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: 10, type: 'number', max: 10 },
      })

      expect(screen.getByRole('button', { name: 'Increment' })).toBeDisabled()
    })

    it('disables decrement button at min', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: 0, type: 'number', min: 0 },
      })

      expect(screen.getByRole('button', { name: 'Decrement' })).toBeDisabled()
    })

    it('clamps pasted value exceeding max', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', max: 10, 'onUpdate:modelValue': onUpdate },
      })

      const input = screen.getByRole('textbox')
      await input.fill('9999')
      expect(onUpdate).toHaveBeenLastCalledWith(10)
    })

    it('clamps pasted value below min', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', min: 0, 'onUpdate:modelValue': onUpdate },
      })

      const input = screen.getByRole('textbox')
      await input.fill('-999')
      expect(onUpdate).toHaveBeenLastCalledWith(0)
    })

    it('applies invalid class to wrapper when isInvalid is true', async () => {
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', isInvalid: true },
      })

      const wrapper = screen.getByRole('textbox').element().closest('.number-wrapper')
      expect(wrapper).toHaveClass('invalid')
    })

    it('increments value with ArrowUp key', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('textbox').click()
      await userEvent.keyboard('{ArrowUp}')
      expect(onUpdate).toHaveBeenCalledWith(6)
    })

    it('decrements value with ArrowDown key', async () => {
      const onUpdate = vi.fn()
      const screen = await render(UiInput, {
        props: { modelValue: 5, type: 'number', 'onUpdate:modelValue': onUpdate },
      })

      await screen.getByRole('textbox').click()
      await userEvent.keyboard('{ArrowDown}')
      expect(onUpdate).toHaveBeenCalledWith(4)
    })
  })
})
