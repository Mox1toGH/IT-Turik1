import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiPagination from './UiPagination.vue'

describe('UiPagination', () => {
  it('shows the item range summary', async () => {
    const screen = await render(UiPagination, {
      props: { modelValue: 1, totalItems: 95, pageSize: 10 },
    })

    expect(screen.getByText('Showing 1-10 of 95')).toBeInTheDocument()
  })

  it('shows the last partial range on the final page', async () => {
    const screen = await render(UiPagination, {
      props: { modelValue: 10, totalItems: 95, pageSize: 10 },
    })

    expect(screen.getByText('Showing 91-95 of 95')).toBeInTheDocument()
  })

  it('hides the summary when showSummary is false', async () => {
    const screen = await render(UiPagination, {
      props: { modelValue: 1, totalItems: 95, pageSize: 10, showSummary: false },
    })

    expect(screen.getByText(/Showing/).query()).not.toBeInTheDocument()
  })

  it('emits the clicked page', async () => {
    const screen = await render(UiPagination, {
      props: { modelValue: 1, totalItems: 95, pageSize: 10 },
    })

    await screen.getByRole('button', { name: '2' }).click()

    expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([2])
  })

  it('disables Prev on the first page and Next on the last page', async () => {
    const first = await render(UiPagination, {
      props: { modelValue: 1, totalItems: 95, pageSize: 10 },
    })
    expect(first.getByRole('button', { name: 'Prev' })).toBeDisabled()
    expect(first.getByRole('button', { name: 'Next' })).not.toBeDisabled()
    first.unmount()

    const last = await render(UiPagination, {
      props: { modelValue: 10, totalItems: 95, pageSize: 10 },
    })
    expect(last.getByRole('button', { name: 'Next' })).toBeDisabled()
    expect(last.getByRole('button', { name: 'Prev' })).not.toBeDisabled()
  })

  it('clamps an out-of-range page to the last page', async () => {
    const screen = await render(UiPagination, {
      props: { modelValue: 99, totalItems: 95, pageSize: 10 },
    })

    expect(screen.getByText('Showing 91-95 of 95')).toBeInTheDocument()
  })
})
