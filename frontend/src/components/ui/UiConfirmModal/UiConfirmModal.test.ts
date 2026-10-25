import { describe, it, expect, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiConfirmModal from './UiConfirmModal.vue'

describe('UiConfirmModal', () => {
  it('renders title, message and action buttons when open', async () => {
    const screen = await render(UiConfirmModal, {
      props: {
        modelValue: true,
        title: 'Delete news',
        message: 'Are you sure you want to delete this news?',
        confirmText: 'Delete',
      },
    })

    expect(screen.getByText('Delete news')).toBeInTheDocument()
    expect(screen.getByText('Are you sure you want to delete this news?')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
  })

  it('emits confirm without closing when the confirm button is clicked', async () => {
    const onConfirm = vi.fn()
    const screen = await render(UiConfirmModal, {
      props: { modelValue: true, onConfirm },
    })

    await screen.getByRole('button', { name: 'Confirm' }).click()

    expect(onConfirm).toHaveBeenCalledTimes(1)
    expect(screen.emitted('update:modelValue')).toBeFalsy()
  })

  it('emits cancel and closes when the cancel button is clicked', async () => {
    const onCancel = vi.fn()
    const screen = await render(UiConfirmModal, {
      props: { modelValue: true, onCancel },
    })

    await screen.getByRole('button', { name: 'Cancel' }).click()

    expect(screen.emitted('update:modelValue')?.[0]).toStrictEqual([false])
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it('disables the confirm button while loading', async () => {
    const screen = await render(UiConfirmModal, {
      props: { modelValue: true, loading: true, confirmText: 'Delete' },
    })

    expect(screen.getByRole('button', { name: 'Delete' })).toBeDisabled()
  })

  it('stays closed when modelValue is false', async () => {
    const screen = await render(UiConfirmModal, {
      props: { modelValue: false, title: 'Delete news' },
    })

    expect(screen.getByText('Delete news').query()).not.toBeInTheDocument()
  })
})
