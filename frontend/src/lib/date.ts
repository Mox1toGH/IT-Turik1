interface FormatDateOptions {
  showHours?: boolean
}

export const formatDate = (value: Date | string, options?: FormatDateOptions) => {
  const date = value instanceof Date ? value : new Date(value)

  if (isNaN(date.getTime())) {
    return ''
  }

  if (options?.showHours) {
    return date.toLocaleDateString('uk-UA', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    })
  }

  return date.toLocaleDateString('uk-UA', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function combineDateAndTime(date: Date, time: string): Date {
  const parts = time.split(':')

  if (parts.length !== 2) {
    throw new Error('Invalid time format. Use HH:mm')
  }

  const hours = Number(parts[0])
  const minutes = Number(parts[1])

  if (Number.isNaN(hours) || Number.isNaN(minutes)) {
    throw new Error('Invalid time value')
  }

  const result = new Date(date)
  result.setHours(hours, minutes, 0, 0)

  return result
}
