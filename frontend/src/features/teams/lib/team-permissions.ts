import type { UserSummary } from '@/shared/types/user'
import type { Team } from '../types'

export function isTeamCaptain(user: Pick<UserSummary, 'id'> | null | undefined, team: Pick<Team, 'captain_id'> | null | undefined): boolean {
  return user?.id !== undefined && team?.captain_id === user.id
}
