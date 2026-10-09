import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useNotification } from '../useNotification'

const DEFAULT_MS = 4200

describe('useNotification', () => {
  const { notification, showNotification, hideNotification, clearNotificationQueue } =
    useNotification()

  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    hideNotification(true)
    vi.useRealTimers()
  })

  describe('show', () => {
    it('shows a success notification by default', () => {
      showNotification('Saved')

      expect(notification.value).toMatchObject({
        message: 'Saved',
        type: 'success',
        duration: DEFAULT_MS,
      })
    })

    it('supports error type', () => {
      showNotification('Failed', 'error')

      expect(notification.value?.type).toBe('error')
    })

    it('trims the message', () => {
      showNotification('  Saved  ')

      expect(notification.value?.message).toBe('Saved')
    })

    it.each([undefined, '', '   '])('ignores empty message: %j', (msg) => {
      showNotification(msg as string | undefined)

      expect(notification.value).toBeNull()
    })
  })

  describe('auto dismiss', () => {
    it('hides after the default duration', () => {
      showNotification('Saved')

      vi.advanceTimersByTime(DEFAULT_MS - 1)
      expect(notification.value).not.toBeNull()

      vi.advanceTimersByTime(1)
      expect(notification.value).toBeNull()
    })

    it('respects a custom duration', () => {
      showNotification('Saved', 'success', { duration: 1000 })

      vi.advanceTimersByTime(999)
      expect(notification.value).not.toBeNull()

      vi.advanceTimersByTime(1)
      expect(notification.value).toBeNull()
    })

    it('hideNotification closes immediately and cancels the timer', () => {
      showNotification('Saved')

      hideNotification()
      expect(notification.value).toBeNull()

      showNotification('Next')
      vi.advanceTimersByTime(DEFAULT_MS - 1)
      // старий таймер не повинен закрити нове повідомлення раніше часу
      expect(notification.value?.message).toBe('Next')
    })
  })

  describe('replace mode (default)', () => {
    it('replaces the current notification and gives it a new id', () => {
      showNotification('A')
      const firstId = notification.value!.id

      showNotification('B')

      expect(notification.value?.message).toBe('B')
      expect(notification.value!.id).not.toBe(firstId)
    })

    it('resets the timer when replaced', () => {
      showNotification('A')
      vi.advanceTimersByTime(3000)

      showNotification('B')
      vi.advanceTimersByTime(3000)
      expect(notification.value?.message).toBe('B') // старий таймер скасовано

      vi.advanceTimersByTime(DEFAULT_MS - 3000)
      expect(notification.value).toBeNull()
    })

    it('same message+type only extends the timer, id is kept', () => {
      showNotification('A')
      const id = notification.value!.id
      vi.advanceTimersByTime(3000)

      showNotification('A')
      expect(notification.value!.id).toBe(id)

      vi.advanceTimersByTime(3000)
      expect(notification.value).not.toBeNull()

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value).toBeNull()
    })

    it('same message with another type is NOT a duplicate', () => {
      showNotification('A', 'success')
      const id = notification.value!.id

      showNotification('A', 'error')

      expect(notification.value!.id).not.toBe(id)
      expect(notification.value?.type).toBe('error')
    })
  })

  describe('queue mode', () => {
    it('shows immediately when nothing is displayed', () => {
      showNotification('A', 'success', { mode: 'queue' })

      expect(notification.value?.message).toBe('A')
    })

    it('does not replace the current one, shows next after it expires', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })

      expect(notification.value?.message).toBe('A')

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value?.message).toBe('B')

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value).toBeNull()
    })

    it('keeps FIFO order', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })
      showNotification('C', 'success', { mode: 'queue' })

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value?.message).toBe('B')

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value?.message).toBe('C')
    })

    it('does not queue a duplicate of the current notification', () => {
      showNotification('A')
      showNotification('A', 'success', { mode: 'queue' })

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value).toBeNull()
    })

    it('does not queue a duplicate of the last queued notification', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })
      showNotification('B', 'success', { mode: 'queue' })

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value?.message).toBe('B')

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value).toBeNull()
    })

    it('hideNotification() skips to the next queued item', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })

      hideNotification()

      expect(notification.value?.message).toBe('B')
    })

    it('hideNotification(true) clears current and queue', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })

      hideNotification(true)
      expect(notification.value).toBeNull()

      vi.advanceTimersByTime(DEFAULT_MS * 2)
      expect(notification.value).toBeNull()
    })

    it('clearNotificationQueue drops queued items but keeps the current one', () => {
      showNotification('A')
      showNotification('B', 'success', { mode: 'queue' })

      clearNotificationQueue()
      expect(notification.value?.message).toBe('A')

      vi.advanceTimersByTime(DEFAULT_MS)
      expect(notification.value).toBeNull()
    })
  })
})
