import type { StatusD67Enum, StatusE43Enum } from '@/api/.ts.schemas'
import type { Variants } from '@/components/ui/UiBadge.vue'

export function truncateText(text: string, maxLength: number) {
  if (typeof text !== 'string') return
  if (text.length > maxLength) return text.slice(0, maxLength) + '...'
  return text
}

export const tournamentStatusBadge = (status?: StatusD67Enum): Variants => {
  if (status === 'draft') return 'gray'
  if (status === 'finished') return 'red'
  if (status === 'running') return 'green'
  if (status === 'registration') return 'orange'

  return 'gray'
}

export const roundStatusBadge = (status?: StatusE43Enum): Variants => {
  if (status === 'active') return 'primary'
  if (status === 'evaluated') return 'red'
  if (status === 'submission_closed') return 'orange'
  return 'gray'
}
