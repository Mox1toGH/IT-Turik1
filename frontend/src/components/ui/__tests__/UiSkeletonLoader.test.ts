import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiSkeletonLoader from '../UiSkeletonLoader.vue'

describe('UiSkeletonLoader', () => {
  it('renders skeleton slot content when loading is true', async () => {
    const screen = await render(UiSkeletonLoader, {
      props: { loading: true },
      slots: { skeleton: 'Loading...', default: 'Content Loaded' },
    })

    expect(screen.getByText('Loading...')).toBeInTheDocument()
    await expect.poll(() => screen.getByText('Content Loaded').query()).not.toBeInTheDocument()
  })

  it('renders content slot content when loading is false', async () => {
    const screen = await render(UiSkeletonLoader, {
      props: { loading: false },
      slots: { skeleton: 'Loading...', default: 'Content loaded' },
    })

    expect(screen.getByText('Content loaded')).toBeInTheDocument()
    await expect.poll(() => screen.getByText('Loading...').query()).not.toBeInTheDocument()
  })

  it('switches displayed content when loading changes', async () => {
    const screen = await render(UiSkeletonLoader, {
      props: { loading: true },
      slots: { skeleton: 'Loading...', default: 'Content' },
    })

    expect(screen.getByText('Loading...')).toBeInTheDocument()
    await expect.poll(() => screen.getByText('Content').query()).not.toBeInTheDocument()

    await screen.rerender({ loading: true })

    expect(screen.getByText('Loading...')).toBeInTheDocument()
    await expect.poll(() => screen.getByText('Content').query()).not.toBeInTheDocument()
  })
})
