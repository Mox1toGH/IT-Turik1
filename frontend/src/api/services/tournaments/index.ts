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
  GetPassingStatusArgs,
  GetPassingStatusResponse,
  PassingStatusResult,
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
  RegisterTeamArgs,
  StartRegistrationArgs,
  StartRoundArgs,
  StartRoundResponse,
  SubmitRoundArgs,
  UpdateRegistrationArgs,
  UpdateRegistrationResponse,
} from './types'
import { toValue } from 'vue'

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
    const params = new URLSearchParams()
    if (args.includeInactive) {
      params.append('include_inactive', 'true')
    }
    const query = params.toString()
    const url = query ? `${prefix}/${args.id}/teams?${query}` : `${prefix}/${args.id}/teams`
    const { data } = await apiClient.get<GetRegisteredTeamsResponse>(url)
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

  editRound: async (args: EditRoundArgs) => {
    const { data } = await apiClient.patch<EditRoundResponse>(
      `${prefix}/rounds/${args.id}/`,
      args.body,
    )
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

  leaveTeam: async (args: LeaveTeamArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.id}/leave-team/`, args.body)
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

  getTeamSubmissions: async (args: GetTeamSubmissionsArgs) => {
    const { data } = await apiClient.get<GetTeamSubmissionsResponse>(
      `${prefix}/${args.tournamentId}/my-submissions/`,
    )
    return data
  },

  editSubmission: async (args: EditSubmissionArgs) => {
    const { data } = await apiClient.patch<EditSubmissionResponse>(
      `${prefix}/submissions/${args.submissionId}/`,
      args.body,
    )
    return data
  },

  getRoundSubmissions: async (args: GetRoundSubmissionsArgs) => {
    const { data } = await apiClient.get<GetRoundSubmissionsResponse>(
      `${prefix}/rounds/${toValue(args.roundId)}/submissions`,
    )
    return data
  },

  getPassingStatus: async (args: GetPassingStatusArgs) => {
    // TODO: Replace with actual passing-status endpoint when backend is ready
    // For now, using leaderboard data and computing passed status
    const { data: leaderboardData } = await apiClient.get(
      `/api/evaluation/tournaments/rounds/${args.roundId}/leaderboard/`
    )

    // Get round data to determine passing_count
    const { data: roundData } = await apiClient.get(`/api/tournaments/rounds/${args.roundId}/`)

    // Get registered teams to determine active status
    const { data: registeredTeams } = await apiClient.get(
      `/api/tournaments/${roundData.tournament}/teams/`
    )

    const passingCount = roundData.passing_count
    const rankings = leaderboardData.rankings || []

    // Create team active status map and registration ID map
    const teamActiveMap = new Map()
    const teamRegistrationMap = new Map()
    registeredTeams.forEach((team: any) => {
      teamActiveMap.set(team.id, team.is_active)
      teamRegistrationMap.set(team.id, team.registration_id)
    })

    // Transform leaderboard data to passing status format
    const results: PassingStatusResult[] = rankings.map((ranking: any, index: number) => {
      const passed = passingCount ? ranking.rank <= passingCount : true
      const is_active = teamActiveMap.get(ranking.team_id) ?? true

      return {
        rank: ranking.rank,
        team_id: ranking.team_id,
        team_name: ranking.team_name,
        total_score: ranking.total_score,
        average_score: ranking.average_score,
        passed,
        is_active,
        registration_id: teamRegistrationMap.get(ranking.team_id) ?? ranking.team_id
      }
    })

    return results
  },

  updateRegistration: async (args: UpdateRegistrationArgs) => {
    const { data } = await apiClient.patch<UpdateRegistrationResponse>(
      `${prefix}/${args.tournamentId}/registrations/${args.registrationId}/`,
      { is_active: args.action === 'activated' },
    )
    return data
  },
}
