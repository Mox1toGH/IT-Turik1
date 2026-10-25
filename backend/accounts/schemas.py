from datetime import date, datetime
from typing import Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from ninja import Schema

from backend.schemas import StaffRole, UserRole
from pydantic import Field, field_validator

# --------------------------------------------------------------------------
# Common
# --------------------------------------------------------------------------

class PasswordResetRequestedResponse(Schema):
    message: str

class PasswordResetLinkValidationResponse(Schema):
    message: str

class PasswordResetCompletedResponse(Schema):
    message: str

class PasswordChangedResponse(Schema):
    message: str

class ActivationResponse(Schema):
    status: str
    message: str

class AvatarSchema(Schema):
    """Response shape for an avatar URL, mapped by the endpoint."""
    avatar: str = ''

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
        value = value.strip()
        
        try:
            validate_email(value)
        except DjangoValidationError:
            raise ValueError('Enter a valid email address.')
        return value

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
    authenticated: bool
    onboarding_required: bool

class TokenRefreshResponse(Schema):
    authenticated: bool

class GoogleAuthRequest(Schema):
    id_token: str

class PasswordResetRequest(Schema):
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
    created_at: datetime
    needs_onboarding: bool
    teams: list[UserTeamResponse]
    active_tournament: UserActiveTournamentResponse | None

class GetUserProfileResponse(Schema):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    phone: str
    city: str
    is_staff: bool
    created_at: datetime
    needs_onboarding: bool
    teams: list[UserTeamResponse]
    active_tournament: UserActiveTournamentResponse | None
    avatar: str = ''

class UpdateUserProfileResponse(Schema):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    phone: str
    city: str
    is_staff: bool
    created_at: datetime
    needs_onboarding: bool
    teams: list[UserTeamResponse]
    active_tournament: UserActiveTournamentResponse | None
    avatar: str = ''

class GetUserResponse(Schema):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    phone: str
    city: str
    is_staff: bool
    created_at: datetime
    needs_onboarding: bool
    teams: list[UserTeamResponse]
    active_tournament: UserActiveTournamentResponse | None
    avatar: str = ''

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
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    password: str | None = None

class UserAvatarResponse(AvatarSchema):
    pass

class UserListFilters(Schema):
    search: Optional[str] = Field(None, description='Filter by username, email, or full name')

class GoogleAuthResponse(Schema):
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
