import { $api } from '@/api/services'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { teamKeys } from '../keys'
import type { AxiosError } from 'axios'
import { computed, toValue } from 'vue'
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
import type { MaybeRefArgs, MutationConfig, QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'

export const useTeams = (config?: QueryConfig<GetTeamsResponse>) => {
  return useQuery<GetTeamsResponse, AxiosError<ApiError>>({
    queryKey: teamKeys.lists(),
    queryFn: $api.teams.getTeams,
    ...config,
  })
}

export const useTeamInfo = (
  payload: MaybeRefArgs<GetTeamInfoArgs>,
  config?: QueryConfig<GetTeamInfoResponse>,
) => {
  return useQuery<GetTeamInfoResponse, AxiosError<ApiError>>({
    queryKey: computed(() => teamKeys.info(toValue(payload.id))),
    queryFn: () => $api.teams.getTeamInfo({ id: payload.id }),
    ...config,
  })
}

export const useTeamJoinRequests = (
  payload: MaybeRefArgs<GetTeamJoinRequestsArgs>,
  config?: QueryConfig<GetTeamJoinRequestsResponse>,
) => {
  return useQuery<GetTeamJoinRequestsResponse, AxiosError<ApiError>>({
    queryKey: computed(() => teamKeys.joinRequests(toValue(payload.teamId))),
    queryFn: () => $api.teams.getTeamJoinRequests({ teamId: payload.teamId }),
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
  payload: MaybeRefArgs<GetTeamInvitationsArgs>,
  config?: QueryConfig<GetTeamInvitationsResponse>,
) => {
  return useQuery<GetTeamInvitationsResponse, AxiosError<ApiError>>({
    queryKey: computed(() => teamKeys.invitations(toValue(payload.teamId))),
    queryFn: () => $api.teams.getTeamInvitations({ teamId: payload.teamId }),
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
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.joinRequests(teamId) })
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
    onSuccess: (_, args) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.invitations(args.teamId) })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.info(teamId) })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.info(teamId) })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.info(teamId) })
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
      queryClient.invalidateQueries({ queryKey: teamKeys.info(teamId) })
      queryClient.invalidateQueries({ queryKey: teamKeys.invitations(teamId) })
    },
    ...config,
  })
}
