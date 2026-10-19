from datetime import datetime
from typing import Optional

from ninja import Schema

from backend.schemas import UserRole
from pydantic import PositiveInt

from accounts.schemas import AvatarSchema

# --------------------------------------------------------------------------
# Nested
# --------------------------------------------------------------------------

class TeamMemberResponse(AvatarSchema):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole

class TeamSummaryResponse(Schema):
    id: int
    name: str
    is_public: bool

# --------------------------------------------------------------------------
# Team
# --------------------------------------------------------------------------

# Success contracts are intentionally independent per endpoint (API-002).
class ListTeamsItemResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class CreateTeamResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class GetTeamResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class UpdateTeamResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class DeleteTeamBannerResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class InviteMemberResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class AcceptTeamInvitationResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class DeclineTeamInvitationResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class AcceptTeamJoinRequestResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class DeclineTeamJoinRequestResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str | None = None
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

class LeaveTeamResponse(Schema):
    detail: str

class CreateTeamJoinRequestResponse(Schema):
    detail: str

class TeamCreateRequest(Schema):
    name: str
    email: str
    is_public: bool = True
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    member_ids: list[PositiveInt] = []

class TeamUpdateRequest(Schema):
    name: Optional[str] = None
    email: Optional[str] = None
    is_public: Optional[bool] = None
    organization: Optional[str] = None
    contact_telegram: Optional[str] = None
    contact_discord: Optional[str] = None
    member_ids: Optional[list[PositiveInt]] = None

class TeamBannerResponse(Schema):
    banner: Optional[str] = None

# --------------------------------------------------------------------------
# Invitations / join requests
# --------------------------------------------------------------------------

class InviteMemberRequest(Schema):
    user_id: Optional[int] = None

class TeamInvitationResponse(Schema):
    id: int
    user: TeamMemberResponse
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None
    invited_by_id: Optional[int] = None

class TeamInvitationInboxResponse(Schema):
    id: int
    team: TeamSummaryResponse
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None
    invited_by: Optional[TeamMemberResponse] = None

class TeamJoinRequestResponse(Schema):
    id: int
    user: TeamMemberResponse
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by_id: Optional[int] = None
