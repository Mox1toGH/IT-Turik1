import type { GetRoleCodesFilter } from '@/api/services/accounts/types'
import type { RoundId, TeamId, TournamentId, UserId } from '@/api/dbTypes'
import type { GetTournamentsArgs } from '@/api/services/tournaments/types'

export const teamKeys = {
  all: () => ['teams'] as const,
  lists: () => [...teamKeys.all(), 'list'] as const,
  details: () => [...teamKeys.all(), 'detail'] as const,
  detail: (id: TeamId) => [...teamKeys.details(), id] as const,
  info: (id: TeamId) => [...teamKeys.detail(id), 'info'] as const,
  joinRequests: (id: TeamId) => [...teamKeys.detail(id), 'join-requests'] as const,
  invitations: (id: TeamId) => [...teamKeys.detail(id), 'invitations'] as const,
}

export const accountKeys = {
  all: () => ['accounts'] as const,
  profile: () => [...accountKeys.all(), 'profile'] as const,
  users: () => [...accountKeys.all(), 'users'] as const,
  user: (id: UserId) => [...accountKeys.users(), id] as const,
  roleCodes: (filter?: GetRoleCodesFilter) =>
    [...accountKeys.all(), 'role-codes', filter?.role ?? 'all'] as const,
}

export const tournamentsKeys = {
  all: () => ['tournaments'] as const,
  lists: () => [...tournamentsKeys.all(), 'list'] as const,
  tournamentsLists: (args: GetTournamentsArgs) =>
    [
      ...tournamentsKeys.lists(),
      {
        page: args.page,
        pageSize: args.pageSize,
        searchQuery: args.searchQuery,
        status: args.status,
      },
    ] as const,
  details: () => [...tournamentsKeys.all(), 'detail'] as const,
  detail: (id: TournamentId) => [...tournamentsKeys.details(), id] as const,
  touranment: (id: TournamentId) => [...tournamentsKeys.detail(id), 'info'] as const,
  rounds: (id: TournamentId) => [...tournamentsKeys.detail(id), 'rounds'] as const,
  currentRound: (id: TournamentId) => [...tournamentsKeys.rounds(id), 'current'] as const,
  registeredTeams: (id: TournamentId) =>
    [...tournamentsKeys.detail(id), 'registered-teams'] as const,
  eligibleTeams: (id: TournamentId) => [...tournamentsKeys.detail(id), 'eligible-teams'] as const,
  events: (id: TournamentId) => [...tournamentsKeys.detail(id), 'events'] as const,
  submissions: (id: TournamentId) => [...tournamentsKeys.detail(id), 'submissions'] as const,
  roundSubmissions: (roundId: RoundId) => ['round-submissions', roundId] as const,
  activeTeamTournament: (teamId: TeamId) =>
    [...tournamentsKeys.all(), 'active-for-team', teamId] as const,
  archiveList: () => [...tournamentsKeys.all(), 'archive', 'list'] as const,
  archiveDetail: (id: TournamentId) => [...tournamentsKeys.all(), 'archive', 'detail', id] as const,
  archiveSubmissions: (id: TournamentId) =>
    [...tournamentsKeys.all(), 'archive', 'submissions', id] as const,
}

export const notificationKeys = {
  all: () => ['notifications'] as const,
  lists: () => [...notificationKeys.all(), 'list'] as const,
  list: (page: number, pageSize: number) =>
    [...notificationKeys.lists(), { page, pageSize }] as const,
  unreadCount: () => [...notificationKeys.all(), 'unread-count'] as const,
  settings: () => [...notificationKeys.all(), 'settings'] as const,
}

export const evaluationKeys = {
  all: () => ['evaluation'] as const,
  availableJury: (roundId: RoundId) => [...evaluationKeys.all(), 'availableJury', roundId] as const,
  assignments: (roundId?: RoundId) =>
    [...evaluationKeys.all(), 'assignments', roundId ?? 'all'] as const,
  assignment: (assignmentId: number) =>
    [...evaluationKeys.all(), 'assignment', assignmentId] as const,
  roundLeaderboard: (roundId: RoundId) =>
    [...evaluationKeys.all(), 'roundLeaderboard', roundId] as const,
  tournamentLeaderboard: (tournamentId: TournamentId) =>
    [...evaluationKeys.all(), 'tournamentLeaderboard', tournamentId] as const,
}
