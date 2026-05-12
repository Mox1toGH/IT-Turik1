import { apiClient } from '@/api/client'
import type { TeamId } from '@/api/dbTypes'
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

const prefix = '/api/teams'

export const teamsService = {
  async createTeam(args: CreateTeamArgs) {
    const { data } = await apiClient.post<CreateTeamResponse>(`${prefix}/`, args.body)
    return data
  },

  async getTeamInfo(args: GetTeamInfoArgs) {
    const { data } = await apiClient.get<GetTeamInfoResponse>(`${prefix}/${args.id}`)
    return data
  },

  async getTeams() {
    const { data } = await apiClient.get<GetTeamsResponse>(`${prefix}/`)
    return data
  },

  async getTeamJoinRequests(args: GetTeamJoinRequestsArgs) {
    const { data } = await apiClient.get<GetTeamJoinRequestsResponse>(
      `${prefix}/${args.teamId}/join-requests-list`,
    )
    return data
  },

  async getInvitations() {
    const { data } = await apiClient.get<GetInvitationsResponse>(`${prefix}/invitations/`)
    return data
  },

  async getTeamInvitations(args: GetTeamInvitationsArgs) {
    const { data } = await apiClient.get<GetTeamInvitationsResponse>(
      `${prefix}/${args.teamId}/invitations`,
    )
    return data
  },

  async respondToInvitation(args: RespondToInvitationArgs) {
    const { data } = await apiClient.post(`${prefix}/invitations/${args.id}/${args.action}/`)
    return data
  },

  async sendJoinRequest(args: SendJoinRequestArgs) {
    const { data } = await apiClient.post(`${prefix}/${args.id}/join-requests/`)
    return data
  },

  async deleteTeam(args: DeleteTeamArgs) {
    const { data } = await apiClient.delete(`${prefix}/${args.id}/`)
    return data
  },

  async leave(args: LeaveTeamArgs) {
    const { data } = await apiClient.post(`${prefix}/${args.id}/leave/`)
    return data
  },

  async manageJoinRequest(args: ManageJoinRequestArgs) {
    const { data } = await apiClient.post<ManageJoinRequestResponse>(
      `${prefix}/${args.teamId}/join-requests/${args.id}/${args.action}/`,
    )
    return data
  },

  async resendInvitation(args: ResendInvitationArgs) {
    const { data } = await apiClient.post<GetTeamInfoResponse>(
      `${prefix}/${args.teamId}/members/`,
      args.body,
    )
    return data
  },

  async changeTeamVisibility(args: ChangeTeamVisibilityArgs) {
    const { data } = await apiClient.patch<GetTeamInfoResponse>(
      `${prefix}/${args.teamId}/`,
      args.body,
    )
    return data
  },

  async updateInfo(args: { teamId: TeamId; body: UpdateTeamInfoBody }) {
    const { data } = await apiClient.patch(`${prefix}/${args.teamId}/`, args.body)
    return data
  },

  async removeMember(args: RemoveMemberArgs) {
    const { data } = await apiClient.delete(`${prefix}/${args.teamId}/members/${args.memberId}/`)
    return data
  },

  async addMember(args: AddMemberArgs) {
    const { data } = await apiClient.post(`${prefix}/${args.teamId}/members/`, args.body)
    return data
  },
}
