import { describe, expect, it } from 'vitest'
import { hasAnyRole, hasRole } from './permissions'

describe('permission checks', () => {
  it('matches a user role', () => {
    expect(hasRole({ role: 'admin' }, 'admin')).toBe(true)
    expect(hasRole({ role: 'team' }, 'admin')).toBe(false)
  })

  it('denies access when no user is available', () => {
    expect(hasRole(undefined, 'admin')).toBe(false)
    expect(hasAnyRole(null, ['admin', 'organizer'])).toBe(false)
  })

  it('accepts any matching role from the allowed roles', () => {
    expect(hasAnyRole({ role: 'organizer' }, ['admin', 'organizer'])).toBe(true)
    expect(hasAnyRole({ role: 'jury' }, ['admin', 'organizer'])).toBe(false)
  })

  it('denies access when the allowed role list is empty', () => {
    expect(hasAnyRole({ role: 'admin' }, [])).toBe(false)
  })
})
