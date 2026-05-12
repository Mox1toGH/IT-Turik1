import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import  PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from backend.openapi import _400, _401, _403, _404

from .models import RoleActivationCode, User
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
    UserSerializer,
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


@extend_schema(methods=['GET'], operation_id='validatePasswordResetLink', responses={
    200: MessageResponseSerializer,
    400: _400,
})
@extend_schema(methods=['POST'], operation_id='confirmPasswordReset', request=PasswordResetConfirmSerializer, responses={
    200: MessageResponseSerializer,
    400: _400,
})
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