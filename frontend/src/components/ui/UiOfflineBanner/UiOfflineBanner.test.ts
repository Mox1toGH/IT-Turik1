import { describe, it, expect, afterEach } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiOfflineBanner from './UiOfflineBanner.vue'

const onlineDescriptor = Object.getOwnPropertyDescriptor(window.navigator, 'onLine')

function setOnline(value: boolean) {
  Object.defineProperty(window.navigator, 'onLine', { value, configurable: true })
}

afterEach(() => {
  if (onlineDescriptor) Object.defineProperty(window.navigator, 'onLine', onlineDescriptor)
})

describe('UiOfflineBanner', () => {
  it('renders nothing while online', async () => {
    const screen = await render(UiOfflineBanner)

    expect(screen.getByText('No connection').query()).not.toBeInTheDocument()
  })

  it('shows the banner when going offline', async () => {
    const screen = await render(UiOfflineBanner)

    try {
      setOnline(false)
      window.dispatchEvent(new Event('offline'))

      await expect.poll(() => screen.getByText('No connection').query()).not.toBeNull()
      expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
    } finally {
      setOnline(true)
      window.dispatchEvent(new Event('online'))
    }
  })

  it('hides the banner when back online', async () => {
    const screen = await render(UiOfflineBanner)

    try {
      setOnline(false)
      window.dispatchEvent(new Event('offline'))
      await expect.poll(() => screen.getByText('No connection').query()).not.toBeNull()

      setOnline(true)
      window.dispatchEvent(new Event('online'))

      await expect.poll(() => screen.getByText('No connection').query()).not.toBeInTheDocument()
    } finally {
      setOnline(true)
      window.dispatchEvent(new Event('online'))
    }
  })
})
