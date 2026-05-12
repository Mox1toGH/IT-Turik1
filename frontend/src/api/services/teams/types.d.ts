import type {
  Invitation,
  InvitationId,
  JoinRequest,
  JoinRequestId,
  Team,
  TeamId,
  UserId,
} from '@/api/dbTypes'

// GetTeamInfo
export interface GetTeamInfoArgs {
  id: TeamId
}
export type GetTeamInfoResponse = Pick<
  Team,
  | 'id'
  | 'name'
  | 'email'
  | 'is_public'
  | 'organization'
  | 'contact_discord'
  | 'contact_telegram'
  | 'members'
> & {
  captain_id: UserId
  is_member: boolean
  is_captain: boolean
  can_request_to_join: boolean
  is_in_active_tournament: true
}

// CreateTeam
export interface CreateTeamBody {
  name: string
  email: string
  organization: string
  contact_telegram: string
  contact_discord: string
  is_public: boolean
  member_ids: UserId[]
}
export interface CreateTeamArgs {
  body: CreateTeamBody
}

// CreateTeam
export type CreateTeamResponse = GetTeamInfoResponse

// GetTeams
export type GetTeamsResponse = (Pick<
  Team,
  | 'id'
  | 'name'
  | 'email'
  | 'is_public'
  | 'organization'
  | 'contact_discord'
  | 'contact_telegram'
  | 'members'
> & {
  captain_id: UserId
  is_member: boolean
  can_request_to_join: boolean
  is_in_active_tournament: boolean
})[]

// GetTeamJoinRequests
export type GetTeamJoinRequestsArgs = {
  teamId: TeamId
}
export type GetTeamJoinRequestsResponse = JoinRequest[]

// GetInvitations
export type GetInvitationsResponse = Exclude<Invitation, 'user'>[]

// GetTeamInvitations
export type GetTeamInvitationsArgs = {
  teamId: TeamId
}
export type GetTeamInvitationsResponse = Invitation[]

// RespondToInvitation
export type RespondToInvitationAction = 'accept' | 'decline'
export interface RespondToInvitationArgs {
  id: InvitationId
  action: RespondToInvitationAction
}

// ResendInvitation
export interface ResendInvitationBody {
  user_id: UserId
}
export interface ResendInvitationArgs {
  teamId: TeamId
  body: ResendInvitationBody
}
export type ResendInvitationResponse = GetTeamInfoResponse

// SEND / LEAVE / JOIN Request
export interface SendJoinRequestArgs {
  id: TeamId
}
export interface DeleteTeamArgs {
  id: TeamId
}
export interface LeaveTeamArgs {
  id: TeamId
}

// ManageJoinRequest
export type ManageJoinRequestAction = 'accept' | 'decline'
export interface ManageJoinRequestArgs {
  id: JoinRequestId
  teamId: TeamId
  action: ManageJoinRequestAction
}
export type ManageJoinRequestResponse = GetTeamInfoResponse

// ChangeTeamVisibility
export interface ChangeTeamVisibilityBody {
  is_public: boolean
}
export interface ChangeTeamVisibilityArgs {
  teamId: TeamId
  body: ChangeTeamVisibilityBody
}
export type ChangeTeamVisibilityResponse = GetTeamInfoResponse

// UpdateTeamInfo
export interface UpdateTeamInfoBody {
  name: string
  email: string
  organization: string
  contact_telegram: string
  contact_discord: string
}
export interface UpdateTeamInfoArgs {
  teamId: TeamId
  body: UpdateTeamInfoBody
}

// RemoveMember
export interface RemoveMemberArgs {
  teamId: TeamId
  memberId: UserId
}

// AddMember
export interface AddMemberBody {
  user_id: UserId
}
export interface AddMemberArgs {
  teamId: TeamId
  body: AddMemberBody
}
