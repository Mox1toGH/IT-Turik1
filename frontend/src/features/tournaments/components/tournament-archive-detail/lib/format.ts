const dateFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
})

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

const toValidDate = (value?: string | null) => {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export const formatArchiveDate = (value?: string | null) => {
  const date = toValidDate(value)
  return date ? dateFormatter.format(date) : 'N/A'
}

export const formatArchiveDateTime = (value?: string | null) => {
  const date = toValidDate(value)
  return date ? dateTimeFormatter.format(date) : 'N/A'
}

export const formatDateRange = (start?: string | null, end?: string | null) => {
  if (!start && !end) return 'Dates not specified'
  return `${formatArchiveDate(start)} - ${formatArchiveDate(end)}`
}

export const formatScore = (score?: number | string | null) => {
  if (score === null || score === undefined || score === '') return '-'
  const normalized = typeof score === 'number' ? score : Number(score)
  if (Number.isNaN(normalized)) return '-'
  return Number.isInteger(normalized) ? String(normalized) : normalized.toFixed(2)
}
