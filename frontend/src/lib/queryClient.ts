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
} from '@/api/tournaments/tournaments'

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
  deleteTournament: [v(() => getListTournamentsQueryKey())],
  startTournamentRegistration: [
    v(({ vars }) => getGetTournamentQueryKey(vars.id as number)),
    v(({ vars }) => getGetTournamentForUpdateQueryKey(vars.id as number)),
  ],
  registerTeamForTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(({ vars }) => getListEligibleTeamsForTournamentQueryKey(vars.id as number)),
    v(() => getGetTournamentTeamRegistrationQueryKey()),
    v(() => getGetTeamActiveTournamentQueryKey()),
  ],
  unregisterTeamFromTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(() => getGetTeamActiveTournamentQueryKey()),
  ],
  disqualifyTeamFromTournament: [
    v(({ vars }) => getListTournamentTeamsQueryKey(vars.id as number)),
    v(() => getGetTournamentTeamRegistrationQueryKey()),
  ],

  // Rounds
  createRound: [v(({ vars }) => getListRoundsQueryKey(vars.tournamentPk as number))],
  replaceRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  updateRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  deleteRound: [v(() => getListRoundsQueryKey())],
  startRound: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
    v(() => getGetCurrentTaskQueryKey()),
  ],
  closeRoundSubmissions: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
  ],
  markRoundEvaluated: [
    v(({ vars }) => getGetRoundQueryKey(vars.id as number)),
    v(({ data }) => getListRoundsQueryKey(data.tournament as number)),
    v(({ vars }) => getGetRoundPassingStatusQueryKey(vars.id as number)),
    v(({ vars }) => getGetRoundLeaderboardQueryKey(vars.id as number)),
    v(({ data }) => getGetTournamentLeaderboardQueryKey(data.tournament as number)),
  ],

  // Submissions
  createSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(() => getListMyTeamSubmissionsQueryKey()),
    v(() => getListRoundSubmissionsQueryKey()),
    v(() => getListTournamentSubmissionsQueryKey()),
    v(() => getGetCurrentTaskQueryKey()),
  ],
  replaceSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(({ vars }) => getGetSubmissionQueryKey(vars.id as number)),
  ],
  updateSubmission: [
    v(() => getListSubmissionsQueryKey()),
    v(({ vars }) => getGetSubmissionQueryKey(vars.id as number)),
  ],

  createEvent: [v(() => getListEventsQueryKey())],
  updateEvent: [
    v(() => getListEventsQueryKey()),
    v(({ vars }) => getGetEventQueryKey(vars.id as number)),
  ],
  deleteEvent: [v(() => getListEventsQueryKey())],
}

export const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: (data, vars, _ctx, mutation) => {
      const key = mutation.options.mutationKey?.[0] as string | undefined
      if (!key) return

      const entries = MUTATION_INVALIDATION_MAP[key] ?? []
      const ctx: Ctx = {
        vars: (vars ?? {}) as Ctx['vars'],
        data: (data ?? {}) as Ctx['data'],
      }

      entries.forEach((entry) => {
        queryClient.invalidateQueries({ queryKey: entry(ctx) })
      })
    },
  }),
})
