import { describe, expect, it } from 'vitest'
import * as v from 'valibot'
import { PhoneSchema } from './phone.schema'

describe('PhoneSchema', () => {
  it.each(['+380501234567', '+380 (67) 123-45-67', '050 123 45 67'])(
    'accepts valid phone number %s',
    (phone) => {
      expect(v.safeParse(PhoneSchema, phone).success).toBe(true)
    },
  )

  it.each([
    '',
    '12345',
    'phone number',
    '+0001234567',
    '+12345678901',
    '020 7946 0958',
    '+3805012345678',
  ])('rejects invalid phone number %s', (phone) => {
    expect(v.safeParse(PhoneSchema, phone).success).toBe(false)
  })
})
