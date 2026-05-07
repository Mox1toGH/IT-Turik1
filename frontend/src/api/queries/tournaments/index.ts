import type { AxiosError } from 'axios'
import type { MaybeRefArgs, MutationConfig, QueryConfig } from '../types'
import type {
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
  SubmitRoundArgs,
} from '@/api/services/tournaments/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { $api } from '@/api/services'
import { touranmentsKeys } from '../keys'
import { computed, toValue } from 'vue'
import type { ApiError } from '@/api/errors'
import type { TournamentId } from '@/api/dbTypes'

export const useTournaments = (
  payload: MaybeRefArgs<GetTournamentsArgs>,
  config?: QueryConfig<GetTournamentsResponse>,
) => {
  const queryKey = computed(() =>
    touranmentsKeys['tournaments-list']({
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
    staleTime: 1000 * 60 * 5,
    ...config,
  })
}

export const useRegisteredTeams = (
  payload: GetRegisteredTeamsArgs,
  config?: QueryConfig<GetRegisteredTeamsResponse>,
) => {
  return useQuery<GetRegisteredTeamsResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['registered-teams'](payload.id),
    queryFn: () => $api.tournaments.getRegisteredTeams({ id: payload.id }),
    ...config,
  })
}

export const useTournamentRounds = (
  payload: GetRoundsArgs,
  config?: QueryConfig<GetRoundsResponse>,
) => {
  return useQuery<GetRoundsResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys.rounds(payload.id),
    queryFn: () => $api.tournaments.getRounds({ id: payload.id }),
    ...config,
  })
}

export const useActiveTeamTournament = (
  payload: GetActiveTeamTournamentArgs,
  config?: QueryConfig<GetActiveTeamTournamentResponse>,
) => {
  return useQuery<GetActiveTeamTournamentResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['active-team-tournament'](payload.id),
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
      queryClient.invalidateQueries({ queryKey: touranmentsKeys.allTouranments() })
    },
    ...config,
  })
}

export const useTournamentInfo = (
  payload: GetTournamentInfoArgs,
  config?: QueryConfig<GetTournamentInfoResponse>,
) => {
  return useQuery<GetTournamentInfoResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys.touranment(payload.id),
    queryFn: () => $api.tournaments.getTournamentInfo({ id: payload.id }),
    ...config,
  })
}

export const useEligibleTeams = (
  payload: GetEligibleTeamsArgs,
  config?: QueryConfig<GetEligibleTeamsResponse>,
) => {
  return useQuery<GetEligibleTeamsResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['eligible-teams'](),
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
        queryClient.invalidateQueries({ queryKey: touranmentsKeys.rounds(vars.id) })
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
      queryClient.invalidateQueries({ queryKey: touranmentsKeys.rounds(payload.id) })
    },
    ...config,
  })
}

export const useCurrentRound = (
  payload: GetCurrentRoundArgs,
  config?: QueryConfig<GetCurrentRoundResponse>,
) => {
  return useQuery<GetCurrentRoundResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['current-round'](payload.id),
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
      queryClient.invalidateQueries({
        queryKey: [
          touranmentsKeys['eligible-teams'](),
          touranmentsKeys['registered-teams'](vars.id),
        ],
      })
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
        queryClient.invalidateQueries({ queryKey: touranmentsKeys.events(vars.body.tournament) })
      },
    },
  )
}

export const useTournamentEvents = (
  payload: GetEventsArgs,
  config?: QueryConfig<GetEventsResponse>,
) => {
  return useQuery<GetEventsResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys.events(payload.tournamentId),
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
