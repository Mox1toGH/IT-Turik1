import { $api } from '@/api/services'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { teamKeys } from '../keys'
import type { AxiosError } from 'axios'
import type {
  AddMemberArgs,
  ChangeTeamVisibilityArgs,
  ChangeTeamVisibilityResponse,
  CreateTeamArgs,
  CreateTeamResponse,
  DeleteTeamArgs,
  GetInvitationsResponse,
  GetTeamInfoArgs,
  GetTeamInfoResponse,
  GetTeamInvitationsArgs,
  GetTeamInvitationsResponse,
  GetTeamJoinRequestsArgs,
  GetTeamJoinRequestsResponse,
  GetTeamsResponse,
  LeaveTeamArgs,
  ManageJoinRequestArgs,
  RemoveMemberArgs,
  ResendInvitationArgs,
  RespondToInvitationArgs,
  SendJoinRequestArgs,
  UpdateTeamInfoArgs,
} from '@/api/services/teams/types'
import type { MutationConfig, QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'

export const useTeams = (config?: QueryConfig<GetTeamsResponse>) => {
  return useQuery<GetTeamsResponse, AxiosError<ApiError>>({
    queryKey: teamKeys.allTeams(),
    queryFn: $api.teams.getTeams,
    ...config,
  })
}

export const useTeamInfo = (
  payload: GetTeamInfoArgs,
  config?: QueryConfig<GetTeamInfoResponse>,
) => {
  return useQuery<GetTeamInfoResponse, AxiosError<ApiError>>({
    queryKey: teamKeys.team(payload.id),
    queryFn: () => $api.teams.getTeamInfo({ id: payload.id }),
    ...config,
  })
}

export const useTeamJoinRequests = (
  payload: GetTeamJoinRequestsArgs,
  config?: QueryConfig<GetTeamJoinRequestsResponse>,
) => {
  return useQuery<GetTeamJoinRequestsResponse, AxiosError<ApiError>>({
    queryKey: teamKeys['join-requests'](payload.teamId),
    queryFn: () => $api.teams.getTeamJoinRequests(payload),
    ...config,
  })
}

export const useInvitations = (config?: QueryConfig<GetInvitationsResponse>) => {
  return useQuery<GetInvitationsResponse, AxiosError<ApiError>>({
    queryKey: ['invitations'],
    queryFn: $api.teams.getInvitations,
    ...config,
  })
}

export const useTeamInvitations = (
  payload: GetTeamInvitationsArgs,
  config?: QueryConfig<GetTeamInvitationsResponse>,
) => {
  return useQuery<GetTeamInvitationsResponse, AxiosError<ApiError>>({
    queryKey: teamKeys['team-invitations'](payload.teamId),
    queryFn: () => $api.teams.getTeamInvitations(payload),
    ...config,
  })
}

export const useCreateTeam = (
  config?: MutationConfig<
    CreateTeamResponse,
    AxiosError<ApiError<keyof CreateTeamArgs['body']>>,
    CreateTeamArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    CreateTeamResponse,
    AxiosError<ApiError<keyof CreateTeamArgs['body']>>,
    CreateTeamArgs
  >({
    mutationFn: $api.teams.createTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
    ...config,
  })
}

export const useRespondToInvitation = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, RespondToInvitationArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, RespondToInvitationArgs>({
    mutationFn: $api.teams.respondToInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invitations'] })
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
    ...config,
  })
}

export const useSendJoinRequest = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, SendJoinRequestArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, SendJoinRequestArgs>({
    mutationFn: $api.teams.sendJoinRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
    ...config,
  })
}

export const useDeleteTeam = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, DeleteTeamArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, DeleteTeamArgs>({
    mutationFn: $api.teams.deleteTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
    ...config,
  })
}

export const useLeaveTeam = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, LeaveTeamArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, LeaveTeamArgs>({
    mutationFn: $api.teams.leave,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
    ...config,
  })
}

export const useManageJoinRequest = (
  config?: MutationConfig<GetTeamInfoResponse, AxiosError<ApiError>, ManageJoinRequestArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<GetTeamInfoResponse, AxiosError<ApiError>, ManageJoinRequestArgs>({
    mutationFn: $api.teams.manageJoinRequest,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys['join-requests'](teamId) })
    },
    ...config,
  })
}

export const useResendInvitation = (
  config?: MutationConfig<GetTeamInfoResponse, AxiosError<ApiError>, ResendInvitationArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<GetTeamInfoResponse, AxiosError<ApiError>, ResendInvitationArgs>({
    mutationFn: $api.teams.resendInvitation,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
    ...config,
  })
}

export const useChangeTeamVisibility = (
  config?: MutationConfig<
    ChangeTeamVisibilityResponse,
    AxiosError<ApiError>,
    ChangeTeamVisibilityArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<ChangeTeamVisibilityResponse, AxiosError<ApiError>, ChangeTeamVisibilityArgs>({
    mutationFn: $api.teams.changeTeamVisibility,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
    ...config,
  })
}

export const useUpdateTeamInfo = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, UpdateTeamInfoArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, UpdateTeamInfoArgs>({
    mutationFn: $api.teams.updateInfo,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
    ...config,
  })
}

export const useRemoveMember = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, RemoveMemberArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, RemoveMemberArgs>({
    mutationFn: $api.teams.removeMember,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
    ...config,
  })
}

export const useAddMember = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, AddMemberArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, AddMemberArgs>({
    mutationFn: $api.teams.addMember,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
    ...config,
  })
}
