import type { AxiosError } from 'axios'
import type { MaybeRefArgs, MutationConfig, QueryConfig } from '../types'
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
  GetTournamentsResponse,
  RegisterTeamArgs,
  StartRegistrationArgs,
  StartRoundArgs,
  StartRoundResponse,
  SubmitRoundArgs,
} from '@/api/services/tournaments/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { $api } from '@/api/services'
import { tournamentsKeys } from '../keys'
import { computed, toValue } from 'vue'
import type { ApiError } from '@/api/errors'
import type { TournamentId } from '@/api/dbTypes'

export const useTournaments = (
  payload: MaybeRefArgs<GetTournamentsArgs>,
  config?: QueryConfig<GetTournamentsResponse>,
) => {
  const queryKey = computed(() =>
    tournamentsKeys.tournamentsLists({
      page: toValue(payload.page),
      searchQuery: toValue(payload.searchQuery),
      status: toValue(payload.status),
      pageSize: toValue(payload.pageSize),
    }),
  )

  return useQuery<GetTournamentsResponse, AxiosError<ApiError>>({
    queryKey,
    queryFn: () =>
      $api.tournaments.getTournaments({
        page: toValue(payload.page),
        searchQuery: toValue(payload.searchQuery),
        pageSize: toValue(payload.pageSize),
        status: toValue(payload.status),
      }),
    ...config,
  })
}

export const useRegisteredTeams = (
  payload: GetRegisteredTeamsArgs,
  config?: QueryConfig<GetRegisteredTeamsResponse>,
) => {
  return useQuery<GetRegisteredTeamsResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.registeredTeams(payload.id),
    queryFn: () => $api.tournaments.getRegisteredTeams({ id: payload.id }),
    ...config,
  })
}

export const useTournamentRounds = (
  payload: GetRoundsArgs,
  config?: QueryConfig<GetRoundsResponse>,
) => {
  return useQuery<GetRoundsResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.rounds(payload.id),
    queryFn: () => $api.tournaments.getRounds({ id: payload.id }),
    ...config,
  })
}

export const useActiveTeamTournament = (
  payload: GetActiveTeamTournamentArgs,
  config?: QueryConfig<GetActiveTeamTournamentResponse>,
) => {
  return useQuery<GetActiveTeamTournamentResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.activeTeamTournament(payload.id),
    queryFn: () => $api.tournaments.getActiveTeamTournament({ id: payload.id }),
    ...config,
  })
}

export const useCreateTournament = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof CreateTournamentArgs['body']>>,
    CreateTournamentArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof CreateTournamentArgs['body']>>,
    CreateTournamentArgs
  >({
    mutationFn: $api.tournaments.createTournament,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.lists() })
    },
    ...config,
  })
}

export const useTournamentInfo = (
  payload: GetTournamentInfoArgs,
  config?: QueryConfig<GetTournamentInfoResponse>,
) => {
  return useQuery<GetTournamentInfoResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.touranment(payload.id),
    queryFn: () => $api.tournaments.getTournamentInfo({ id: payload.id }),
    ...config,
  })
}

export const useEligibleTeams = (
  payload: GetEligibleTeamsArgs,
  config?: QueryConfig<GetEligibleTeamsResponse>,
) => {
  return useQuery<GetEligibleTeamsResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.eligibleTeams(payload.id),
    queryFn: () => $api.tournaments.getEligibleTeams({ id: payload.id }),
    ...config,
  })
}

export const useCreateRound = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof CreateRoundArgs['body']>>,
    CreateRoundArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError<keyof CreateRoundArgs['body']>>, CreateRoundArgs>(
    {
      mutationFn: $api.tournaments.createRound,
      onSuccess: (_data, vars) => {
        queryClient.invalidateQueries({ queryKey: tournamentsKeys.rounds(vars.id) })
      },
      ...config,
    },
  )
}

export const useDeleteRound = (
  payload: { id: TournamentId },
  config?: MutationConfig<unknown, AxiosError<ApiError>, DeleteRoundArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, DeleteRoundArgs>({
    mutationFn: $api.tournaments.deleteRound,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.rounds(payload.id) })
    },
    ...config,
  })
}

export const useCurrentRound = (
  payload: GetCurrentRoundArgs,
  config?: QueryConfig<GetCurrentRoundResponse>,
) => {
  return useQuery<GetCurrentRoundResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.currentRound(payload.id),
    queryFn: () => $api.tournaments.getCurrentRound({ id: payload.id }),
    ...config,
  })
}

export const useRegisterTeam = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof RegisterTeamArgs['body']>>,
    RegisterTeamArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof RegisterTeamArgs['body']>>,
    RegisterTeamArgs
  >({
    mutationFn: $api.tournaments.registerTeam,
    onSuccess: (_data, vars) => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.eligibleTeams(vars.id) })
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.registeredTeams(vars.id) })
    },
    ...config,
  })
}

export const useSubmitRound = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof SubmitRoundArgs['body']>>,
    SubmitRoundArgs
  >,
) => {
  return useMutation<unknown, AxiosError<ApiError<keyof SubmitRoundArgs['body']>>, SubmitRoundArgs>(
    {
      mutationFn: $api.tournaments.submitRound,
      ...config,
    },
  )
}

export const useCreateEvent = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof CreateEventArgs['body']>>,
    CreateEventArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError<keyof CreateEventArgs['body']>>, CreateEventArgs>(
    {
      mutationFn: $api.tournaments.createEvent,
      ...config,
      onSuccess: (_data, vars) => {
        queryClient.invalidateQueries({ queryKey: tournamentsKeys.events(vars.body.tournament) })
      },
    },
  )
}

export const useTournamentEvents = (
  payload: GetEventsArgs,
  config?: QueryConfig<GetEventsResponse>,
) => {
  return useQuery<GetEventsResponse, AxiosError<ApiError>>({
    queryKey: tournamentsKeys.events(payload.tournamentId),
    queryFn: () => $api.tournaments.getEvents({ tournamentId: payload.tournamentId }),
    ...config,
  })
}

export const useEditEvent = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof EditEventArgs['body']>>,
    EditEventArgs
  >,
) => {
  return useMutation<unknown, AxiosError<ApiError<keyof EditEventArgs['body']>>, EditEventArgs>({
    mutationFn: $api.tournaments.editEvent,
    ...config,
  })
}

export const useDeleteEvent = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, DeleteEventArgs>,
) => {
  return useMutation<unknown, AxiosError<ApiError>, DeleteEventArgs>({
    mutationFn: $api.tournaments.deleteEvent,
    ...config,
  })
}

export const useStartRegistration = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, StartRegistrationArgs>,
) => {
  const queryClient = useQueryClient()

  return useMutation<unknown, AxiosError<ApiError>, StartRegistrationArgs>({
    mutationFn: $api.tournaments.startRegistration,
    onSuccess: (_data, args) => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.detail(args.tournamentId) })
    },
    ...config,
  })
}

export const useStartRound = (
  config?: MutationConfig<StartRoundResponse, AxiosError<ApiError>, StartRoundArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<StartRoundResponse, AxiosError<ApiError>, StartRoundArgs>({
    mutationFn: $api.tournaments.startRound,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.rounds(data.tournament) })
    },
    ...config,
  })
}

export const useCloseSubmissions = (
  config?: MutationConfig<CloseSubmissionsResponse, AxiosError<ApiError>, CloseSubmissionsArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<CloseSubmissionsResponse, AxiosError<ApiError>, CloseSubmissionsArgs>({
    mutationFn: $api.tournaments.closeSubmissions,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: tournamentsKeys.rounds(data.tournament) })
      queryClient.resetQueries({ queryKey: tournamentsKeys.currentRound(data.tournament) })
    },
    ...config,
  })
}
