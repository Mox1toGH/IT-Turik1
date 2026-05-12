import { apiClient } from '@/api/client'
import type { TeamId } from '@/api/dbTypes'
import { toValue } from 'vue'
import type {
  AddMemberArgs,
  ChangeTeamVisibilityArgs,
  CreateTeamArgs,
  CreateTeamResponse,
  DeleteTeamArgs,
  GetInvitationsResponse,
  GetTeamInfoArgs,
  GetTeamInfoResponse,
  GetTeamInvitationsArgs,
  GetTeamInvitationsResponse,
  GetTeamJoinRequestsResponse,
  GetTeamJoinRequestsArgs,
  GetTeamsResponse,
  LeaveTeamArgs,
  ManageJoinRequestArgs,
  ManageJoinRequestResponse,
  RemoveMemberArgs,
  ResendInvitationArgs,
  RespondToInvitationArgs,
  SendJoinRequestArgs,
  UpdateTeamInfoBody,
} from './types'
import type { MaybeRefArgs } from '@/api/queries/types'

const prefix = '/api/teams'

export const teamsService = {
  async createTeam(args: MaybeRefArgs<CreateTeamArgs>) {
    const { data } = await apiClient.post<CreateTeamResponse>(`${prefix}/`, toValue(args.body))
    return data
  },

  async getTeamInfo(args: MaybeRefArgs<GetTeamInfoArgs>) {
    const { data } = await apiClient.get<GetTeamInfoResponse>(`${prefix}/${toValue(args.id)}`)
    return data
  },

  async getTeams() {
    const { data } = await apiClient.get<GetTeamsResponse>(`${prefix}/`)
    return data
  },

  async getTeamJoinRequests(args: MaybeRefArgs<GetTeamJoinRequestsArgs>) {
    const { data } = await apiClient.get<GetTeamJoinRequestsResponse>(
      `${prefix}/${toValue(args.teamId)}/join-requests-list`,
    )
    return data
  },

  async getInvitations() {
    const { data } = await apiClient.get<GetInvitationsResponse>(`${prefix}/invitations/`)
    return data
  },

  async getTeamInvitations(args: MaybeRefArgs<GetTeamInvitationsArgs>) {
    const { data } = await apiClient.get<GetTeamInvitationsResponse>(
      `${prefix}/${toValue(args.teamId)}/invitations`,
    )
    return data
  },

  async respondToInvitation(args: MaybeRefArgs<RespondToInvitationArgs>) {
    const { data } = await apiClient.post(
      `${prefix}/invitations/${toValue(args.id)}/${toValue(args.action)}/`,
    )
    return data
  },

  async sendJoinRequest(args: MaybeRefArgs<SendJoinRequestArgs>) {
    const { data } = await apiClient.post(`${prefix}/${toValue(args.id)}/join-requests/`)
    return data
  },

  async deleteTeam(args: MaybeRefArgs<DeleteTeamArgs>) {
    const { data } = await apiClient.delete(`${prefix}/${toValue(args.id)}/`)
    return data
  },

  async leave(args: MaybeRefArgs<LeaveTeamArgs>) {
    const { data } = await apiClient.post(`${prefix}/${toValue(args.id)}/leave/`)
    return data
  },

  async manageJoinRequest(args: MaybeRefArgs<ManageJoinRequestArgs>) {
    const { data } = await apiClient.post<ManageJoinRequestResponse>(
      `${prefix}/${toValue(args.teamId)}/join-requests/${toValue(args.id)}/${toValue(args.action)}/`,
    )
    return data
  },

  async resendInvitation(args: MaybeRefArgs<ResendInvitationArgs>) {
    const { data } = await apiClient.post<GetTeamInfoResponse>(
      `${prefix}/${toValue(args.teamId)}/members/`,
      toValue(args.body),
    )
    return data
  },

  async changeTeamVisibility(args: MaybeRefArgs<ChangeTeamVisibilityArgs>) {
    const { data } = await apiClient.patch<GetTeamInfoResponse>(
      `${prefix}/${toValue(args.teamId)}/`,
      toValue(args.body),
    )
    return data
  },

  async updateInfo(args: MaybeRefArgs<{ teamId: TeamId; body: UpdateTeamInfoBody }>) {
    const { data } = await apiClient.patch(`${prefix}/${toValue(args.teamId)}/`, toValue(args.body))
    return data
  },

  async removeMember(args: MaybeRefArgs<RemoveMemberArgs>) {
    const { data } = await apiClient.delete(
      `${prefix}/${toValue(args.teamId)}/members/${toValue(args.memberId)}/`,
    )
    return data
  },

  async addMember(args: MaybeRefArgs<AddMemberArgs>) {
    const { data } = await apiClient.post(
      `${prefix}/${toValue(args.teamId)}/members/`,
      toValue(args.body),
    )
    return data
  },
}
