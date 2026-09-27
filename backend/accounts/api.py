import secrets
from urllib.parse import urlencode

import requests as http_requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from ninja import File, Query, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from backend.auth import JWTAuth
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from evaluation.models import LeaderboardEntry
from teams.models import Team, TeamMember
from tournaments.models import Tournament, TournamentTeamRegistration

from .models import RoleActivationCode, User
from .google_calendar import (
    GOOGLE_AUTH_URI,
    GOOGLE_TOKEN_URI,
    SCOPES,
    _generate_code_challenge,
    _generate_code_verifier,
    _sync_all_calendar_items,
)

from backend.schemas import ErrorResponse
from .schemas import (
    ActivationResponse,
    ChangePasswordRequest,
    GoogleAuthRequest,
    GoogleAuthResponse,
    GoogleCalendarCallbackRequest,
    GoogleCalendarConnectResponse,
    GoogleCalendarStatusResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    RegisterResponse,
    RoleActivationCodeGenerateRequest,
    RoleActivationCodeGenerateResponse,
    RoleActivationCodeListFilters,
    RoleActivationCodeListResponse,
    RoleActivationCodeResponse,
    TeamUserListResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserAvatarResponse,
    UserListFilters,
    UserResponse,
    UserTournamentHistoryItemResponse,
    UserUpdateRequest,
)

router = Router(tags=['accounts'])

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _get_user_by_uid(uidb64: str):
    try:
        return User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def _check_password_or_400(password: str, user=None) -> None:
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise HttpError(400, ' '.join(exc.messages))

def send_html_email(
    subject: str,
    template_name: str,
    context: dict,
    recipient: str,
) -> None:
    html_message = render_to_string(template_name, context)

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.content_subtype = "html"
    email.send()

def _send_link_email(
    user,
    path: str,
    template_name: str,
    subject: str,
    intro: str,
) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    base = getattr(settings, "FRONTEND_URL", "").rstrip("/")
    link = f"{base}/{path}/{uid}/{token}/"

    send_html_email(
        subject=subject,
        template_name=template_name,
        context={
            "username": user.username,
            "title": subject,
            "secondary_message": intro,
            "action_url": link,
        },
        recipient=user.email,
    )


def _is_platform_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))


def _require_admin(request) -> None:
    if not _is_platform_admin(request.user):
        raise HttpError(403, 'Admin access required.')


def _active_counts() -> dict:
    return {
        role: RoleActivationCode.objects.filter(role=role, is_used=False).count()
        for role in ('jury', 'organizer', 'admin')
    }


# --------------------------------------------------------------------------
# Registration / activation / auth
# --------------------------------------------------------------------------

@router.post(
    '/register',
    auth=None,
    operation_id='registerUser',
    url_name="register",
    response={201: RegisterResponse, 400: ErrorResponse},
)
def register_user(request, payload: RegisterRequest):
    if User.objects.filter(username__iexact=payload.username).exists():
        raise HttpError(400, 'A user with that username already exists.')
    if User.objects.filter(email__iexact=payload.email).exists():
        raise HttpError(400, 'A user with that email already exists.')

    user = User(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        full_name=payload.full_name,
        phone=payload.phone,
        city=payload.city,
        is_active=False,
    )
    _check_password_or_400(payload.password, user)

    with transaction.atomic():
        code = None
        if payload.role != 'team':
            code = (
                RoleActivationCode.objects.select_for_update()
                .filter(code=payload.activation_code, role=payload.role, is_used=False)
                .first()
            )
            if code is None:
                raise HttpError(400, 'Invalid or already used activation code.')

        user.set_password(payload.password)
        
        if user.role == 'admin':
            user.is_staff = True
            user.is_superuser = True

        user.save()

        if code is not None:
            code.is_used = True
            code.used_by = user
            code.save(update_fields=['is_used', 'used_by'])
        
    _send_link_email(
        user,
        "activate",
        "accounts/account_activation_email.html",
        "Activate your account",
        "Follow the link to activate your account:",
    )
    return 201, RegisterResponse.model_validate(user, from_attributes=True)


@router.patch(
    '/activate/{uidb64}/{token}',
    auth=None,
    operation_id='activateAccount',
    url_name="activate",
    response={200: ActivationResponse, 400: ErrorResponse},
)
def activate_account(request, uidb64: str, token: str):
    user = _get_user_by_uid(uidb64)
    if user is None or not default_token_generator.check_token(user, token):
        raise HttpError(400, 'Activation link is invalid or expired.')

    user.is_active = True
    user.save(update_fields=['is_active'])
    return ActivationResponse(status='success', message='Account activated!')


@router.post(
    '/login',
    auth=None,
    operation_id='login',
    url_name="token_obtain_pair",
    response={200: LoginResponse, 401: ErrorResponse},
)
def login(request, payload: LoginRequest):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        raise HttpError(401, 'No active account found with the given credentials.')
    refresh = RefreshToken.for_user(user)
    return LoginResponse(access=str(refresh.access_token), refresh=str(refresh))


@router.post(
    '/token/refresh',
    auth=None,
    operation_id='refreshToken',
    url_name="token_refresh",
    response={200: TokenRefreshResponse, 401: ErrorResponse},
)
def refresh_token(request, payload: TokenRefreshRequest):
    try:
        refresh = RefreshToken(payload.refresh)
        return TokenRefreshResponse(access=str(refresh.access_token))
    except TokenError:
        raise HttpError(401, 'Token is invalid or expired.')


@router.post(
    '/google-login',
    auth=None,
    operation_id='googleAuth',
    url_name="google_login",
    response={200: GoogleAuthResponse, 400: ErrorResponse},
)
def google_auth(request, payload: GoogleAuthRequest):
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    try:
        info = google_id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError:
        raise HttpError(400, 'Invalid Google token.')

    email = info.get('email')
    if not email or not info.get('email_verified', False):
        raise HttpError(400, 'Google account email is not verified.')

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        base = email.split('@')[0]
        username, suffix = base, 1
        while User.objects.filter(username__iexact=username).exists():
            username = f'{base}{suffix}'
            suffix += 1
        user = User(username=username, email=email, full_name=info.get('name', ''), needs_onboarding=True, is_active=True)
        user.set_unusable_password()
        user.save()
    elif not user.is_active:
        raise HttpError(400, 'This account is inactive.')

    refresh = RefreshToken.for_user(user)
    return GoogleAuthResponse(
        access=str(refresh.access_token),
        refresh=str(refresh),
        user=user,
        onboarding_required=user.needs_onboarding,
    )


# --------------------------------------------------------------------------
# Current user profile
# --------------------------------------------------------------------------

@router.get(
    '/profile',
    auth=JWTAuth(),
    operation_id='getUserProfile',
    url_name="profile",
    response={200: UserResponse, 401: ErrorResponse},
)
def get_user_profile(request):
    return UserResponse.model_validate(request.user, from_attributes=True, context={'request': request})

@router.patch(
    '/profile',
    auth=JWTAuth(),
    operation_id='updateUserProfile',
    url_name="profile",
    response={200: UserResponse, 400: ErrorResponse, 401: ErrorResponse},
)
def update_user_profile(request, payload: UserUpdateRequest):
    user = request.user
    data = payload.model_dump(exclude_unset=True)

    if "role" in data:
        raise HttpError(400, "Role cannot be changed.")

    password = data.pop("password", None)

    if (
        user.needs_onboarding
        and not user.has_usable_password()
        and not password
    ):
        raise HttpError(
            400,
            "Please set a password to complete Google registration."
        )
    

    if password:
        if not (
            user.needs_onboarding
            and not user.has_usable_password()
        ):
            raise HttpError(
                400,
                "Password can only be set during onboarding."
            )

        _check_password_or_400(password, user)

    for field, value in data.items():
        setattr(user, field, value)

    if password:
        user.set_password(password)

    if (
        user.needs_onboarding
        and user.role
        and user.full_name
        and user.phone
        and user.city
        and user.has_usable_password()
    ):
        user.needs_onboarding = False

    update_fields = list(data.keys())

    if password:
        update_fields.append("password")

    if user.needs_onboarding is False:
        update_fields.append("needs_onboarding")

    if update_fields:
        user.save(update_fields=list(set(update_fields)))

    return UserResponse.model_validate(
        user,
        from_attributes=True,
        context={"request": request},
    )


@router.delete(
    '/profile',
    auth=JWTAuth(),
    operation_id='deleteUserProfile',
    url_name="profile",
    response={204: None, 401: ErrorResponse},
)
def delete_user_profile(request):
    request.user.delete()
    return 204, None


@router.patch(
    '/profile/avatar',
    auth=JWTAuth(),
    operation_id='updateUserAvatar',
    url_name="profile_avatar",
    response={200: UserAvatarResponse, 400: ErrorResponse, 401: ErrorResponse},
)
def update_user_avatar(request, avatar: UploadedFile = File(...)):
    if not (avatar.content_type or '').startswith('image/'):
        raise HttpError(400, 'Upload a valid image.')

    user = request.user
    user.avatar = avatar
    user.save(update_fields=['avatar'])
    return UserAvatarResponse.model_validate(user, from_attributes=True, context={'request': request})


@router.delete(
    '/profile/avatar',
    auth=JWTAuth(),
    operation_id='deleteUserAvatar',
    url_name="profile_avatar",
    response={204: None, 401: ErrorResponse},
)
def delete_user_avatar(request):
    user = request.user
    if user.avatar:
        user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
    return 204, None


# --------------------------------------------------------------------------
# Google Calendar
# --------------------------------------------------------------------------

@router.get(
    '/google-calendar/status',
    auth=JWTAuth(),
    operation_id='getGoogleCalendarStatus',
    url_name="google_calendar_status",
    response={200: GoogleCalendarStatusResponse, 401: ErrorResponse},
)
def get_google_calendar_status(request):
    return GoogleCalendarStatusResponse(connected=request.user.google_calendar_connected)


@router.post(
    '/google-calendar/connect',
    auth=JWTAuth(),
    operation_id='connectGoogleCalendar',
    url_name="google_calendar_connect",
    response={200: GoogleCalendarConnectResponse, 401: ErrorResponse, 503: ErrorResponse},
)
def connect_google_calendar(request):
    if not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HttpError(503, 'Google Calendar integration is not configured.')

    code_verifier = _generate_code_verifier()
    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_CALENDAR_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'code_challenge': _generate_code_challenge(code_verifier),
        'code_challenge_method': 'S256',
    }

    request.user.google_calendar_token = {'_code_verifier': code_verifier}
    request.user.save(update_fields=['google_calendar_token'])
    return GoogleCalendarConnectResponse(auth_url=f'{GOOGLE_AUTH_URI}?{urlencode(params)}')


@router.post(
    '/google-calendar/callback',
    auth=JWTAuth(),
    operation_id='callbackGoogleCalendar',
    url_name="google_calendar_callback",
    response={200: GoogleCalendarStatusResponse, 400: ErrorResponse, 401: ErrorResponse, 503: ErrorResponse},
)
def callback_google_calendar(request, payload: GoogleCalendarCallbackRequest):
    try:
        code_verifier = (request.user.google_calendar_token or {}).get('_code_verifier')
        token_response = http_requests.post(
            GOOGLE_TOKEN_URI,
            data={
                'code': payload.code,
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_CALENDAR_REDIRECT_URI,
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier,
            },
        )
        if token_response.status_code != 200:
            error_data = token_response.json()
            message = error_data.get('error_description', error_data.get('error', 'Unknown error'))
            raise HttpError(400, f'Token exchange failed: {message}')

        tokens = token_response.json()
        user = request.user
        user.google_calendar_token = {
            'token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
        }
        user.google_calendar_connected = True
        user.save(update_fields=['google_calendar_token', 'google_calendar_connected'])
        _sync_all_calendar_items(user)
        return GoogleCalendarStatusResponse(connected=True)
    except HttpError:
        raise
    except Exception as exc:
        raise HttpError(400, f'Failed to connect: {exc}') from exc


@router.post(
    '/google-calendar/disconnect',
    auth=JWTAuth(),
    operation_id='disconnectGoogleCalendar',
    url_name="google_calendar_disconnect",
    response={200: GoogleCalendarStatusResponse, 401: ErrorResponse},
)
def disconnect_google_calendar(request):
    user = request.user
    user.google_calendar_token = None
    user.google_calendar_connected = False
    user.save(update_fields=['google_calendar_token', 'google_calendar_connected'])
    return GoogleCalendarStatusResponse(connected=False)


# --------------------------------------------------------------------------
# Users
# --------------------------------------------------------------------------

@router.get(
    '/users',
    auth=JWTAuth(),
    operation_id='listUsers',
    url_name="users",
    response={200: list[TeamUserListResponse], 401: ErrorResponse},
)
def list_users(request, filters: UserListFilters = Query(...)):
    queryset = User.objects.filter(role='team', is_superuser=False).order_by('id')
    search = (filters.search or '').strip()
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(full_name__icontains=search)
        )
    return [
        TeamUserListResponse.model_validate(user, from_attributes=True, context={'request': request})
        for user in queryset
    ]


@router.get(
    '/users/{int:pk}',
    auth=JWTAuth(),
    operation_id='getUser',
    url_name="user_detail",
    response={200: UserResponse, 401: ErrorResponse, 404: ErrorResponse},
)
def get_user(request, pk: int):
    user = get_object_or_404(User.objects.filter(is_active=True, is_superuser=False), pk=pk)
    return UserResponse.model_validate(user, from_attributes=True, context={'request': request})


@router.get(
    '/users/{int:pk}/tournaments-history',
    auth=JWTAuth(),
    operation_id='listUserTournamentHistory',
    url_name="user_tournaments_history",
    response={200: list[UserTournamentHistoryItemResponse], 401: ErrorResponse, 404: ErrorResponse},
)
def list_user_tournament_history(request, pk: int):
    user = get_object_or_404(User.objects.filter(is_active=True, is_superuser=False), pk=pk)

    team_ids = set(TeamMember.objects.filter(user=user).values_list('team_id', flat=True)) | set(
        Team.objects.filter(captain=user).values_list('id', flat=True)
    )
    if not team_ids:
        return []

    registrations = (
        TournamentTeamRegistration.objects.select_related('tournament', 'team')
        .filter(
            team_id__in=team_ids,
            tournament__status=Tournament.STATUS_FINISHED,
        )
        .order_by('-tournament__end_date', '-created_at', '-id')
    )

    by_tournament: dict[int, TournamentTeamRegistration] = {}
    for registration in registrations:
        by_tournament.setdefault(registration.tournament_id, registration)

    if not by_tournament:
        return []

    standings = LeaderboardEntry.objects.filter(
        round__isnull=True,
        tournament_id__in=by_tournament.keys(),
        team_id__in=[registration.team_id for registration in by_tournament.values()],
    ).values('tournament_id', 'team_id', 'rank', 'total_score')
    standings_map = {(e['tournament_id'], e['team_id']): e for e in standings}

    ordered = sorted(
        by_tournament.values(),
        key=lambda reg: (reg.tournament.end_date, reg.tournament.created_at),
        reverse=True,
    )
    context = {'request': request, 'standings': standings_map}
    return [
        UserTournamentHistoryItemResponse.model_validate(reg, from_attributes=True, context=context)
        for reg in ordered
    ]


# --------------------------------------------------------------------------
# Passwords
# --------------------------------------------------------------------------

@router.post(
    "/password-reset",
    auth=None,
    operation_id="requestPasswordReset",
    url_name="password_reset_request",
    response={200: MessageResponse},
)
def request_password_reset(request, payload: PasswordResetRequest):
    user = User.objects.filter(
        email__iexact=payload.email.strip(),
        is_active=True,
    ).first()

    if user:
        _send_link_email(
            user,
            "reset-password",
            "accounts/password_reset_email.html",
            "Password reset",
            "Follow the link to reset your password:",
        )

    return MessageResponse(
        message="Password reset email sent successfully."
    )


@router.get(
    '/password-reset/{uidb64}/{token}',
    auth=None,
    operation_id='validatePasswordResetLink',
    url_name="password_reset_confirm",
    response={200: MessageResponse, 400: ErrorResponse},
)
def validate_password_reset_link(request, uidb64: str, token: str):
    user = _get_user_by_uid(uidb64)
    if user is None or not default_token_generator.check_token(user, token):
        raise HttpError(400, 'Password reset link is invalid or expired.')
    return MessageResponse(message='Password reset link is valid.')


@router.post(
    '/password-reset/{uidb64}/{token}',
    auth=None,
    operation_id='confirmPasswordReset',
    url_name="password_reset_confirm",
    response={200: MessageResponse, 400: ErrorResponse},
)
def confirm_password_reset(request, uidb64: str, token: str, payload: PasswordResetConfirmRequest):
    user = _get_user_by_uid(uidb64)
    if user is None or not default_token_generator.check_token(user, token):
        raise HttpError(400, 'Password reset link is invalid or expired.')

    if payload.new_password != payload.confirm_password:
        raise HttpError(400, 'Passwords do not match.')
    _check_password_or_400(payload.new_password, user)

    user.set_password(payload.new_password)
    user.save(update_fields=['password'])
    return MessageResponse(message='Password has been reset successfully.')


@router.post(
    '/change-password',
    auth=JWTAuth(),
    operation_id='changePassword',
    url_name="change_password",
    response={200: MessageResponse, 400: ErrorResponse, 401: ErrorResponse},
)
def change_password(request, payload: ChangePasswordRequest):
    user = request.user
    if not user.check_password(payload.current_password):
        raise HttpError(400, 'Current password is incorrect.')
    if payload.new_password != payload.confirm_password:
        raise HttpError(400, 'Passwords do not match.')
    _check_password_or_400(payload.new_password, user)

    user.set_password(payload.new_password)
    user.save(update_fields=['password'])
    return MessageResponse(message='Password changed successfully.')


# --------------------------------------------------------------------------
# Role activation codes (admin only)
# --------------------------------------------------------------------------

@router.get(
    '/role-codes',
    auth=JWTAuth(),
    operation_id='listRoleActivationCodes',
    url_name="role_codes_admin",
    response={200: RoleActivationCodeListResponse, 401: ErrorResponse, 403: ErrorResponse},
)
def list_role_activation_codes(request, filters: RoleActivationCodeListFilters = Query(...)):
    _require_admin(request)

    queryset = RoleActivationCode.objects.select_related('created_by', 'used_by').order_by('-created_at')
    role = (filters.role or '').strip()
    if role:
        queryset = queryset.filter(role=role)

    return RoleActivationCodeListResponse(
        codes=[RoleActivationCodeResponse.model_validate(c, from_attributes=True) for c in queryset],
        active_counts=_active_counts(),
    )


@router.post(
    '/role-codes',
    auth=JWTAuth(),
    operation_id='generateRoleActivationCodes',
    url_name="role_codes_admin",
    response={201: RoleActivationCodeGenerateResponse, 400: ErrorResponse, 401: ErrorResponse, 403: ErrorResponse},
)
def generate_role_activation_codes(request, payload: RoleActivationCodeGenerateRequest):
    _require_admin(request)

    with transaction.atomic():
        codes = [
            RoleActivationCode.objects.create(
                code=secrets.token_hex(8).upper(),
                role=payload.role,
                created_by=request.user,
            )
            for _ in range(payload.count)
        ]

    return 201, RoleActivationCodeGenerateResponse(
        created=[RoleActivationCodeResponse.model_validate(c, from_attributes=True) for c in codes],
        active_counts=_active_counts(),
    )
