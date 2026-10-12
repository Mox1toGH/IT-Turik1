import { describe, it, expect, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiFileDrop from './UiFileDrop.vue'

function pngFile(name = 'photo.png', size = 1024): File {
  return new File(['x'.repeat(size)], name, { type: 'image/png' })
}

function dropOn(viewport: HTMLElement, files: File[]) {
  const dataTransfer = new DataTransfer()
  for (const file of files) dataTransfer.items.add(file)
  viewport.dispatchEvent(new DragEvent('drop', { dataTransfer, bubbles: true }))
}

describe('UiFileDrop', () => {
  it('shows the default hint when no hint is provided', async () => {
    const screen = await render(UiFileDrop, {
      props: { modelValue: [] },
    })

    expect(screen.getByText('Any file type')).toBeInTheDocument()
  })

  it('shows the custom hint and accept summary', async () => {
    const screen = await render(UiFileDrop, {
      props: { modelValue: [], accept: 'image/*', maxSizeMb: 5, maxFiles: 3 },
    })

    expect(screen.getByText('image/* • up to 5MB • max 3 files')).toBeInTheDocument()
  })

  it('emits dropped files and lists them', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiFileDrop, {
      props: { modelValue: [], 'onUpdate:modelValue': onUpdate },
    })

    const zone = screen.getByText('Click to upload').element().closest('.dropzone') as HTMLElement
    dropOn(zone, [pngFile()])

    expect(onUpdate).toHaveBeenCalledTimes(1)
    const emitted = onUpdate.mock.calls[0]?.[0] as File[]
    expect(emitted.map((file) => file.name)).toStrictEqual(['photo.png'])
    await expect.poll(() => screen.getByText('photo.png').query()).not.toBeNull()
  })

  it('rejects a disallowed file type with an error', async () => {
    const onUpdate = vi.fn()
    const onError = vi.fn()
    const screen = await render(UiFileDrop, {
      props: { modelValue: [], accept: 'image/*', 'onUpdate:modelValue': onUpdate, onError },
    })

    const zone = screen.getByText('Click to upload').element().closest('.dropzone') as HTMLElement
    dropOn(zone, [new File(['x'], 'notes.txt', { type: 'text/plain' })])

    expect(onUpdate).not.toHaveBeenCalled()
    expect(onError).toHaveBeenCalledTimes(1)
    await expect.poll(() => screen.getByText(/isn't an accepted file type/).query()).not.toBeNull()
  })

  it('rejects files over the size limit', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiFileDrop, {
      props: { modelValue: [], maxSizeMb: 1, 'onUpdate:modelValue': onUpdate },
    })

    const zone = screen.getByText('Click to upload').element().closest('.dropzone') as HTMLElement
    dropOn(zone, [pngFile('big.png', 2 * 1024 * 1024)])

    expect(onUpdate).not.toHaveBeenCalled()
    await expect.poll(() => screen.getByText(/is over the 1MB limit/).query()).not.toBeNull()
  })

  it('removes a file when its remove button is clicked', async () => {
    const file = pngFile()
    const onUpdate = vi.fn()
    const screen = await render(UiFileDrop, {
      props: { modelValue: [file], 'onUpdate:modelValue': onUpdate },
    })

    expect(screen.getByText('photo.png')).toBeInTheDocument()

    await screen.getByRole('button', { name: 'Remove file' }).click()

    expect(onUpdate).toHaveBeenLastCalledWith([])
    await expect.poll(() => screen.getByText('photo.png').query()).not.toBeInTheDocument()
  })

  it('ignores drops when disabled', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiFileDrop, {
      props: { modelValue: [], disabled: true, 'onUpdate:modelValue': onUpdate },
    })

    const zone = screen.getByText('Click to upload').element().closest('.dropzone') as HTMLElement
    dropOn(zone, [pngFile()])

    expect(onUpdate).not.toHaveBeenCalled()
  })
})
