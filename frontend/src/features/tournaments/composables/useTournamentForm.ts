import type { Ref } from 'vue'
import type { FormErrors } from '@/composables/useForm'
import { combineDateAndTime } from '@/lib/date'

export interface TournamentFormFields {
  name: string
  description: string
  startDate: Date
  startTime: string
  endDate: Date
  endTime: string
  max_teams: number
  min_team_members: number
}

export interface TournamentFormController {
  fields: Ref<TournamentFormFields>
  errors: Ref<FormErrors>
  validateField: (field: string) => void
}

export interface TournamentFormPayload {
  name: string
  description: string
  max_teams: number
  min_team_members: number
  start_date: string
  end_date: string
}

export function createTournamentFormDefaults(): TournamentFormFields {
  return {
    name: '',
    description: '',
    startDate: new Date(),
    startTime: '00:00',
    endDate: new Date(),
    endTime: '00:00',
    max_teams: 2,
    min_team_members: 2,
  }
}

export function toTournamentPayload(values: TournamentFormFields): TournamentFormPayload {
  return {
    name: values.name,
    description: values.description,
    max_teams: values.max_teams,
    min_team_members: values.min_team_members,
    start_date: combineDateAndTime(values.startDate, values.startTime).toISOString(),
    end_date: combineDateAndTime(values.endDate, values.endTime).toISOString(),
  }
}

export function toTime(value: Date | string): string {
  const date = new Date(value)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}
