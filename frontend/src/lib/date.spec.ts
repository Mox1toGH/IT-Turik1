import { describe, it, expect } from 'vitest'
import { formatDate, combineDateAndTime } from './date'

describe('formatDate', () => {
  const date = new Date(2024, 0, 15) // Jan 15, 2024

  it('formats date without hours by default', () => {
    const result = formatDate(date)
    expect(result).toMatchInlineSnapshot(`"15 січ. 2024 р."`)
  })

  it('formats date with hours when showHours is true', () => {
    const dateWithTime = new Date(2024, 0, 15, 14, 30)
    const result = formatDate(dateWithTime, { showHours: true })
    expect(result).toMatchInlineSnapshot(`"15 січ. 2024 р., 14:30"`)
  })

  it('formats date without hours when showHours is false', () => {
    const result = formatDate(date, { showHours: false })
    expect(result).toMatchInlineSnapshot(`"15 січ. 2024 р."`)
  })
})

describe('combineDateAndTime', () => {
  const baseDate = new Date(2024, 0, 15)

  it('combines date and time correctly', () => {
    const result = combineDateAndTime(baseDate, '14:30')
    expect(result.getHours()).toBe(14)
    expect(result.getMinutes()).toBe(30)
    expect(result.getSeconds()).toBe(0)
    expect(result.getMilliseconds()).toBe(0)
  })

  it('does not mutate the original date', () => {
    const original = new Date(2024, 0, 15, 10, 0)
    combineDateAndTime(original, '14:30')
    expect(original.getHours()).toBe(10)
  })

  it('preserves the original date parts', () => {
    const result = combineDateAndTime(baseDate, '09:05')
    expect(result.getFullYear()).toBe(2024)
    expect(result.getMonth()).toBe(0)
    expect(result.getDate()).toBe(15)
  })

  it('handles midnight', () => {
    const result = combineDateAndTime(baseDate, '00:00')
    expect(result.getHours()).toBe(0)
    expect(result.getMinutes()).toBe(0)
  })

  it('handles end of day', () => {
    const result = combineDateAndTime(baseDate, '23:59')
    expect(result.getHours()).toBe(23)
    expect(result.getMinutes()).toBe(59)
  })

  it('throws on invalid format', () => {
    expect(() => combineDateAndTime(baseDate, '1430')).toThrow('Invalid time format. Use HH:mm')
    expect(() => combineDateAndTime(baseDate, '14:30:00')).toThrow('Invalid time format. Use HH:mm')
  })

  it('throws on non-numeric values', () => {
    expect(() => combineDateAndTime(baseDate, 'ab:cd')).toThrow('Invalid time value')
  })
})
