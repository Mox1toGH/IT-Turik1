import { describe, it, expect } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiSelect, { type SelectOption } from '../UiSelect.vue'

const mockOptions: SelectOption[] = [
  { value: 'apple', label: 'Apple' },
  { value: 'banana', label: 'Banana' },
  { value: 'cherry', label: 'Cherry' },
  { value: 'date', label: 'Date' },
]

const mockNumberOptions: SelectOption[] = [
  { value: 1, label: 'Apple' },
  { value: 2, label: 'Banana' },
  { value: 3, label: 'Cherry' },
  { value: 4, label: 'Date' },
]

describe('UiSelect', () => {
  describe('display', () => {
    it('shows placeholder when no option is selected', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions, placeholder: 'Choose fruit' },
      })

      expect(screen.getByText('Choose fruit')).toBeInTheDocument()
    })

    it('shows custom trigger button', async () => {
      const screen = await render(UiSelect, {
        props: { multiple: true, modelValue: [], options: mockOptions },
        slots: {
          trigger: '<button>Custom</button>',
        },
      })

      const button = screen.getByRole('button', { hasText: 'Custom' })
      expect(button).toBeInTheDocument()
    })

    it('shows selected label when a value is provided', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: 'apple', options: mockOptions },
      })

      expect(screen.getByText('Apple')).toBeInTheDocument()
    })

    it('shows multiple selection summary when more than one item is selected', async () => {
      const screen = await render(UiSelect, {
        props: { multiple: true, modelValue: ['apple', 'banana', 'cherry'], options: mockOptions },
      })

      expect(screen.getByText('Apple +2 more')).toBeInTheDocument()
    })
  })

  describe('open / close', () => {
    it('opens the dropdown and reveals option items', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const options = screen.getByRole('option').all()
      expect(options.length).toBe(4)
      expect(screen.getByTestId('select-search')).toBeInTheDocument()
    })

    it('opens dropdown when custom trigger is clicked', async () => {
      const screen = await render(UiSelect, {
        props: { multiple: true, modelValue: [], options: mockOptions },
        slots: {
          trigger: '<button>Custom</button>',
        },
      })

      await userEvent.click(screen.getByRole('button', { hasText: 'Custom' }))

      expect(screen.getByRole('listbox')).toBeInTheDocument()
    })

    it('opens the dropdown with keyboard Enter', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      await userEvent.keyboard('{Tab}{Enter}')

      expect(screen.getByTestId('select-dropdown')).toBeInTheDocument()
    })

    it('closes the dropdown with Escape', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      await userEvent.keyboard('{Escape}')

      await expect.poll(() => screen.getByTestId('select-dropdown').query()).not.toBeInTheDocument()
    })
  })

  describe('selection', () => {
    it('selects an option', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const options = screen.getByRole('option').first()
      await options.click()

      expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual(['apple'])
    })

    it('selects a numeric option', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockNumberOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const options = screen.getByRole('option').first()
      await options.click()

      expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([1])
    })

    it('allows multiple selections', async () => {
      const screen = await render(UiSelect, {
        props: {
          multiple: true,
          modelValue: ['apple'],
          options: mockOptions,
        },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const options = screen.getByRole('option').all()
      await options[1].click()
      await options[2].click()

      expect(screen.emitted('update:modelValue')).toStrictEqual([
        [['apple', 'banana']],
        [['apple', 'cherry']],
      ])
    })
  })

  describe('search / filtering', () => {
    it('filters the option list based on query', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const input = screen.getByRole('textbox')
      await input.fill('ban')

      const options = screen.getByRole('option').all()
      expect(options.length).toBe(1)
      expect(options[0]).toHaveTextContent('Banana')
    })

    it('shows an empty state when no options are available', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: [] },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const options = screen.getByRole('option')
      expect(options.length).toBe(0)
      expect(screen.getByTestId('select-empty')).toBeInTheDocument()
    })
  })

  describe('loading and error states', () => {
    it('handles loading correctly', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, isLoading: true, options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      expect(trigger).toBeDisabled()

      const loading = screen.getByTestId('loading-icon')
      const arrow = screen.getByTestId('arrow-icon')

      expect(loading).toBeInTheDocument()
      expect(arrow).not.toBeInTheDocument()

      await screen.rerender({ isLoading: false })

      expect(arrow).toBeInTheDocument()
      expect(loading).not.toBeInTheDocument()
    })

    it('handles error correctly', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, isError: true, error: 'Some error', options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      const error = screen.getByRole('alert')
      expect(error).toBeInTheDocument()

      await expect.poll(() => screen.getByRole('option').query()).not.toBeInTheDocument()
    })
  })

  describe('accessibility', () => {
    it('applies accessible aria attributes to the trigger and listbox', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      const trigger = screen.getByTestId('trigger-wrapper')
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox')
      expect(trigger).toHaveAttribute('aria-expanded', 'false')

      await trigger.click()

      expect(trigger).toHaveAttribute('aria-expanded', 'true')
      expect(screen.getByRole('listbox')).toHaveAttribute('role', 'listbox')
      expect(screen.getByRole('listbox')).toHaveAttribute('aria-multiselectable', 'false')
    })

    it('sets aria-multiselectable when multiple mode is enabled', async () => {
      const screen = await render(UiSelect, {
        props: { multiple: true, modelValue: [], options: mockOptions },
      })

      const trigger = screen.getByRole('button')
      await trigger.click()

      expect(screen.getByRole('listbox')).toHaveAttribute('aria-multiselectable', 'true')
    })
  })
})
