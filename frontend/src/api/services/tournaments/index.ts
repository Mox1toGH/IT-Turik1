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
  GetActiveTeamTournamentArgs,
  GetActiveTeamTournamentResponse,
  GetCurrentRoundArgs,
  GetCurrentRoundResponse,
  GetEligibleTeamsArgs,
  GetEligibleTeamsResponse,
  GetEventsArgs,
  GetEventsResponse,
  GetRegisteredTeamsArgs,
  GetRegisteredTeamsResponse,
  GetRoundsArgs,
  GetRoundsResponse,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
  GetTournamentsArgs,
  RegisterTeamArgs,
  StartRegistrationArgs,
  StartRoundArgs,
  StartRoundResponse,
  SubmitRoundArgs,
} from './types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  getTournaments: async (args: GetTournamentsArgs) => {
    const params = new URLSearchParams()
    params.append('page', String(args.page))

    if (args.pageSize) {
      params.append('pageSize', String(args.pageSize))
    }
    if (args.searchQuery) {
      params.append('searchQuery', args.searchQuery)
    }
    if (args.status) {
      params.append('status', args.status.join(','))
    }

    const { data } = await apiClient.get(`${prefix}?${params.toString()}`)
    return data
  },

  async getActiveTeamTournament(args: GetActiveTeamTournamentArgs) {
    const params = new URLSearchParams()
    params.append('team_id', String(args.id))

    const { data } = await apiClient.get<GetActiveTeamTournamentResponse>(
      `${prefix}/active?${params.toString()}`,
    )
    return data
  },

  getRegisteredTeams: async (args: GetRegisteredTeamsArgs) => {
    const { data } = await apiClient.get<GetRegisteredTeamsResponse>(`${prefix}/${args.id}/teams`)
    return data
  },

  getRounds: async (args: GetRoundsArgs) => {
    const { data } = await apiClient.get<GetRoundsResponse>(`${prefix}/${args.id}/rounds`)
    return data
  },

  createTournament: async (args: CreateTournamentArgs) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, args.body)
    return data
  },

  getTournamentInfo: async (args: GetTournamentInfoArgs) => {
    const { data } = await apiClient.get<GetTournamentInfoResponse>(`${prefix}/${args.id}`)
    return data
  },

  getEligibleTeams: async (args: GetEligibleTeamsArgs) => {
    const { data } = await apiClient.get<GetEligibleTeamsResponse>(
      `${prefix}/${args.id}/eligible-teams`,
    )
    return data
  },

  createRound: async (args: CreateRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.id}/rounds/`, args.body)
    return data
  },

  deleteRound: async (args: DeleteRoundArgs) => {
    const { data } = await apiClient.delete(`${prefix}/rounds/${args.id}/`)
    return data
  },

  getCurrentRound: async (args: GetCurrentRoundArgs) => {
    const { data } = await apiClient.get<GetCurrentRoundResponse>(
      `${prefix}/current-task/?tournament_id=${args.id}`,
    )
    return data
  },

  registerTeam: async (args: RegisterTeamArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.id}/register-team/`, args.body)
    return data
  },

  submitRound: async (args: SubmitRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/submissions/`, args.body)
    return data
  },

  createEvent: async (args: CreateEventArgs) => {
    const { data } = await apiClient.post(`${prefix}/events/`, args.body)
    return data
  },

  getEvents: async (args: GetEventsArgs) => {
    const params = new URLSearchParams()
    params.append('tournament', String(args.tournamentId))

    const { data } = await apiClient.get<GetEventsResponse>(`${prefix}/events?${params.toString()}`)
    return data
  },

  editEvent: async (args: EditEventArgs) => {
    const { data } = await apiClient.patch(`${prefix}/events/${args.eventId}/`, args.body)
    return data
  },

  deleteEvent: async (args: DeleteEventArgs) => {
    const { data } = await apiClient.delete(`${prefix}/events/${args.eventId}/`)
    return data
  },

  startRegistration: async (args: StartRegistrationArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.tournamentId}/start-registration/`)
    return data
  },

  startRound: async (args: StartRoundArgs) => {
    const { data } = await apiClient.post<StartRoundResponse>(
      `${prefix}/rounds/${args.roundId}/start/`,
    )
    return data
  },

  closeSubmissions: async (args: CloseSubmissionsArgs) => {
    const { data } = await apiClient.post<CloseSubmissionsResponse>(
      `${prefix}/rounds/${args.roundId}/close-submissions/`,
    )
    return data
  },
}
