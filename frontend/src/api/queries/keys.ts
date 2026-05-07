import type { GetRoleCodesFilter } from '@/api/services/accounts/types'
import type { TeamId, TournamentId, UserId } from '@/api/dbTypes'
import type { GetTournamentsArgs } from '@/api/services/tournaments/types'

export const teamKeys = {
  allTeams: () => ['teams'],
  team: (id: TeamId) => ['teams', id],
  'join-requests': (id: TeamId) => ['team-join-requests', id],
  'team-invitations': (id: TeamId) => ['team-invitations', id],
}

export const accountKeys = {
  profile: () => ['profile'],
  users: () => ['users'],
  user: (id: UserId) => ['user', id],
  roleCodes: (filter?: GetRoleCodesFilter) => ['role-codes', filter?.role ?? 'all'],
}

export const touranmentsKeys = {
  allTouranments: () => ['tournaments'],
  'tournaments-list': (args: GetTournamentsArgs) => [
    'tournaments',
    args.page,
    args.searchQuery,
    args.status,
    args.pageSize,
  ],
  touranment: (id: TournamentId) => ['tournaments', id],
  'active-team-tournament': (id: TeamId) => ['active-team-tournament', id],
  'eligible-teams': () => ['eligible-teams'],
  'registered-teams': (id: TournamentId) => ['registered-teams', id],
  rounds: (id: TournamentId) => ['rounds', id],
  'current-round': (id: TournamentId) => ['current-round', id],
  events: (id: TournamentId) => ['tournament-events', id],
}

export const notificationKeys = {
  all: ['notifications'],
  lists: () => [...notificationKeys.all, 'list'],
  list: (page: number, pageSize: number) => [...notificationKeys.lists(), { page, pageSize }],
  unreadCount: () => [...notificationKeys.all, 'unread-count'],
  settings: () => [...notificationKeys.all, 'settings'],
}
