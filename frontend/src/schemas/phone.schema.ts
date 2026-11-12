import * as v from 'valibot'

function isValidPhoneNumber(value: string): boolean {
  if (!/^\+?[\d\s().-]+$/.test(value)) return false

  const compact = value.replace(/[\s().-]/g, '')
  return /^(?:\+380|0)[3-9]\d{8}$/.test(compact)
}

export const PhoneSchema = v.pipe(
  v.string(),
  v.trim(),
  v.check(isValidPhoneNumber, 'Enter a valid Ukrainian phone number.'),
)
