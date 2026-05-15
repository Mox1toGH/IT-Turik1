import { MutationCache, QueryClient } from '@tanstack/vue-query'

import {
  getListTeamsQueryKey,
  getGetTeamQueryKey,
  getListTeamInvitationsQueryKey,
  getListTeamInvitationsByTeamQueryKey,
  getListTeamJoinRequestsByTeamQueryKey,
} from '@/api/teams/teams'

import {
  getListJuryAssignmentsQueryKey,
  getGetJuryEvaluationQueryKey,
  getListAvailableJuryQueryKey,
  getGetRoundPassingStatusQueryKey,
  getGetTournamentLeaderboardQueryKey,
  getGetRoundLeaderboardQueryKey,
} from '@/api/evaluation/evaluation'

import {
  getListTournamentsQueryKey,
  getGetTournamentQueryKey,
  getGetTournamentForUpdateQueryKey,
  getListTournamentTeamsQueryKey,
  getListRoundsQueryKey,
  getGetRoundQueryKey,
  getListRoundSubmissionsQueryKey,
  getListTournamentSubmissionsQueryKey,
  getListSubmissionsQueryKey,
  getGetSubmissionQueryKey,
  getListEventsQueryKey,
  getGetEventQueryKey,
  getGetTeamActiveTournamentQueryKey,
  getGetCurrentTaskQueryKey,
  getGetTournamentTeamRegistrationQueryKey,
  getListEligibleTeamsForTournamentQueryKey,
  getListMyTeamSubmissionsQueryKey,
  getGetMyCalendarQueryKey,
} from '@/api/tournaments/tournaments'

import {
  getGetMyPointsBalanceQueryKey,
  getListMyPointsTransactionsQueryKey,
  getGetAdminUserPointsBalanceQueryKey,
  getListAdminUserPointsTransactionsQueryKey,
} from '@/api/points/points'

import {
  getListProductsQueryKey,
  getGetProductQueryKey,
  getListMyOrdersQueryKey,
  getListAdminCategoriesQueryKey,
  getGetAdminCategoryQueryKey,
  getListAdminProductsQueryKey,
  getGetAdminProductQueryKey,
  getListAdminOrdersQueryKey,
  getListAvatarFramesQueryKey,
  getListAdminAvatarFramesQueryKey,
  getGetAdminAvatarFrameQueryKey,
} from '@/api/shop/shop'

import {
  getListCertificatesQueryKey,
  getGetCertificateQueryKey,
  getListCertificateTemplatesQueryKey,
  getGetCertificateTemplateQueryKey,
} from '@/api/certificates/certificates'

import {
  getListNotificationsQueryKey,
  getGetUnreadNotificationCountQueryKey,
  getGetNotificationSettingsQueryKey,
} from '@/api/notifications/notifications'

import { getListMyDigitalInventoryQueryKey } from '@/api/inventory/inventory'

import { getListNewsQueryKey, getGetNewsQueryKey } from '@/api/news/news'

import {
  getGetUserProfileQueryKey,
  getListRoleActivationCodesQueryKey,
} from '@/api/accounts/accounts'

import {
  getGetPlayerStatsQueryKey,
  getGetTournamentStatsQueryKey,
  getGetAdminStatsQueryKey,
} from '@/api/stats/stats'

type Ctx = {
  vars: Record<string, unknown>
  data: Record<string, unknown>
}

type InvalidationEntry = (ctx: Ctx) => readonly unknown[]

const v = (fn: InvalidationEntry): InvalidationEntry => fn

const MUTATION_INVALIDATION_MAP: Record<string, InvalidationEntry[]> = {
  // Teams
  createTeam: [v(() => getListTeamsQueryKey())],
  replaceTeam: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
  ],
  updateTeam: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
  ],
  updateTeamBanner: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
  ],
  deleteTeamBanner: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
  ],
  deleteTeam: [v(() => getListTeamsQueryKey())],
  leaveTeam: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
  ],
  removeMemberFromTeam: [v(({ vars }) => getGetTeamQueryKey(vars.id as number))],
  inviteMemberToTeam: [
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
    v(({ vars }) => getListTeamInvitationsByTeamQueryKey(vars.id as number)),
  ],
  acceptTeamJoinRequest: [
    v(({ vars }) => getGetTeamQueryKey(vars.id as number)),
    v(({ vars }) => getListTeamJoinRequestsByTeamQueryKey(vars.id as number)),
  ],
  declineTeamJoinRequest: [
    v(({ vars }) => getListTeamJoinRequestsByTeamQueryKey(vars.id as number)),
  ],
  createTeamJoinRequest: [v(() => getListTeamsQueryKey())],
  acceptTeamInvitation: [
    v(() => getListTeamsQueryKey()),
    v(() => getListTeamInvitationsQueryKey()),
  ],
  declineTeamInvitation: [v(() => getListTeamInvitationsQueryKey())],

  // Evaluation
  createJuryEvaluation: [
    v(() => getListJuryAssignmentsQueryKey()),
    v(() => getGetJuryEvaluationQueryKey()),
  ],
  replaceJuryEvaluation: [
    v(({ vars }) => getGetJuryEvaluationQueryKey(vars.id as number)),
    v(() => getListJuryAssignmentsQueryKey()),
  ],
  updateJuryEvaluation: [
    v(({ vars }) => getGetJuryEvaluationQueryKey(vars.id as number)),
    v(() => getListJuryAssignmentsQueryKey()),
  ],
  deleteJuryEvaluation: [
    v(({ vars }) => getGetJuryEvaluationQueryKey(vars.id as number)),
    v(() => getListJuryAssignmentsQueryKey()),
  ],
  assignJuryToRound: [
    v(() => getListJuryAssignmentsQueryKey()),
    v(({ vars }) => getListAvailableJuryQueryKey(vars.id as number)),
    v(({ vars }) => getGetRoundPassingStatusQueryKey(vars.id as number)),
  ],

  // Tournaments
  createTournament: [v(() => getListTournamentsQueryKey())],
  replaceTournament: [
    v(() => getListTournamentsQueryKey()),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  updateTournament: [
    v(() => getListTournamentsQueryKey()),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  updateTournamentBanner: [
    v(() => getListTournamentsQueryKey()),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  deleteTournamentBanner: [
    v(() => getListTournamentsQueryKey()),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  deleteTournament: [v(() => getListTournamentsQueryKey()), v(() => getGetAdminStatsQueryKey())],
  registerTeamForTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(({ vars }) => getListEligibleTeamsForTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(() => getGetTournamentTeamRegistrationQueryKey()),
    v(() => getGetTeamActiveTournamentQueryKey()),
    v(({ vars }) => getGetTournamentStatsQueryKey(vars.id as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],
  unregisterTeamFromTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(() => getGetTeamActiveTournamentQueryKey()),
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentStatsQueryKey(vars.id as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],
  disqualifyTeamFromTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(() => getGetTournamentTeamRegistrationQueryKey()),
    v(({ vars }) => getGetTournamentStatsQueryKey(vars.id as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],

  // Rounds
  createRound: [
    v(({ vars }) => getListRoundsQueryKey(vars.tournamentPk as number)),
    v(() => getGetMyCalendarQueryKey()),
  ],
  replaceRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  updateRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  deleteRound: [v(() => getListRoundsQueryKey()), v(() => getGetMyCalendarQueryKey())],
  startTournamentRegistration: [
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  startRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
    v(() => getGetCurrentTaskQueryKey()),
    v(({ data }) => getGetTournamentQueryKey(data.tournament as number)),
    v(({ data }) => getGetTournamentForUpdateQueryKey(data.tournament as number)),
    v(() => getGetMyCalendarQueryKey()),
  ],
  closeRoundSubmissions: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
    v(({ data }) => getGetCurrentTaskQueryKey({ tournament_id: data.tournament as number })),
  ],
  markRoundEvaluated: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
    v(({ vars }) => getGetRoundPassingStatusQueryKey(vars.id as number)),
    v(({ vars }) => getGetRoundLeaderboardQueryKey(vars.id as number)),
    v(({ data }) => getGetTournamentLeaderboardQueryKey(data.tournament as number)),
    v(() => getGetPlayerStatsQueryKey()),
    v(({ data }) => getGetTournamentStatsQueryKey(data.tournament as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],

  // Submissions
  createSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(() => getListMyTeamSubmissionsQueryKey()),
    v(() => getListRoundSubmissionsQueryKey()),
    v(() => getListTournamentSubmissionsQueryKey()),
    v(() => getGetCurrentTaskQueryKey()),
    v(() => getGetPlayerStatsQueryKey()),
    v(() => getGetAdminStatsQueryKey()),
  ],
  replaceSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(({ vars }) => getGetSubmissionQueryKey(vars.id as number)),
  ],
  updateSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(({ vars }) => getGetSubmissionQueryKey(vars.id as number)),
  ],

  // Events
  createEvent: [v(() => getListEventsQueryKey()), v(() => getGetMyCalendarQueryKey())],
  updateEvent: [
    v(() => getListEventsQueryKey()),
    v(({ vars }) => getGetEventQueryKey(vars.id as number)),
    v(() => getGetMyCalendarQueryKey()),
  ],
  deleteEvent: [v(() => getListEventsQueryKey()), v(() => getGetMyCalendarQueryKey())],

  // Accounts
  updateUserProfile: [v(() => getGetUserProfileQueryKey()), v(() => getGetAdminStatsQueryKey())],
  deleteUserProfile: [v(() => getGetAdminStatsQueryKey())],
  login: [v(() => getGetUserProfileQueryKey())],
  googleAuth: [v(() => getGetUserProfileQueryKey())],

  replaceUserProfile: [v(() => getGetUserProfileQueryKey())],

  updateUserAvatar: [v(() => getGetUserProfileQueryKey())],
  updateUserAvatar2: [v(() => getGetUserProfileQueryKey())],
  deleteUserAvatar: [v(() => getGetUserProfileQueryKey())],

  generateRoleActivationCodes: [v(() => getListRoleActivationCodesQueryKey())],

  // News
  createNews: [v(() => getListNewsQueryKey())],
  replaceNews: [
    v(() => getListNewsQueryKey()),
    v(({ vars }) => getGetNewsQueryKey(vars.id as number)),
  ],
  updateNews: [
    v(() => getListNewsQueryKey()),
    v(({ vars }) => getGetNewsQueryKey(vars.id as number)),
  ],
  deleteNews: [v(() => getListNewsQueryKey())],

  // Points
  modifyUserPointsBalance: [
    v(({ vars }) => getGetAdminUserPointsBalanceQueryKey(vars.userId as number)),
    v(({ vars }) => getListAdminUserPointsTransactionsQueryKey(vars.userId as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],

  // Shop
  purchaseProduct: [
    v(() => getListMyOrdersQueryKey()),
    v(() => getGetMyPointsBalanceQueryKey()),
    v(() => getListMyPointsTransactionsQueryKey()),
    v(() => getListMyDigitalInventoryQueryKey()),
    v(() => getGetAdminStatsQueryKey()),
    v(() => getListProductsQueryKey()),
  ],
  cancelMyOrder: [
    v(() => getListMyOrdersQueryKey()),
    v(() => getGetMyPointsBalanceQueryKey()),
    v(() => getListMyPointsTransactionsQueryKey()),
  ],
  createAdminCategory: [v(() => getListAdminCategoriesQueryKey())],
  replaceAdminCategory: [
    v(({ vars }) => getGetAdminCategoryQueryKey(vars.id as number)),
    v(() => getListAdminCategoriesQueryKey()),
  ],
  updateAdminCategory: [
    v(({ vars }) => getGetAdminCategoryQueryKey(vars.id as number)),
    v(() => getListAdminCategoriesQueryKey()),
  ],
  deleteAdminCategory: [v(() => getListAdminCategoriesQueryKey())],
  createAdminProduct: [v(() => getListAdminProductsQueryKey()), v(() => getListProductsQueryKey())],
  replaceAdminProduct: [
    v(({ vars }) => getGetAdminProductQueryKey(vars.id as number)),
    v(() => getListAdminProductsQueryKey()),
    v(() => getListProductsQueryKey()),
    v(({ vars }) => getGetProductQueryKey(vars.id as number)),
  ],
  updateAdminProduct: [
    v(({ vars }) => getGetAdminProductQueryKey(vars.id as number)),
    v(() => getListAdminProductsQueryKey()),
    v(() => getListProductsQueryKey()),
    v(({ vars }) => getGetProductQueryKey(vars.id as number)),
  ],
  deleteAdminProduct: [v(() => getListAdminProductsQueryKey()), v(() => getListProductsQueryKey())],
  updateAdminOrderStatus: [v(() => getListAdminOrdersQueryKey())],
  cancelAdminOrder: [v(() => getListAdminOrdersQueryKey())],
  createAdminAvatarFrame: [v(() => getListAdminAvatarFramesQueryKey())],
  replaceAdminAvatarFrame: [
    v(({ vars }) => getGetAdminAvatarFrameQueryKey(vars.id as number)),
    v(() => getListAdminAvatarFramesQueryKey()),
    v(() => getListAvatarFramesQueryKey()),
  ],
  updateAdminAvatarFrame: [
    v(({ vars }) => getGetAdminAvatarFrameQueryKey(vars.id as number)),
    v(() => getListAdminAvatarFramesQueryKey()),
    v(() => getListAvatarFramesQueryKey()),
  ],
  deleteAdminAvatarFrame: [
    v(() => getListAdminAvatarFramesQueryKey()),
    v(() => getListAvatarFramesQueryKey()),
  ],

  // Inventory
  equipDigitalInventoryItem: [v(() => getListMyDigitalInventoryQueryKey())],
  unequipDigitalInventoryItem: [v(() => getListMyDigitalInventoryQueryKey())],

  // Certificates
  createCertificate: [v(() => getListCertificatesQueryKey())],
  certificatesUpdate: [
    v(({ vars }) => getGetCertificateQueryKey(vars.uniqueCode as string)),
    v(() => getListCertificatesQueryKey()),
  ],
  updateCertificate: [
    v(({ vars }) => getGetCertificateQueryKey(vars.uniqueCode as string)),
    v(() => getListCertificatesQueryKey()),
  ],
  deleteCertificate: [v(() => getListCertificatesQueryKey())],

  // Certificate Templates
  createCertificateTemplate: [v(() => getListCertificateTemplatesQueryKey())],
  replaceCertificateTemplate: [
    v(({ vars }) => getGetCertificateTemplateQueryKey(vars.id as number)),
    v(() => getListCertificateTemplatesQueryKey()),
  ],
  updateCertificateTemplate: [
    v(({ vars }) => getGetCertificateTemplateQueryKey(vars.id as number)),
    v(() => getListCertificateTemplatesQueryKey()),
  ],
  deleteCertificateTemplate: [v(() => getListCertificateTemplatesQueryKey())],

  // Notifications
  deleteNotification: [
    v(() => getListNotificationsQueryKey()),
    v(() => getGetUnreadNotificationCountQueryKey()),
  ],
  markNotificationRead: [
    v(() => getListNotificationsQueryKey()),
    v(() => getGetUnreadNotificationCountQueryKey()),
  ],
  deleteAllNotifications: [
    v(() => getListNotificationsQueryKey()),
    v(() => getGetUnreadNotificationCountQueryKey()),
  ],
  markAllNotificationsRead: [
    v(() => getListNotificationsQueryKey()),
    v(() => getGetUnreadNotificationCountQueryKey()),
  ],
  updateNotificationConfig: [v(() => getGetNotificationSettingsQueryKey())],
  updateGlobalNotificationConfig: [v(() => getGetNotificationSettingsQueryKey())],
}

export const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: (data, vars, _ctx, mutation) => {
      const key = mutation.options.mutationKey?.[0] as string | undefined
      if (!key) return

      // Зберегти токен ДО інвалідації
      if ((key === 'login' || key === 'googleAuth') && data) {
        const d = data as { access?: string; refresh?: string }
        if (d.access) localStorage.setItem('access', d.access)
        if (d.refresh) localStorage.setItem('refresh', d.refresh)
      }

      const entries = MUTATION_INVALIDATION_MAP[key] ?? []
      const ctx: Ctx = {
        vars: (vars ?? {}) as Ctx['vars'],
        data: (data ?? {}) as Ctx['data'],
      }

      console.log(ctx, key)

      entries.forEach((entry) => {
        queryClient.invalidateQueries({ queryKey: entry(ctx) })
      })
    },
  }),
})
