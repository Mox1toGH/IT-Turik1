from datetime import datetime
from typing import Optional

from ninja import Schema

from backend.media import absolute_media_url
from backend.schemas import UserRole
from pydantic import PositiveInt

from accounts.schemas import AvatarSchema

from .models import TeamInvitation, TeamJoinRequest
from .services import get_active_tournament_registration


def _context_user(context):
    request = (context or {}).get('request')
    user = getattr(request, 'auth', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return None
    return user


def _absolute_url(file_field, context) -> Optional[str]:
    return absolute_media_url(file_field, context)


# --------------------------------------------------------------------------
# Common
# --------------------------------------------------------------------------

class DetailResponse(Schema):
    detail: str


# --------------------------------------------------------------------------
# Nested
# --------------------------------------------------------------------------

class TeamMemberResponse(AvatarSchema):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    avatar_frame_url: str | None

    @staticmethod
    def resolve_avatar_frame_url(obj, context):
        from inventory.models import UserInventory

        equipped_item = (
            UserInventory.objects.select_related('product', 'product__avatar_frame')
            .filter(user=obj, is_equipped=True)
            .first()
        )
        if equipped_item is None:
            return None

        url = equipped_item.product.effective_digital_asset_url
        if not url:
            return None

        return absolute_media_url(url, context)


class TeamSummaryResponse(Schema):
    id: int
    name: str
    is_public: bool


# --------------------------------------------------------------------------
# Team
# --------------------------------------------------------------------------

class TeamResponse(Schema):
    id: int
    name: str
    email: str
    captain_id: int
    is_public: bool
    organization: str = ''
    contact_telegram: str = ''
    contact_discord: str = ''
    banner: str = ''
    members: list[TeamMemberResponse]
    is_member: bool
    can_request_to_join: bool
    is_in_active_tournament: bool

    @staticmethod
    def resolve_banner(obj, context):
        return _absolute_url(obj.banner, context)

    @staticmethod
    def resolve_members(obj):
        return list(obj.members.all())

    @staticmethod
    def resolve_is_member(obj, context):
        user = _context_user(context)
        if not user:
            return False
        return any(member.id == user.id for member in obj.members.all())

    @staticmethod
    def resolve_can_request_to_join(obj, context):
        user = _context_user(context)
        if not user or not obj.is_public:
            return False
        if obj.captain_id == user.id or any(member.id == user.id for member in obj.members.all()):
            return False

        for invitation in obj.invitations.all():
            if invitation.user_id == user.id and invitation.status == TeamInvitation.STATUS_INVITED:
                return False

        for join_request in obj.join_requests.all():
            if join_request.user_id == user.id and join_request.status == TeamJoinRequest.STATUS_PENDING:
                return False
        return True

    @staticmethod
    def resolve_is_in_active_tournament(obj):
        return get_active_tournament_registration(obj) is not None


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

    @staticmethod
    def resolve_banner(obj, context):
        return _absolute_url(obj.banner, context)


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
