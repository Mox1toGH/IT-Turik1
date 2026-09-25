from datetime import date, datetime
from typing import Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from ninja import Schema

from backend.media import absolute_media_url
from backend.schemas import StaffRole, UserRole
from pydantic import Field, field_validator

# --------------------------------------------------------------------------
# Common
# --------------------------------------------------------------------------

class MessageResponse(Schema):
    message: str


class ActivationResponse(Schema):
    status: str
    message: str


class AvatarSchema(Schema):
    """Base schema: `avatar` is returned as an absolute URL (needs context={'request': request})."""

    avatar: str = ''

    @staticmethod
    def resolve_avatar(obj, context):
        return absolute_media_url(getattr(obj, 'avatar', None), context) or ''


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------

class RegisterRequest(Schema):
    username: str = Field(..., min_length=1, max_length=150)
    email: str
    password: str
    role: UserRole = UserRole.TEAM
    full_name: str = ''
    phone: str = ''
    city: str = ''
    activation_code: Optional[str] = None

    @field_validator('email')
    @classmethod
    def _valid_email(cls, value: str) -> str:
        try:
            validate_email(value)
        except DjangoValidationError:
            raise ValueError('Enter a valid email address.')
        return value.strip()


class RegisterResponse(Schema):
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None


class LoginRequest(Schema):
    username: str
    password: str


class LoginResponse(Schema):
    access: str
    refresh: str


class TokenRefreshRequest(Schema):
    refresh: str


class TokenRefreshResponse(Schema):
    access: str


class GoogleAuthRequest(Schema):
    id_token: str


class PasswordResetRequestRequest(Schema):
    email: str


class PasswordResetConfirmRequest(Schema):
    new_password: str
    confirm_password: str


class ChangePasswordRequest(Schema):
    current_password: str
    new_password: str
    confirm_password: str


# --------------------------------------------------------------------------
# Users
# --------------------------------------------------------------------------

class UserTeamResponse(Schema):
    id: int
    name: str
    contact_telegram: str
    contact_discord: str


class UserActiveTournamentTeamResponse(Schema):
    id: int
    name: str


class UserActiveTournamentRoundResponse(Schema):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: str


class UserActiveTournamentResponse(Schema):
    id: int
    name: str
    status: str
    start_date: datetime
    end_date: datetime
    team: UserActiveTournamentTeamResponse
    team_registration_status: str
    current_round: UserActiveTournamentRoundResponse | None


class UserResponse(AvatarSchema):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    phone: str
    city: str
    is_staff: bool
    avatar_frame_url: str | None
    created_at: datetime
    needs_onboarding: bool
    teams: list[UserTeamResponse]
    active_tournament: UserActiveTournamentResponse | None

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
        return absolute_media_url(equipped_item.product.effective_digital_asset_url, context)

    @staticmethod
    def resolve_created_at(obj):
        return obj.date_joined

    @staticmethod
    def resolve_teams(obj):
        return [
            {
                'id': team.id,
                'name': team.name,
                'contact_telegram': team.contact_telegram or '',
                'contact_discord': team.contact_discord or '',
            }
            for team in obj.teams.all()
        ]

    @staticmethod
    def resolve_active_tournament(obj):
        return None


class UserShortResponse(Schema):
    id: int
    username: str


class TeamUserListResponse(AvatarSchema):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    city: Optional[str] = None


class UserUpdateRequest(Schema):
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None

    @field_validator('email')
    @classmethod
    def _valid_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        try:
            validate_email(value)
        except DjangoValidationError:
            raise ValueError('Enter a valid email address.')
        return value.strip()


class UserAvatarResponse(AvatarSchema):
    pass


class UserListFilters(Schema):
    search: Optional[str] = Field(None, description='Filter by username, email, or full name')


class GoogleAuthResponse(Schema):
    access: str
    refresh: str
    user: UserResponse
    onboarding_required: bool


class GoogleCalendarStatusResponse(Schema):
    connected: bool


class GoogleCalendarConnectResponse(Schema):
    auth_url: str


class GoogleCalendarCallbackRequest(Schema):
    code: str


# --------------------------------------------------------------------------
# Tournament history
# --------------------------------------------------------------------------

class TeamRefResponse(Schema):
    id: int
    name: str


class UserTournamentHistoryItemResponse(Schema):
    tournament_id: int
    tournament_name: str
    tournament_status: str
    start_date: date
    end_date: date
    team: TeamRefResponse
    team_registration_status: str
    final_rank: Optional[int] = None
    final_score: Optional[float] = None

    @staticmethod
    def resolve_tournament_name(obj):
        return obj.tournament.name

    @staticmethod
    def resolve_tournament_status(obj):
        return obj.tournament.status

    @staticmethod
    def resolve_start_date(obj):
        return obj.tournament.start_date

    @staticmethod
    def resolve_end_date(obj):
        return obj.tournament.end_date

    @staticmethod
    def resolve_team_registration_status(obj):
        if obj.is_disqualified:
            return 'disqualified'
        if obj.is_active:
            return 'active'
        return 'inactive'

    # context['standings'] = {(tournament_id, team_id): {'rank': .., 'total_score': ..}}
    @staticmethod
    def resolve_final_rank(obj, context):
        standing = (context or {}).get('standings', {}).get((obj.tournament_id, obj.team_id))
        return standing['rank'] if standing else None

    @staticmethod
    def resolve_final_score(obj, context):
        standing = (context or {}).get('standings', {}).get((obj.tournament_id, obj.team_id))
        return standing['total_score'] if standing else None


# --------------------------------------------------------------------------
# Role activation codes
# --------------------------------------------------------------------------

class RoleActivationCodeResponse(Schema):
    id: int
    code: str
    role: str
    is_used: bool
    created_at: datetime
    created_by: Optional[UserShortResponse] = None
    used_by: Optional[UserShortResponse] = None
    created_by_username: str | None
    used_by_username: str | None
    used_at: datetime | None

    @staticmethod
    def resolve_created_by_username(obj):
        return obj.created_by.username if obj.created_by else None

    @staticmethod
    def resolve_used_by_username(obj):
        return obj.used_by.username if obj.used_by else None


class RoleActivationCodeListFilters(Schema):
    role: Optional[str] = Field(None, description='Filter by role: jury, organizer, admin')


class RoleActivationCodeGenerateRequest(Schema):
    role: StaffRole
    count: int = Field(1, ge=1, le=100)


class RoleActivationCodeListResponse(Schema):
    codes: list[RoleActivationCodeResponse]
    active_counts: dict[str, int]


class RoleActivationCodeGenerateResponse(Schema):
    created: list[RoleActivationCodeResponse]
    active_counts: dict[str, int]
