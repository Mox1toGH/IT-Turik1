import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import generics, status
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RoleActivationCode, User
from .serializers import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RoleActivationCodeGenerateSerializer,
    RoleActivationCodeSerializer,
    RegisterSerializer,
    TeamUserListSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ActivationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response({'status': 'success', 'message': 'Account activated!'}, status=status.HTTP_200_OK)

        raise ValidationError({'message': ['Activation link is invalid or expired.']})


class GoogleAuthView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def _generate_unique_username(email):
        base = re.sub(r'[^a-zA-Z0-9_]', '', email.split('@')[0]) or 'user'
        base = base[:140]
        username = base
        index = 1

        while User.objects.filter(username=username).exists():
            suffix = str(index)
            username = f"{base[:150 - len(suffix)]}{suffix}"
            index += 1

        return username

    def post(self, request):
        raw_id_token = request.data.get('id_token') or request.data.get('credential')
        if not raw_id_token:
            raise ValidationError({'id_token': ['id_token is required.']})

        if not settings.GOOGLE_OAUTH_CLIENT_ID:
            raise APIException('Google auth is not configured.')

        try:
            payload = id_token.verify_oauth2_token(
                raw_id_token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError:
            raise ValidationError({'id_token': ['Invalid Google token.']}) from None

        issuer = payload.get('iss')
        if issuer not in {'accounts.google.com', 'https://accounts.google.com'}:
            raise ValidationError({'id_token': ['Invalid token issuer.']})

        if not payload.get('email_verified'):
            raise ValidationError({'id_token': ['Google email is not verified.']})

        email = payload.get('email')
        if not email:
            raise ValidationError({'id_token': ['Google account email is missing.']})

        full_name = payload.get('name', '')

        user = User.objects.filter(email=email).first()
        if user is None:
            username = self._generate_unique_username(email)
            user = User.objects.create(
                username=username,
                email=email,
                full_name=full_name,
                is_active=True,
                needs_onboarding=True,
            )
            user.set_unusable_password()
            user.save()
        else:
            updated_fields = []
            if not user.is_active:
                user.is_active = True
                updated_fields.append('is_active')
            if full_name and not user.full_name:
                user.full_name = full_name
                updated_fields.append('full_name')
            if updated_fields:
                user.save(update_fields=updated_fields)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
                'onboarding_required': user.needs_onboarding,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


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


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True, is_superuser=False)


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password reset email sent successfully.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

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
        return Response({'message': 'Password reset link is valid.'}, status=status.HTTP_200_OK)

    def post(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            raise ValidationError({'message': ['Password reset link is invalid or expired.']})

        serializer = PasswordResetConfirmSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class RoleActivationCodeAdminView(APIView):
    permission_classes = [IsAuthenticated]

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

        serializer = RoleActivationCodeSerializer(queryset, many=True)
        return Response(
            {
                'codes': serializer.data,
                'active_counts': self._active_counts(),
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        denied = self._deny_if_not_admin(request)
        if denied:
            return denied

        serializer = RoleActivationCodeGenerateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        codes = serializer.save()
        return Response(
            {
                'created': RoleActivationCodeSerializer(codes, many=True).data,
                'active_counts': self._active_counts(),
            },
            status=status.HTTP_201_CREATED,
        )
