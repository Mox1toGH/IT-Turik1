import { MutationCache, QueryCache, QueryClient } from '@tanstack/vue-query'
import { connectNotificationSocket } from '@/lib/notificationSocket'

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
  getListNotificationsQueryKey,
  getGetUnreadNotificationCountQueryKey,
  getGetNotificationSettingsQueryKey,
} from '@/api/notifications/notifications'

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
import type { ApiErrorResponse } from '@/shared/types/apiError'
import type { ErrorType } from './apiClient'

type Ctx = {
  vars: Record<string, unknown>
  data: Record<string, unknown>
}

type InvalidationEntry = (ctx: Ctx) => readonly unknown[]

const v = (fn: InvalidationEntry): InvalidationEntry => fn

/**
 * Generated key helpers always emit a slot for every path param and fill the ones
 * the caller omitted with `undefined`. React Query compares a filter key element by
 * element, so a key with a hole in the middle compares unequal to the real key and
 * the invalidation silently does nothing. Cutting the key off at the first unknown
 * slot leaves a prefix that does match every key of that endpoint family.
 */
const knownKey = (key: readonly unknown[]): readonly unknown[] => {
  const unknownAt = key.findIndex((part) => part === undefined || part === null)
  return unknownAt === -1 ? key : key.slice(0, unknownAt)
}

/** Read a numeric id out of a mutation payload whose shape we do not control. */
const nestedId = (source: unknown, ...path: string[]): number | null => {
  let current: unknown = source
  for (const part of path) {
    if (current === null || typeof current !== 'object') return null
    current = (current as Record<string, unknown>)[part]
  }
  return typeof current === 'number' ? current : null
}

const MUTATION_INVALIDATION_MAP: Record<string, InvalidationEntry[]> = {
  // Teams
  createTeam: [v(() => getListTeamsQueryKey())],
  updateTeam: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
  ],
  teamBannerUpdate: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
  ],
  deleteTeamBanner: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
  ],
  deleteTeam: [v(() => getListTeamsQueryKey())],
  leaveTeam: [
    v(() => getListTeamsQueryKey()),
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
  ],
  removeMemberFromTeam: [v(({ vars }) => getGetTeamQueryKey(vars.pk as number))],
  inviteMemberToTeam: [
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
    v(({ vars }) => getListTeamInvitationsByTeamQueryKey(vars.pk as number)),
  ],
  acceptTeamJoinRequest: [
    v(({ vars }) => getGetTeamQueryKey(vars.pk as number)),
    v(({ vars }) => getListTeamJoinRequestsByTeamQueryKey(vars.pk as number)),
  ],
  declineTeamJoinRequest: [
    v(({ vars }) => getListTeamJoinRequestsByTeamQueryKey(vars.pk as number)),
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
    v(({ data }) => getGetJuryEvaluationQueryKey(nestedId(data, 'id') ?? undefined)),
  ],
  updateJuryEvaluation: [
    v(({ vars }) => getGetJuryEvaluationQueryKey(vars.evaluationId as number)),
    v(() => getListJuryAssignmentsQueryKey()),
  ],
  deleteJuryEvaluation: [
    v(({ vars }) => getGetJuryEvaluationQueryKey(vars.evaluationId as number)),
    v(() => getListJuryAssignmentsQueryKey()),
  ],
  assignJuryToRound: [
    v(() => getListJuryAssignmentsQueryKey()),
    v(({ vars }) => getListAvailableJuryQueryKey(vars.roundId as number)),
    v(({ vars }) => getGetRoundPassingStatusQueryKey(vars.roundId as number)),
    v(({ vars }) => getListRoundSubmissionsQueryKey(vars.roundId as number)),
  ],

  // Tournaments
  createTournament: [v(() => getListTournamentsQueryKey())],
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
    v(({ vars }) => getGetTournamentTeamRegistrationQueryKey(vars.id as number)),
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
    v(({ vars }) => getGetTournamentTeamRegistrationQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentStatsQueryKey(vars.id as number)),
    v(() => getGetAdminStatsQueryKey()),
  ],

  // Rounds
  createRound: [
    v(({ vars }) => getListRoundsQueryKey(vars.tournamentPk as number)),
    v(() => getGetMyCalendarQueryKey()),
  ],
  updateRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  // The round id alone cannot address a rounds list, so this refreshes every
  // tournament-scoped query (the round card lives on the tournament page anyway).
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
    // The submission response nests the ids the list keys need; when a payload has
    // no body the key falls back to the endpoint family prefix (see knownKey).
    v(({ data }) =>
      getListMyTeamSubmissionsQueryKey(nestedId(data, 'round_details', 'tournament') ?? undefined),
    ),
    v(({ data }) => getListRoundSubmissionsQueryKey(nestedId(data, 'round') ?? undefined)),
    v(({ data }) =>
      getListTournamentSubmissionsQueryKey(
        nestedId(data, 'round_details', 'tournament') ?? undefined,
      ),
    ),
    v(() => getGetCurrentTaskQueryKey()),
    v(() => getGetPlayerStatsQueryKey()),
    v(() => getGetAdminStatsQueryKey()),
  ],
  updateSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(({ vars }) => getGetSubmissionQueryKey(vars.id as number)),
    // "My submissions" lives under the tournament, which only the response knows.
    v(({ data }) =>
      getListMyTeamSubmissionsQueryKey(nestedId(data, 'round_details', 'tournament') ?? undefined),
    ),
    v(({ data }) => getListRoundSubmissionsQueryKey(nestedId(data, 'round') ?? undefined)),
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

  updateUserAvatar: [v(() => getGetUserProfileQueryKey())],
  deleteUserAvatar: [v(() => getGetUserProfileQueryKey())],

  generateRoleActivationCodes: [v(() => getListRoleActivationCodesQueryKey())],

  // News
  createNews: [v(() => getListNewsQueryKey())],
  updateNews: [
    v(() => getListNewsQueryKey()),
    v(({ vars }) => getGetNewsQueryKey(vars.articleId as number)),
  ],
  deleteNews: [v(() => getListNewsQueryKey())],

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

/**
 * Filter keys to invalidate after a mutation succeeded. Exported so the wiring can
 * be asserted against the generated query keys in tests.
 */
export const invalidationKeys = (
  mutationKey: string | undefined,
  vars: unknown,
  data: unknown,
): readonly (readonly unknown[])[] => {
  if (!mutationKey) return []
  const entries = MUTATION_INVALIDATION_MAP[mutationKey] ?? []
  const ctx: Ctx = {
    vars: (vars ?? {}) as Ctx['vars'],
    data: (data ?? {}) as Ctx['data'],
  }

  // `vars` and `data` come from the generated client and are only as complete as the
  // endpoint makes them, so every key is trimmed to its known part.
  return entries.map((entry) => knownKey(entry(ctx)))
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (count, err) => {
        const s = (err as { _axiosError?: { response?: { status?: number } } })?._axiosError
          ?.response?.status
        return (!s || s >= 500) && count < 2
      },
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      const status = (error as ErrorType<ApiErrorResponse>)?._axiosError?.response?.status
      // 401 is handled globally (tokens cleared + redirect in the axios
      // interceptor); cards never render a 401 error state.
      if (status === 401) {
        console.warn('[query] unauthorized (401): redirect handled by api interceptor')
        return
      }
      console.error('[query] failed:', error)
    },
  }),
  mutationCache: new MutationCache({
    onSuccess: (data, vars, _ctx, mutation) => {
      const key = mutation.options.mutationKey?.[0] as string | undefined
      if (!key) return

      // Зберегти токен ДО інвалідації
      if ((key === 'login' || key === 'googleAuth') && data) {
        const d = data as { access?: string; refresh?: string }
        if (d.access) localStorage.setItem('access', d.access)
        if (d.refresh) localStorage.setItem('refresh', d.refresh)
        connectNotificationSocket(queryClient)
      }

      invalidationKeys(key, vars, data).forEach((queryKey) => {
        queryClient.invalidateQueries({ queryKey })
      })
    },
  }),
})
