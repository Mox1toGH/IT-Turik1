import { apiClient } from '@/api/client'
import type {
  CloseSubmissionsArgs,
  CloseSubmissionsResponse,
  CreateEventArgs,
  CreateRoundArgs,
  CreateTournamentArgs,
  DeleteEventArgs,
  DeleteRoundArgs,
  EditEventArgs,
  EditRoundArgs,
  EditRoundResponse,
  EditSubmissionArgs,
  EditSubmissionResponse,
  GetActiveTeamTournamentArgs,
  GetActiveTeamTournamentResponse,
  GetCurrentRoundArgs,
  GetCurrentRoundResponse,
  GetEligibleTeamsArgs,
  GetEligibleTeamsResponse,
  GetEventsArgs,
  GetEventsResponse,
  LeaveTeamArgs,
  GetRegisteredTeamsArgs,
  GetRegisteredTeamsResponse,
  GetRoundsArgs,
  GetRoundsResponse,
  GetRoundSubmissionsArgs,
  GetRoundSubmissionsResponse,
  GetTeamSubmissionsArgs,
  GetTeamSubmissionsResponse,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
  GetTournamentsArgs,
  MarkEvaluatedArgs,
  MarkEvaluatedResponse,
  RegisterTeamArgs,
  StartRegistrationArgs,
  StartRoundArgs,
  StartRoundResponse,
  SubmitRoundArgs,
  UpdateRegistrationArgs,
  UpdateRegistrationResponse,
} from './types'
import { toValue } from 'vue'
import type { MaybeRefArgs } from '@/api/queries/types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  getTournaments: async (args: MaybeRefArgs<GetTournamentsArgs>) => {
    const params = new URLSearchParams()
    params.append('page', String(toValue(args.page)))

    if (toValue(args.pageSize)) {
      params.append('pageSize', String(toValue(args.pageSize)))
    }
    if (toValue(args.searchQuery)) {
      params.append('searchQuery', String(toValue(args.searchQuery)))
    }
    if (toValue(args.status)) {
      params.append('status', toValue(args.status)!.join(','))
    }

    const { data } = await apiClient.get(`${prefix}?${params.toString()}`)
    return data
  },

  async getActiveTeamTournament(args: MaybeRefArgs<GetActiveTeamTournamentArgs>) {
    const params = new URLSearchParams()
    params.append('team_id', String(toValue(args.id)))

    const { data } = await apiClient.get<GetActiveTeamTournamentResponse>(
      `${prefix}/active?${params.toString()}`,
    )
    return data
  },

  getRegisteredTeams: async (args: MaybeRefArgs<GetRegisteredTeamsArgs>) => {
    const params = new URLSearchParams()
    const status = toValue(args.status)
    if (status) {
      params.append('status', status)
    }
    if (args.includeInactive) {
      params.append('include_inactive', 'true')
    }
    const query = params.toString()
    const url = query
      ? `${prefix}/${args.id}/teams?${query}`
      : `${prefix}/${toValue(args.id)}/teams`
    const { data } = await apiClient.get<GetRegisteredTeamsResponse>(url)
    return data
  },

  getRounds: async (args: MaybeRefArgs<GetRoundsArgs>) => {
    const { data } = await apiClient.get<GetRoundsResponse>(`${prefix}/${toValue(args.id)}/rounds`)
    return data
  },

  createTournament: async (args: MaybeRefArgs<CreateTournamentArgs>) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, toValue(args.body))
    return data
  },

  getTournamentInfo: async (args: MaybeRefArgs<GetTournamentInfoArgs>) => {
    const { data } = await apiClient.get<GetTournamentInfoResponse>(`${prefix}/${toValue(args.id)}`)
    return data
  },

  getEligibleTeams: async (args: MaybeRefArgs<GetEligibleTeamsArgs>) => {
    const { data } = await apiClient.get<GetEligibleTeamsResponse>(
      `${prefix}/${toValue(args.id)}/eligible-teams`,
    )
    return data
  },

  createRound: async (args: MaybeRefArgs<CreateRoundArgs>) => {
    const { data } = await apiClient.post(
      `${prefix}/${toValue(args.id)}/rounds/`,
      toValue(args.body),
    )
    return data
  },

  editRound: async (args: MaybeRefArgs<EditRoundArgs>) => {
    const { data } = await apiClient.patch<EditRoundResponse>(
      `${prefix}/rounds/${toValue(args.id)}/`,
      toValue(args.body),
    )
    return data
  },

  deleteRound: async (args: MaybeRefArgs<DeleteRoundArgs>) => {
    const { data } = await apiClient.delete(`${prefix}/rounds/${toValue(args.id)}/`)
    return data
  },

  getCurrentRound: async (args: MaybeRefArgs<GetCurrentRoundArgs>) => {
    const { data } = await apiClient.get<GetCurrentRoundResponse>(
      `${prefix}/current-task/?tournament_id=${toValue(args.id)}`,
    )
    return data
  },

  registerTeam: async (args: MaybeRefArgs<RegisterTeamArgs>) => {
    const { data } = await apiClient.post(
      `${prefix}/${toValue(args.id)}/register-team/`,
      toValue(args.body),
    )
    return data
  },

  leaveTeam: async (args: MaybeRefArgs<LeaveTeamArgs>) => {
    const { data } = await apiClient.post(
      `${prefix}/${toValue(args.id)}/leave-team/`,
      toValue(args.body),
    )
    return data
  },

  submitRound: async (args: MaybeRefArgs<SubmitRoundArgs>) => {
    const { data } = await apiClient.post(`${prefix}/submissions/`, toValue(args.body))
    return data
  },

  createEvent: async (args: MaybeRefArgs<CreateEventArgs>) => {
    const { data } = await apiClient.post(`${prefix}/events/`, toValue(args.body))
    return data
  },

  getEvents: async (args: MaybeRefArgs<GetEventsArgs>) => {
    const params = new URLSearchParams()
    params.append('tournament', String(toValue(args.tournamentId)))

    const { data } = await apiClient.get<GetEventsResponse>(`${prefix}/events?${params.toString()}`)
    return data
  },

  editEvent: async (args: MaybeRefArgs<EditEventArgs>) => {
    const { data } = await apiClient.patch(
      `${prefix}/events/${toValue(args.eventId)}/`,
      toValue(args.body),
    )
    return data
  },

  deleteEvent: async (args: MaybeRefArgs<DeleteEventArgs>) => {
    const { data } = await apiClient.delete(`${prefix}/events/${toValue(args.eventId)}/`)
    return data
  },

  startRegistration: async (args: MaybeRefArgs<StartRegistrationArgs>) => {
    const { data } = await apiClient.post(
      `${prefix}/${toValue(args.tournamentId)}/start-registration/`,
    )
    return data
  },

  startRound: async (args: MaybeRefArgs<StartRoundArgs>) => {
    const { data } = await apiClient.post<StartRoundResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/start/`,
    )
    return data
  },

  closeSubmissions: async (args: MaybeRefArgs<CloseSubmissionsArgs>) => {
    const { data } = await apiClient.post<CloseSubmissionsResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/close-submissions/`,
    )
    return data
  },

  markEvaluated: async (args: MaybeRefArgs<MarkEvaluatedArgs>) => {
    const { data } = await apiClient.post<MarkEvaluatedResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/mark-evaluated/`,
    )
    return data
  },

  getTeamSubmissions: async (args: MaybeRefArgs<GetTeamSubmissionsArgs>) => {
    const { data } = await apiClient.get<GetTeamSubmissionsResponse>(
      `${prefix}/${toValue(args.tournamentId)}/my-submissions/`,
    )
    return data
  },

  editSubmission: async (args: MaybeRefArgs<EditSubmissionArgs>) => {
    const { data } = await apiClient.patch<EditSubmissionResponse>(
      `${prefix}/submissions/${toValue(args.submissionId)}/`,
      toValue(args.body),
    )
    return data
  },

  getRoundSubmissions: async (args: MaybeRefArgs<GetRoundSubmissionsArgs>) => {
    const { data } = await apiClient.get<GetRoundSubmissionsResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/submissions`,
    )
    return data
  },

  updateRegistration: async (args: MaybeRefArgs<UpdateRegistrationArgs>) => {
    const { data } = await apiClient.patch<UpdateRegistrationResponse>(
      `${prefix}/${args.tournamentId}/registrations/${toValue(args.registrationId)}/disqualification/`,
      args.body,
    )
    return data
  },
}
