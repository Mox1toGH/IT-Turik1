import * as v from 'valibot'

function normalizeLink(value: string): string {
  return /^[a-z][a-z\d+.-]*:/i.test(value) ? value : `https://${value}`
}

function getProtocol(value: string): string {
  return value.match(/^([a-z][a-z\d+.-]*):/i)?.[1]?.toLowerCase() ?? ''
}

function hasSupportedProtocol(value: string): boolean {
  return ['http', 'https', 'mailto', 'tel'].includes(getProtocol(value))
}

function isWellFormedUrl(value: string): boolean {
  if (value === 'https://') return true

  try {
    new URL(value)
    return true
  } catch {
    return false
  }
}

function hasValidWebAddress(value: string): boolean {
  if (!['http', 'https'].includes(getProtocol(value))) return true
  try {
    return !!new URL(value).hostname
  } catch {
    return true
  }
}

function hasValidEmailAddress(value: string): boolean {
  if (getProtocol(value) !== 'mailto') return true
  try {
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(new URL(value).pathname)
  } catch {
    return true
  }
}

function hasValidPhoneNumber(value: string): boolean {
  if (getProtocol(value) !== 'tel') return true
  try {
    return /^\+?[\d().-]+$/.test(new URL(value).pathname)
  } catch {
    return true
  }
}

export const LinkUrlSchema = v.pipe(
  v.string(),
  v.trim(),
  v.nonEmpty('Enter a link URL.'),
  v.transform(normalizeLink),
  v.check(
    hasSupportedProtocol,
    'This link type is not supported. Use http, https, mailto, or tel.',
  ),
  v.check(isWellFormedUrl, 'The URL format is invalid. Check the address and try again.'),
  v.check(hasValidWebAddress, 'Web links must include a valid domain, such as example.com.'),
  v.check(
    hasValidEmailAddress,
    'Email links must use the format mailto:name@example.com with a valid email address.',
  ),
  v.check(
    hasValidPhoneNumber,
    'Phone links must use tel: followed by a valid number, such as tel:+15551234567.',
  ),
)
