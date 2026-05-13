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

export const certificateKeys = {
  myCertificates: (page = 1, pageSize = 6) => ['my-certificates', page, pageSize],
  allCertificates: (page = 1, pageSize = 20) => ['certificates', page, pageSize],
  templates: () => ['certificate-templates'],
  verify: (code: string) => ['certificate-verify', code],
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
  calendar: () => [...tournamentsKeys.all(), 'calendar'] as const,
}

export const notificationKeys = {
  all: () => ['notifications'] as const,
  lists: () => [...notificationKeys.all(), 'list'] as const,
  list: (page: number, pageSize: number) =>
    [...notificationKeys.lists(), { page, pageSize }] as const,
  unreadCount: () => [...notificationKeys.all(), 'unread-count'] as const,
  settings: () => [...notificationKeys.all(), 'settings'] as const,
}

export const newsKeys = {
  all: () => ['news'] as const,
  lists: () => [...newsKeys.all(), 'list'] as const,
  list: (page: number, pageSize: number) => [...newsKeys.lists(), { page, pageSize }] as const,
  detail: (id: number) => [...newsKeys.all(), 'detail', id] as const,
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

export const pointsKeys = {
  all: () => ['points'] as const,
  myBalance: () => [...pointsKeys.all(), 'my-balance'] as const,
  myTransactionsPrefix: () => [...pointsKeys.all(), 'my-transactions'] as const,
  myTransactions: (args: { page: number; pageSize: number; ordering: string }) =>
    [...pointsKeys.myTransactionsPrefix(), args] as const,
  userBalance: (userId: UserId) => [...pointsKeys.all(), 'user-balance', userId] as const,
  userTransactionsPrefix: (userId: UserId) =>
    [...pointsKeys.all(), 'user-transactions', userId] as const,
  userTransactions: (
    userId: UserId,
    args: { page: number; pageSize: number; ordering: string },
  ) => [...pointsKeys.userTransactionsPrefix(userId), args] as const,
}

export const inventoryKeys = {
  all: () => ['inventory'] as const,
  myPrefix: () => [...inventoryKeys.all(), 'my'] as const,
  my: () => [...inventoryKeys.myPrefix(), 'list'] as const,
}

export const shopKeys = {
  all: () => ['shop'] as const,
  productsPrefix: () => [...shopKeys.all(), 'products'] as const,
  products: (args: {
    page: number
    pageSize: number
    search: string
    category: number | null
    productType: string
    ordering: string
  }) => [...shopKeys.productsPrefix(), args] as const,
  myOrdersPrefix: () => [...shopKeys.all(), 'my-orders'] as const,
  myOrders: (args: { page: number; pageSize: number }) =>
    [...shopKeys.myOrdersPrefix(), args] as const,
  adminCategoriesPrefix: () => [...shopKeys.all(), 'admin-categories'] as const,
  adminCategories: (args: { page: number; pageSize: number }) =>
    [...shopKeys.adminCategoriesPrefix(), args] as const,
  adminProductsPrefix: () => [...shopKeys.all(), 'admin-products'] as const,
  adminProducts: (args: {
    page: number
    pageSize: number
    search: string
    category: number | null
    productType: string
  }) => [...shopKeys.adminProductsPrefix(), args] as const,
  adminOrdersPrefix: () => [...shopKeys.all(), 'admin-orders'] as const,
  adminOrders: (args: { page: number; pageSize: number; status: string; user: string }) =>
    [...shopKeys.adminOrdersPrefix(), args] as const,
  avatarFramesPrefix: () => [...shopKeys.all(), 'avatar-frames'] as const,
  avatarFrames: (args: { page: number; pageSize: number; search: string }) =>
    [...shopKeys.avatarFramesPrefix(), args] as const,
  adminAvatarFramesPrefix: () => [...shopKeys.all(), 'admin-avatar-frames'] as const,
  adminAvatarFrames: (args: { page: number; pageSize: number; search: string }) =>
    [...shopKeys.adminAvatarFramesPrefix(), args] as const,
}
