import { describe, it, expect, vi } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiCardError from './UiCardError.vue'

describe('UiCardError', () => {
  it('shows the offline message when the network is unreachable', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: 'network' },
    })

    expect(screen.getByText('No connection')).toBeInTheDocument()
    expect(screen.getByText('Check your internet and try again.')).toBeInTheDocument()
  })

  it('shows the server message for 5xx codes', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: 500 },
    })

    expect(screen.getByText('Server unavailable')).toBeInTheDocument()
    expect(screen.getByText('Something broke on our side. Try again in a moment.')).toBeInTheDocument()
  })

  it('shows the forbidden message without a retry button', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: 403 },
    })

    expect(screen.getByText('No access')).toBeInTheDocument()
    expect(screen.getByText("You don't have permission to view this.")).toBeInTheDocument()
    expect(screen.getByRole('button').query()).not.toBeInTheDocument()
  })

  it('shows the not-found message without a retry button', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: 404 },
    })

    expect(screen.getByText('Not found')).toBeInTheDocument()
    expect(screen.getByRole('button').query()).not.toBeInTheDocument()
  })

  it('names the failed section when a title is provided', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: null, title: 'teams' },
    })

    expect(screen.getByText("Couldn't load teams")).toBeInTheDocument()
  })

  it('falls back to a generic message without a code or title', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: null },
    })

    expect(screen.getByText("Couldn't load data")).toBeInTheDocument()
    expect(screen.getByText('Try again.')).toBeInTheDocument()
  })

  it('emits retry when the retry button is clicked', async () => {
    const onRetry = vi.fn()
    const screen = await render(UiCardError, {
      props: { errorCode: 500, onRetry },
    })

    await screen.getByRole('button', { name: 'Try again' }).click()

    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('disables the retry button while a retry is in flight', async () => {
    const screen = await render(UiCardError, {
      props: { errorCode: 500, isFetching: true },
    })

    const button = screen.getByRole('button', { name: 'Retrying…' })
    expect(button).toBeDisabled()
  })
})
