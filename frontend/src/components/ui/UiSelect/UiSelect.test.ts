import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiSelect, { type SelectOption } from './UiSelect.vue'

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

      await screen.getByTestId('trigger-wrapper').click()

      const options = screen.getByRole('option').all()
      expect(options.length).toBe(4)
    })
  })

  describe('selection', () => {
    it('selects an option', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockOptions },
      })

      await screen.getByTestId('trigger-wrapper').click()
      await screen.getByRole('option').first().click()

      expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual(['apple'])
    })

    it('selects a numeric option', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: mockNumberOptions },
      })

      await screen.getByTestId('trigger-wrapper').click()
      await screen.getByRole('option').first().click()

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

      await screen.getByTestId('trigger-wrapper').click()

      const options = screen.getByRole('option').all()
      await options[1]!.click()
      await options[2]!.click()

      expect(screen.emitted('update:modelValue')).toStrictEqual([
        [['apple', 'banana']],
        [['apple', 'banana', 'cherry']],
      ])
    })
  })

  describe('empty state', () => {
    it('shows an empty state when no options are available', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, options: [] },
      })

      await screen.getByTestId('trigger-wrapper').click()

      await expect.poll(() => screen.getByRole('option').query()).not.toBeInTheDocument()
      expect(screen.getByTestId('select-empty')).toBeInTheDocument()
    })
  })

  describe('loading and error states', () => {
    it('disables the trigger and swaps the chevron for a loader while loading', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, isLoading: true, options: mockOptions },
      })

      const trigger = screen.getByTestId('trigger-wrapper')
      expect(trigger).toBeDisabled()

      expect(screen.getByTestId('loading-icon')).toBeInTheDocument()
      expect(screen.getByTestId('arrow-icon').query()).not.toBeInTheDocument()

      await screen.rerender({ isLoading: false })

      expect(screen.getByTestId('arrow-icon')).toBeInTheDocument()
      expect(screen.getByTestId('loading-icon').query()).not.toBeInTheDocument()
    })

    it('shows the error message', async () => {
      const screen = await render(UiSelect, {
        props: { modelValue: null, isError: true, error: 'Some error', options: mockOptions },
      })

      await screen.getByTestId('trigger-wrapper').click()

      const error = screen.getByRole('alert')
      expect(error).toBeInTheDocument()
      expect(error).toHaveTextContent('Some error')
    })
  })
})
