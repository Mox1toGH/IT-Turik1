import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status, serializers as drf_serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView as _TokenObtainPairView,
    TokenRefreshView as _TokenRefreshView,
)

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer

from backend.openapi import _400, _401, _403, _404

from .models import RoleActivationCode, User
from evaluation.models import LeaderboardEntry
from teams.models import Team, TeamMember
from tournaments.models import Tournament, TournamentTeamRegistration
from .serializers import (
    MessageResponseSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RoleActivationCodeGenerateSerializer,
    RoleActivationCodeSerializer,
    GoogleAuthResponseSerializer,
    GoogleAuthSerializer,
    RegisterSerializer,
    RoleActivationCodeGenerateResponseSerializer,
    RoleActivationCodeListResponseSerializer,
    ActivationResponseSerializer,
    TeamUserListSerializer,
    UserAvatarUpdateSerializer,
    UserSerializer,
    UserTournamentHistoryItemSerializer,
    UserUpdateSerializer,
)


@extend_schema(operation_id='registerUser', responses={
    201: RegisterSerializer,
    400: _400,
})
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@extend_schema(
    operation_id='activateAccount',
    parameters=[
        OpenApiParameter('uidb64', str, OpenApiParameter.PATH, description='Base64-encoded user ID'),
        OpenApiParameter('token', str, OpenApiParameter.PATH, description='Activation token'),
    ],
    responses={
        200: ActivationResponseSerializer,
        400: _400,
    },
)
class ActivationView(APIView):
    permission_classes = (AllowAny,)

    def patch(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response(
                ActivationResponseSerializer({'status': 'success', 'message': 'Account activated!'}).data,
                status=status.HTTP_200_OK,
            )

        raise ValidationError({'message': ['Activation link is invalid or expired.']})


@extend_schema(
    operation_id='googleAuth',
    responses={
        200: GoogleAuthResponseSerializer,
        400: _400,
    },
)
class GoogleAuthView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, refresh = serializer.save()
        return Response(
            GoogleAuthResponseSerializer({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user,
                'onboarding_required': user.needs_onboarding,
            }).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(methods=['GET'], operation_id='getUserProfile', responses={
    200: UserSerializer,
    401: _401,
})
@extend_schema(methods=['PUT'], operation_id='replaceUserProfile', responses={
    200: UserSerializer,
    400: _400,
    401: _401,
})
@extend_schema(methods=['PATCH'], operation_id='updateUserProfile', responses={
    200: UserSerializer,
    400: _400,
    401: _401,
})
@extend_schema(methods=['DELETE'], operation_id='deleteUserProfile', responses={
    204: OpenApiResponse(description='Account deleted successfully.'),
    401: _401,
})
class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

@extend_schema(methods=['PATCH'], operation_id='updateUserAvatar', responses={
    200: UserAvatarUpdateSerializer,
    400: _400,
    401: _401,
})
@extend_schema(methods=['DELETE'], operation_id='deleteUserAvatar', responses={
    204: OpenApiResponse(description='Avatar deleted successfully.'),
    401: _401,
})
class UserAvatarView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserAvatarUpdateSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    operation_id='listUsers',
    parameters=[
        OpenApiParameter('search', str, required=False, description='Filter by username, email, or full name'),
    ],
    responses={
        200: TeamUserListSerializer(many=True),
        401: _401,
    },
)
class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamUserListSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='team', is_superuser=False).order_by('id')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(full_name__icontains=search)
            )
        return queryset


@extend_schema(operation_id='getUser', responses={
    200: UserSerializer,
    401: _401,
    404: _404,
})
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True, is_superuser=False)


@extend_schema(
    operation_id='listUserTournamentHistory',
    responses={
        200: UserTournamentHistoryItemSerializer(many=True),
        401: _401,
        404: _404,
    },
)
class UserTournamentHistoryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTournamentHistoryItemSerializer

    @staticmethod
    def _team_registration_status(registration: TournamentTeamRegistration) -> str:
        if registration.is_disqualified:
            return 'disqualified'
        if registration.is_active:
            return 'active'
        return 'inactive'

    def get(self, request, pk):
        user = get_object_or_404(User.objects.filter(is_active=True, is_superuser=False), pk=pk)

        team_ids = set(TeamMember.objects.filter(user=user).values_list('team_id', flat=True)) | set(
            Team.objects.filter(captain=user).values_list('id', flat=True)
        )
        if not team_ids:
            return Response([], status=status.HTTP_200_OK)

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
            if registration.tournament_id not in by_tournament:
                by_tournament[registration.tournament_id] = registration

        if not by_tournament:
            return Response([], status=status.HTTP_200_OK)

        standings = (
            LeaderboardEntry.objects.filter(
                round__isnull=True,
                tournament_id__in=by_tournament.keys(),
                team_id__in=[registration.team_id for registration in by_tournament.values()],
            )
            .values('tournament_id', 'team_id', 'rank', 'total_score')
        )
        standings_map = {
            (entry['tournament_id'], entry['team_id']): entry
            for entry in standings
        }

        payload = []
        for registration in sorted(
            by_tournament.values(),
            key=lambda reg: (reg.tournament.end_date, reg.tournament.created_at),
            reverse=True,
        ):
            standing = standings_map.get((registration.tournament_id, registration.team_id))
            payload.append({
                'tournament_id': registration.tournament.id,
                'tournament_name': registration.tournament.name,
                'tournament_status': registration.tournament.status,
                'start_date': registration.tournament.start_date,
                'end_date': registration.tournament.end_date,
                'team': {
                    'id': registration.team.id,
                    'name': registration.team.name,
                },
                'team_registration_status': self._team_registration_status(registration),
                'final_rank': standing['rank'] if standing else None,
                'final_score': standing['total_score'] if standing else None,
            })

        return Response(
            UserTournamentHistoryItemSerializer(payload, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='requestPasswordReset',
    request=PasswordResetRequestSerializer,
    responses={
        200: MessageResponseSerializer,
        400: _400,
    },
)
class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            MessageResponseSerializer({'message': 'Password reset email sent successfully.'}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(methods=['GET'], operation_id='validatePasswordResetLink',
    parameters=[
        OpenApiParameter('uidb64', str, OpenApiParameter.PATH),
        OpenApiParameter('token', str, OpenApiParameter.PATH),
    ],
    responses={200: MessageResponseSerializer, 400: _400},
)
@extend_schema(methods=['POST'], operation_id='confirmPasswordReset',
    parameters=[
        OpenApiParameter('uidb64', str, OpenApiParameter.PATH),
        OpenApiParameter('token', str, OpenApiParameter.PATH),
    ],
    request=PasswordResetConfirmSerializer,
    responses={200: MessageResponseSerializer, 400: _400},
)
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    @staticmethod
    def _get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            raise ValidationError({'message': ['Password reset link is invalid or expired.']})
        return Response(
            MessageResponseSerializer({'message': 'Password reset link is valid.'}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            raise ValidationError({'message': ['Password reset link is invalid or expired.']})

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            MessageResponseSerializer({'message': 'Password has been reset successfully.'}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    operation_id='changePassword',
    request=ChangePasswordSerializer,
    responses={
        200: MessageResponseSerializer,
        400: _400,
        401: _401,
    },
)
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            MessageResponseSerializer({'message': 'Password changed successfully.'}).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(methods=['GET'], operation_id='listRoleActivationCodes',
    parameters=[
        OpenApiParameter('role', str, required=False, description='Filter by role: jury, organizer, admin'),
    ],
    responses={
        200: RoleActivationCodeListResponseSerializer,
        401: _401,
        403: _403,
    },
)
@extend_schema(methods=['POST'], operation_id='generateRoleActivationCodes', request=RoleActivationCodeGenerateSerializer, responses={
    201: RoleActivationCodeGenerateResponseSerializer,
    400: _400,
    401: _401,
    403: _403,
})
class RoleActivationCodeAdminView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleActivationCodeGenerateSerializer
        return RoleActivationCodeSerializer

    @staticmethod
    def _is_platform_admin(user):
        return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))

    def _deny_if_not_admin(self, request):
        if not self._is_platform_admin(request.user):
            raise PermissionDenied('Admin access required.')
        return None

    @staticmethod
    def _active_counts():
        roles = ('jury', 'organizer', 'admin')
        return {
            role: RoleActivationCode.objects.filter(role=role, is_used=False).count()
            for role in roles
        }

    def get(self, request):
        denied = self._deny_if_not_admin(request)
        if denied:
            return denied

        role = request.query_params.get('role', '').strip()
        queryset = RoleActivationCode.objects.select_related('created_by', 'used_by').order_by('-created_at')
        if role:
            queryset = queryset.filter(role=role)

        return Response(
            RoleActivationCodeListResponseSerializer({
                'codes': queryset,
                'active_counts': self._active_counts(),
            }).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        denied = self._deny_if_not_admin(request)
        if denied:
            return denied

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        codes = serializer.save()
        return Response(
            RoleActivationCodeGenerateResponseSerializer({
                'created': codes,
                'active_counts': self._active_counts(),
            }).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    operation_id='login',
    request=inline_serializer('LoginRequest', fields={
        'username': drf_serializers.CharField(),
        'password': drf_serializers.CharField(),
    }),
    responses={
        200: inline_serializer('LoginResponse', fields={
            'access': drf_serializers.CharField(),
            'refresh': drf_serializers.CharField(),
        }),
        400: _400,
        401: _401,
    },
)
class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return _TokenObtainPairView.as_view()(request._request, *args, **kwargs)


@extend_schema(
    operation_id='refreshToken',
    request=inline_serializer('TokenRefreshRequest', fields={
        'refresh': drf_serializers.CharField(),
    }),
    responses={
        200: inline_serializer('TokenRefreshResponse', fields={
            'access': drf_serializers.CharField(),
        }),
        400: _400,
        401: _401,
    },
)
class TokenRefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return _TokenRefreshView.as_view()(request._request, *args, **kwargs)
